import os
import cv2
import numpy as np
from Crypto.Random import get_random_bytes

# --- 1. Import all functions from your other files ---
try:
    from dwt_watermark import embed_dwt, extract_dwt
    from aes_gcm_cipher import encrypt_aes_gcm, decrypt_aes_gcm
    from chaos_cipher import encrypt_decrypt_chaos
except ImportError:
    print("FATAL ERROR: Could not find your other .py files.")
    print("Please make sure 'dwt_watermark.py', 'aes_gcm_cipher.py', and 'chaos_cipher.py' are in the same folder.")
    exit()

def main():
    print("="*60)
    print("### Secure Image Transmission (Full Pipeline + Attacks) ###")
    print("="*60)

    # --- 2. Get User Input ---
    FILE_HOST = input("Enter the filename of your HOST image (e.g., Original_image.png): ")
    FILE_WATERMARK = input("Enter the filename of your WATERMARK image (e.g., watermark_logo.png): ")

    # --- 3. Validate Input ---
    if not os.path.exists(FILE_HOST):
        print(f"\nError: Host file not found: '{FILE_HOST}'")
        return
    if not os.path.exists(FILE_WATERMARK):
        print(f"\nError: Watermark file not found: '{FILE_WATERMARK}'")
        return
        
    base_name = os.path.splitext(FILE_HOST)[0]

    # --- 4. Configuration ---
    # We use 25.0 so the watermark is strong enough to survive attacks
    DWT_ALPHA = 25.0 
    AES_KEY = get_random_bytes(32)

    # --- 5. Output Filenames ---
    FILE_WATERMARKED = f"{base_name}_watermarked.png"
    
    # AES Files
    FILE_AES_ENCRYPTED = f"{base_name}_aes.bin"
    FILE_AES_DECRYPTED = f"{base_name}_aes_decrypted.png"

    # Extraction Files
    FILE_EXTRACT_WATERMARK = f"{base_name}_watermark_from_decrypted.png"

    print(f"\n[INFO] Using Strength (Alpha): {DWT_ALPHA}")
    
    # === STEP 1: EMBED WATERMARK ===
    print("\n" + "-"*50)
    print("STEP 1: Embedding DWT watermark...")
    embed_dwt(FILE_HOST, FILE_WATERMARK, FILE_WATERMARKED, alpha=DWT_ALPHA)

    # === STEP 2: SECURE TRANSMISSION (AES-GCM) ===
    print("\n" + "-"*50)
    print("STEP 2: Transmitting via AES-GCM (Encryption & Decryption)...")
    
    # Encrypt
    print(f"Encrypting '{FILE_WATERMARKED}'...")
    encrypt_aes_gcm(FILE_WATERMARKED, FILE_AES_ENCRYPTED, AES_KEY)
    
    # Decrypt
    print(f"Decrypting '{FILE_AES_ENCRYPTED}'...")
    success = decrypt_aes_gcm(FILE_AES_ENCRYPTED, FILE_AES_DECRYPTED, AES_KEY)
    
    if not success:
        print("Decryption failed. Stopping.")
        return
    
    # 4. EXTRACT (From the DECRYPTED image)
    print(f"[4] Extracting Watermark from {FILE_AES_DECRYPTED}...")
    extract_dwt(FILE_HOST, FILE_AES_DECRYPTED, FILE_EXTRACT_WATERMARK, alpha=DWT_ALPHA)
    print("\n" + "-"*60)

if __name__ == "__main__":
    main()