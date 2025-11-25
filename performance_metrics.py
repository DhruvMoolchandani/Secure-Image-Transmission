import cv2
import numpy as np
import os
import time
from math import log10, sqrt
from scipy.stats import entropy
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# --- CONFIGURATION ---
FILE_ORIGINAL = "Original_image.png"
FILE_WATERMARKED = "Original_image_watermarked.png" # From run_full_project.py
FILE_ENCRYPTED = "Original_image_aes.bin"        # From run_full_project.py

def calculate_psnr(img1, img2):
    """Calculates Peak Signal-to-Noise Ratio (Quality)."""
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0: return 100
    pixel_max = 255.0
    return 20 * log10(pixel_max / sqrt(mse))

def calculate_entropy(data_bytes):
    """Calculates Shannon Entropy (Randomness). Ideal = 8.0"""
    # Convert bytes to a list of integers (0-255)
    if isinstance(data_bytes, bytes):
        data = np.frombuffer(data_bytes, dtype=np.uint8)
    else:
        data = data_bytes.flatten()
        
    # Calculate counts of each value
    value, counts = np.unique(data, return_counts=True)
    # Normalize counts to get probabilities
    probs = counts / len(data)
    # Calculate entropy
    ent = entropy(probs, base=2)
    return ent

def calculate_correlation(image):
    """Calculates correlation between adjacent pixels. Ideal Encrypted = 0"""
    # Use grayscale for calculation
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    flat = image.flatten()
    # Correlation of pixel i with pixel i+1
    x = flat[:-1]
    y = flat[1:]
    
    return np.corrcoef(x, y)[0, 1]

def measure_speed():
    """Measures AES-GCM Speed."""
    img = cv2.imread(FILE_WATERMARKED)
    data = img.tobytes()
    key = get_random_bytes(32)
    
    # Measure Encryption
    start_enc = time.time()
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    end_enc = time.time()
    
    # Measure Decryption
    start_dec = time.time()
    cipher_dec = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
    _ = cipher_dec.decrypt_and_verify(ciphertext, tag)
    end_dec = time.time()
    
    return (end_enc - start_enc), (end_dec - start_dec)

def main():
    print("="*60)
    print("### FINAL PERFORMANCE EVALUATION ###")
    print("="*60)

    # 1. Load Images
    if not os.path.exists(FILE_ORIGINAL) or not os.path.exists(FILE_WATERMARKED):
        print("Error: Run 'run_full_project.py' first to generate images.")
        exit()
        
    img_orig = cv2.imread(FILE_ORIGINAL)
    img_water = cv2.imread(FILE_WATERMARKED)
    
    # --- METRIC 1: IMPERCEPTIBILITY (PSNR) ---
    print("\n[1] Visual Quality (Imperceptibility)")
    psnr_val = calculate_psnr(img_orig, img_water)
    print(f"   -> PSNR (Original vs Watermarked): {psnr_val:.2f} dB")
    if psnr_val > 30: print("      (Status: Good Quality)")
    else: print("      (Status: Visible Degradation - Expected for Robustness)")

    # --- METRIC 2: CRYPTOGRAPHIC STRENGTH ---
    print("\n[2] Security Analysis")
    
    # Entropy
    entropy_orig = calculate_entropy(img_orig)
    
    # Generate fresh encryption for accurate entropy calculation on raw bytes
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, _ = cipher.encrypt_and_digest(img_water.tobytes())
    
    entropy_enc = calculate_entropy(ciphertext)
    
    print(f"   -> Entropy (Original Image):  {entropy_orig:.4f}")
    print(f"   -> Entropy (Encrypted Data):  {entropy_enc:.4f} (Target: ~8.0)")
    
    # Correlation
    corr_orig = calculate_correlation(img_orig)
    # We can't calculate pixel correlation on bytes, but we know it's 0 for AES
    # We can verify this by interpreting bytes as image
    # padding to match shape
    flat_cipher = np.frombuffer(ciphertext, dtype=np.uint8)
    # Take a chunk to calculate correlation
    x = flat_cipher[:-1]
    y = flat_cipher[1:]
    corr_enc = np.corrcoef(x, y)[0, 1]

    print(f"   -> Correlation (Original):    {corr_orig:.4f} (High is expected)")
    print(f"   -> Correlation (Encrypted):   {corr_enc:.4f} (Close to 0 is ideal)")

    # --- METRIC 3: EFFICIENCY ---
    print("\n[3] Computational Efficiency")
    enc_time, dec_time = measure_speed()
    print(f"   -> Encryption Time: {enc_time:.6f} seconds")
    print(f"   -> Decryption Time: {dec_time:.6f} seconds")
    print(f"   -> Total Throughput: {(len(ciphertext)/1024/1024) / (enc_time + dec_time):.2f} MB/s")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()