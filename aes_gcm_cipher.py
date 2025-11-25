from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

def encrypt_aes_gcm(input_file_path, output_file_path, key):
    """
    Encrypts a file using AES-GCM and saves it.

    Args:
        input_file_path (str): Path to the file to encrypt.
        output_file_path (str): Path to save the encrypted file.
        key (bytes): A 32-byte (256-bit) AES key.
    """
    try:
        # --- 1. Read Data ---
        with open(input_file_path, 'rb') as f:
            plaintext = f.read()

        # --- 2. Encrypt ---
        # Create a new AES cipher object in GCM mode
        cipher = AES.new(key, AES.MODE_GCM)
        
        # Encrypt the data and get the ciphertext and authentication tag
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        # --- 3. Save to File ---
        # We must save the nonce, tag, and ciphertext
        with open(output_file_path, 'wb') as f:
            f.write(cipher.nonce)  # 16 bytes
            f.write(tag)           # 16 bytes
            f.write(ciphertext)
            
        print(f"File encrypted and saved to {output_file_path}")

    except Exception as e:
        print(f"Error during AES-GCM encryption: {e}")

def decrypt_aes_gcm(input_file_path, output_file_path, key):
    """
    Decrypts a file using AES-GCM and verifies its integrity.

    Args:
        input_file_path (str): Path to the encrypted file.
        output_file_path (str): Path to save the decrypted file.
        key (bytes): The *same* 32-byte key used for encryption.
    """
    try:
        # --- 1. Read Encrypted Data ---
        with open(input_file_path, 'rb') as f:
            # Read the components in the order they were saved
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read() # Read the rest of the file

        # --- 2. Decrypt & Verify ---
        # Create a new AES cipher object with the *same key and nonce*
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # ** This is the critical step! **
        # It decrypts the data *and* checks the tag for integrity.
        # If the tag is wrong (data tampered), it raises a ValueError.
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        # --- 3. Save Decrypted File ---
        with open(output_file_path, 'wb') as f:
            f.write(plaintext)
            
        print(f"Success! File decrypted and saved to {output_file_path}")
        return True

    except ValueError:
        # This block executes if the authentication (tag) check fails
        print("Decryption failed! The file has been tampered with or the key is wrong.")
        return False
    except Exception as e:
        print(f"Error during AES-GCM decryption: {e}")
        return False