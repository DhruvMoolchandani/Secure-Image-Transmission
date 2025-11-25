import os
import cv2
import numpy as np
import random
from Crypto.Random import get_random_bytes

# Import all functions from your existing files
# Make sure they are in the same directory!
try:
    from dwt_watermark import embed_dwt, extract_dwt
    from aes_gcm_cipher import encrypt_aes_gcm, decrypt_aes_gcm
    from chaos_cipher import encrypt_decrypt_chaos
except ImportError:
    print("FATAL ERROR: Make sure 'dwt_watermark.py', 'aes_gcm_cipher.py', and 'chaos_cipher.py' are in the same folder.")
    exit()

# --- THE ATTACK FUNCTION ---
def perform_bit_flip_attack(file_path, num_bits_to_flip):
    """
    Reads a file, flips a specified number of random bits, 
    and saves the corrupted file back to the same path.
    """
    print(f"\n[ATTACK] Attacking '{file_path}' by flipping {num_bits_to_flip} bits...")
    
    try:
        # Read the file as raw bytes
        with open(file_path, 'rb') as f:
            data = f.read()
            
        # Convert to a mutable bytearray to allow changes
        data_corrupted = bytearray(data)
        num_bytes = len(data_corrupted)
        
        if num_bytes == 0:
            print("[ATTACK] Error: File is empty.")
            return

        # Flip the specified number of random bits
        for _ in range(num_bits_to_flip):
            # Pick a random byte
            byte_index = random.randint(0, num_bytes - 1)
            # Pick a random bit within that byte (0-7)
            bit_index = random.randint(0, 7)
            
            # Create a bitmask (e.g., 00010000)
            bit_mask = 1 << bit_index
            
            # Flip the bit using XOR
            data_corrupted[byte_index] = data_corrupted[byte_index] ^ bit_mask
            
        # Write the corrupted data back to the file
        with open(file_path, 'wb') as f:
            f.write(data_corrupted)
            
        print(f"[ATTACK] Attack complete. File '{file_path}' is now corrupted.")

    except Exception as e:
        print(f"[ATTACK] Error during attack: {e}")


# --- MAIN TEST SCRIPT ---
if __name__ == "__main__":
    
    # --- 0. SETUP: Create the files we need ---
    print("="*60)
    print("### STEP 0: SETTING UP THE ENVIRONMENT ###")
    
    # Create dummy images if they don't exist
    if not os.path.exists("cover.png"):
        cv2.imwrite("cover.png", np.random.randint(0, 256, (512, 512), dtype=np.uint8))
    if not os.path.exists("watermark_logo.png"):
        cv2.imwrite("watermark_logo.png", np.random.randint(0, 256, (64, 64), dtype=np.uint8))

    # Define file names
    FILE_HOST = "cover.png"
    FILE_WATERMARK = "watermark_logo.png"
    FILE_WATERMARKED = "watermarked_image.png"
    
    # AES files
    FILE_AES_ENCRYPTED = "encrypted_image.bin"
    FILE_AES_DECRYPTED = "decrypted_attacked_aes.png"
    AES_KEY = get_random_bytes(32)
    
    # Chaos files
    FILE_CHAOS_ENCRYPTED = "encrypted_image_chaos.png"
    FILE_CHAOS_DECRYPTED = "decrypted_attacked_chaos.png"
    CHAOS_KEY_X0 = 0.42
    CHAOS_KEY_MU = 3.99

    # 1. Create a clean watermarked image
    embed_dwt(FILE_HOST, FILE_WATERMARK, FILE_WATERMARKED, alpha=0.1)
    
    # 2. Create a clean encrypted AES file
    encrypt_aes_gcm(FILE_WATERMARKED, FILE_AES_ENCRYPTED, AES_KEY)
    
    # 3. Create a clean encrypted Chaos file
    encrypt_decrypt_chaos(FILE_WATERMARKED, FILE_CHAOS_ENCRYPTED, CHAOS_KEY_X0, CHAOS_KEY_MU)
    print("Setup complete. Clean encrypted files have been created.")
    
    
    # --- 1. TEST AES-GCM INTEGRITY ---
    print("\n" + "="*60)
    print("### STEP 1: ATTACKING AES-GCM CIPHERTEXT ###")
    
    # Attack the encrypted file
    perform_bit_flip_attack(FILE_AES_ENCRYPTED, num_bits_to_flip=10)
    
    # Attempt to decrypt the corrupted file
    print(f"\n[DECRYPT] Attempting to decrypt '{FILE_AES_ENCRYPTED}'...")
    success = decrypt_aes_gcm(FILE_AES_ENCRYPTED, FILE_AES_DECRYPTED, AES_KEY)
    
    if not success:
        print("\n[RESULT] AES-GCM test PASSED.")
        print("The system correctly detected the tampered file and refused to decrypt it.")
    else:
        print("\n[RESULT] AES-GCM test FAILED. This should not happen.")


    # --- 2. TEST CHAOS CIPHER INTEGRITY ---
    print("\n" + "="*60)
    print("### STEP 2: ATTACKING CHAOS CIPHERTEXT ###")
    
    # Attack the encrypted image
    perform_bit_flip_attack(FILE_CHAOS_ENCRYPTED, num_bits_to_flip=10)
    
    # Attempt to decrypt the corrupted file
    print(f"\n[DECRYPT] Attempting to decrypt '{FILE_CHAOS_ENCRYPTED}'...")
    try:
        encrypt_decrypt_chaos(FILE_CHAOS_ENCRYPTED, FILE_CHAOS_DECRYPTED, CHAOS_KEY_X0, CHAOS_KEY_MU)
        print(f"\n[RESULT] Chaos cipher 'succeeded' in decrypting.")
        print(f"File saved to '{FILE_CHAOS_DECRYPTED}'.")
        print("This is a VULNERABILITY. The decrypted image will be corrupted.")

        # --- 3. (Optional) Prove the corruption ---
        print("\n[VERIFY] Trying to extract watermark from corrupted chaos image...")
        extract_dwt(FILE_HOST, FILE_CHAOS_DECRYPTED, "corrupted_watermark.png", alpha=0.1)
        print("Check 'corrupted_watermark.png'. It will be garbled,")
        print("proving the decryption passed on bad data.")

    except Exception as e:
        print(f"\n[RESULT] Chaos cipher failed unexpectedly: {e}")

    print("\n" + "="*60)
    print("### ATTACK TEST COMPLETE ###")