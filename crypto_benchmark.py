import time
import os
import cv2
import numpy as np
from Crypto.Cipher import AES, ChaCha20
from Crypto.Random import get_random_bytes

# --- CONFIGURATION ---
FILE_TO_TEST = "Original_image_watermarked.png" 

def create_error_image(shape, message):
    img = np.zeros(shape, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(message, font, 1, 2)[0]
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = (img.shape[0] + text_size[1]) // 2
    cv2.putText(img, message, (text_x, text_y), font, 1, (0, 0, 255), 2)
    return img

def load_image_data():
    if not os.path.exists(FILE_TO_TEST):
        print(f"FATAL: Could not find '{FILE_TO_TEST}'.")
        print("Please run 'run_full_project.py' first.")
        exit()
    img = cv2.imread(FILE_TO_TEST)
    return img.tobytes(), img.shape

# Load data once
sample_data, image_shape = load_image_data()
print(f"Loaded {FILE_TO_TEST} | Size: {len(sample_data)} bytes")

def apply_attack(ciphertext_bytes):
    """Simulates a Man-in-the-Middle attack by flipping bits."""
    ba = bytearray(ciphertext_bytes)
    idx = len(ba) // 2
    ba[idx] = ba[idx] ^ 0xFF 
    ba[idx+1] = ba[idx+1] ^ 0xFF 
    ba[idx+50] = ba[idx+50] ^ 0xFF 
    return bytes(ba)

def save_result_image(filename, data_bytes, shape):
    try:
        # Handle padding if size mismatch occurs
        expected_len = np.prod(shape)
        if len(data_bytes) != expected_len:
            if len(data_bytes) < expected_len:
                data_bytes += b'\x00' * (expected_len - len(data_bytes))
            else:
                data_bytes = data_bytes[:expected_len]
            
        arr = np.frombuffer(data_bytes, dtype=np.uint8)
        img = arr.reshape(shape)
        cv2.imwrite(filename, img)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

# ==========================================================
# 1. AES-GCM (Secure)
# ==========================================================
def test_aes_gcm():
    print(f"\n[1] Testing AES-GCM...", end=" ")
    key = get_random_bytes(32)
    
    # Encrypt
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(sample_data)
    
    # Save Ciphertext (Proof of Encryption)
    save_result_image("ENC_AES_GCM_Ciphertext.png", ciphertext, image_shape)
    
    # Attack & Decrypt
    corrupted_ciphertext = apply_attack(ciphertext)
    try:
        cipher_verify = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
        cipher_verify.decrypt_and_verify(corrupted_ciphertext, tag)
        
        print("FAILED (Unsafe)")
        save_result_image("DEMO_AES_GCM_AttackResult.png", ciphertext, image_shape)
    except ValueError:
        print("PASSED (Attack Detected!)")
        error_img = create_error_image(image_shape, "AES-GCM: INTEGRITY CHECK FAILED")
        cv2.imwrite("DEMO_AES_GCM_AttackResult.png", error_img)

# ==========================================================
# 2. CHAOS CIPHER (Insecure Integrity)
# ==========================================================
def test_chaos_cipher():
    print(f"\n[2] Testing Chaos-Based Cipher...", end=" ")
    
    np.random.seed(42) 
    keystream = np.random.randint(0, 256, len(sample_data), dtype=np.uint8)
    np_data = np.frombuffer(sample_data, dtype=np.uint8)
    
    # Encrypt
    encrypted = np.bitwise_xor(np_data, keystream)
    save_result_image("ENC_Chaos_Ciphertext.png", encrypted.tobytes(), image_shape)
    
    # Attack & Decrypt
    corrupted_bytes = apply_attack(encrypted.tobytes())
    np_corrupted = np.frombuffer(corrupted_bytes, dtype=np.uint8)
    decrypted = np.bitwise_xor(np_corrupted, keystream)
    
    print("FAILED (Accepted corrupt data)")
    save_result_image("DEMO_Chaos_CorruptedDecrypted.png", decrypted.tobytes(), image_shape)

# ==========================================================
# 3. CHACHA20 (Insecure Integrity)
# ==========================================================
def test_chacha20():
    print(f"\n[3] Testing ChaCha20...", end=" ")
    key = get_random_bytes(32)
    nonce = get_random_bytes(12)
    
    cipher = ChaCha20.new(key=key, nonce=nonce)
    ciphertext = cipher.encrypt(sample_data)
    save_result_image("ENC_ChaCha20_Ciphertext.png", ciphertext, image_shape)
    
    corrupted_ciphertext = apply_attack(ciphertext)
    cipher_dec = ChaCha20.new(key=key, nonce=nonce)
    decrypted = cipher_dec.decrypt(corrupted_ciphertext)
    
    print("FAILED (Accepted corrupt data)")
    save_result_image("DEMO_ChaCha20_CorruptedDecrypted.png", decrypted, image_shape)

# ==========================================================
# 4. VSS (Insecure Integrity)
# ==========================================================
def test_vss():
    print(f"\n[4] Testing VSS...", end=" ")
    
    share1 = os.urandom(len(sample_data))
    save_result_image("ENC_VSS_Share1_Ciphertext.png", share1, image_shape)
    
    np_data = np.frombuffer(sample_data, dtype=np.uint8)
    np_share1 = np.frombuffer(share1, dtype=np.uint8)
    np_share2 = np.bitwise_xor(np_data, np_share1)
    
    # Attack Share 2
    share2_bytes = np_share2.tobytes()
    corrupted_share2 = apply_attack(share2_bytes)
    np_corrupted_share2 = np.frombuffer(corrupted_share2, dtype=np.uint8)
    
    decrypted = np.bitwise_xor(np_share1, np_corrupted_share2)
    
    print("FAILED (Accepted corrupt data)")
    save_result_image("DEMO_VSS_CorruptedDecrypted.png", decrypted.tobytes(), image_shape)

# ==========================================================
# 5. DRPE (Insecure Integrity)
# ==========================================================
def test_drpe():
    print(f"\n[5] Testing DRPE...", end=" ")
    
    arr = np.frombuffer(sample_data, dtype=np.uint8)
    spectrum = np.fft.fft(arr)
    
    # Save Spectrum visualization
    display_spectrum = (np.abs(spectrum) / np.max(np.abs(spectrum)) * 255).astype(np.uint8)
    save_result_image("ENC_DRPE_Ciphertext.png", display_spectrum.tobytes(), image_shape)
    
    # Attack
    idx = len(spectrum)//2
    spectrum[idx] += 5000 
    spectrum[idx+1] += 5000
    
    decrypted = np.fft.ifft(spectrum)
    decrypted_bytes = np.abs(decrypted).astype(np.uint8).tobytes()
    
    print("FAILED (Accepted corrupt data)")
    save_result_image("DEMO_DRPE_CorruptedDecrypted.png", decrypted_bytes, image_shape)

# --- RUN ALL TESTS ---
if __name__ == "__main__":
    print("\n" + "="*60)
    print("--- COMPARATIVE ANALYSIS ---")
    print("="*60)
    
    test_aes_gcm()       
    test_chaos_cipher()  
    test_chacha20()      
    test_vss()           
    test_drpe()          

    print("\n" + "="*60)
    print("DONE! Check your folder.")