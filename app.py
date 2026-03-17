import os
import time
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from Crypto.Random import get_random_bytes

# Import existing modules
from dwt_watermark import embed_dwt, extract_dwt
from aes_gcm_cipher import encrypt_aes_gcm, decrypt_aes_gcm
from chaos_cipher import encrypt_decrypt_chaos

app = Flask(__name__)

# Configure upload and result folders
# In Vercel serverless environment, only /tmp is writable
if os.environ.get('VERCEL') == '1':
    UPLOAD_FOLDER = '/tmp/uploads'
    RESULT_FOLDER = '/tmp/results'
else:
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    RESULT_FOLDER = os.path.join(app.root_path, 'static', 'results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max

def clear_directory(folder_path):
    """Utility to prevent file buildup in temp directories."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def get_base64_img(file_path):
    """Read a file and convert it to a base64 string for direct browser rendering."""
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_pipeline():
    try:
        # Clear out previous files to avoid clutter
        clear_directory(UPLOAD_FOLDER)
        clear_directory(RESULT_FOLDER)
        
        if 'host_image' not in request.files or 'watermark_image' not in request.files:
            return jsonify({'error': 'Missing host or watermark image'}), 400
            
        host_file = request.files['host_image']
        watermark_file = request.files['watermark_image']
        alpha = float(request.form.get('alpha', 25.0))
        
        if host_file.filename == '' or watermark_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        host_filename = secure_filename(host_file.filename)
        watermark_filename = secure_filename(watermark_file.filename)
        
        # We append a timestamp to ensure fresh URLs for the browser cache
        ts = str(int(time.time()))
        
        host_path = os.path.join(app.config['UPLOAD_FOLDER'], f"host_{ts}_{host_filename}")
        watermark_path = os.path.join(app.config['UPLOAD_FOLDER'], f"wm_{ts}_{watermark_filename}")
        
        host_file.save(host_path)
        watermark_file.save(watermark_path)
        
        # Result paths
        watermarked_name = f"watermarked_{ts}.png"
        encrypted_name = f"aes_{ts}.bin"
        decrypted_name = f"decrypted_{ts}.png"
        extracted_name = f"extracted_{ts}.png"
        
        watermarked_path = os.path.join(app.config['RESULT_FOLDER'], watermarked_name)
        encrypted_path = os.path.join(app.config['RESULT_FOLDER'], encrypted_name)
        decrypted_path = os.path.join(app.config['RESULT_FOLDER'], decrypted_name)
        extracted_path = os.path.join(app.config['RESULT_FOLDER'], extracted_name)
        
        # STEP 1: Embed Watermark
        embed_dwt(host_path, watermark_path, watermarked_path, alpha=alpha)
        if not os.path.exists(watermarked_path):
            return jsonify({'error': 'Failed to embed watermark'}), 500
            
        # STEP 2: AES-GCM Encrypt & Decrypt
        AES_KEY = get_random_bytes(32)
        encrypt_aes_gcm(watermarked_path, encrypted_path, AES_KEY)
        
        success = decrypt_aes_gcm(encrypted_path, decrypted_path, AES_KEY)
        if not success or not os.path.exists(decrypted_path):
            return jsonify({'error': 'Decryption failed (File tampering suspected)'}), 500
            
        # STEP 3: Extract Watermark
        extract_dwt(host_path, decrypted_path, extracted_path, alpha=alpha)
        if not os.path.exists(extracted_path):
            return jsonify({'error': 'Failed to extract watermark'}), 500
            
        # Return base64 images directly to avoid Vercel Serverless /tmp loss
        return jsonify({
            'success': True,
            'watermarked_url': get_base64_img(watermarked_path),
            'decrypted_url': get_base64_img(decrypted_path),
            'extracted_url': get_base64_img(extracted_path),
            'host_url': get_base64_img(host_path),
            'watermark_url': get_base64_img(watermark_path)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
