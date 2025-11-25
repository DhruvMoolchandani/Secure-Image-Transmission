import cv2
import numpy as np

def generate_logistic_keystream(x0, mu, size):
    """
    Generates a chaotic keystream using the Logistic Map.
    x_n+1 = mu * x_n * (1 - x_n)

    Args:
        x0 (float): Initial value (key), 0 < x0 < 1.
        mu (float): Control parameter (key), 3.57 < mu <= 4.0 for chaos.
        size (int): The total number of bytes needed (e.g., image width * height * channels).
    
    Returns:
        numpy.ndarray: A keystream of 'uint8' bytes, 1D.
    """
    
    # --- 1. Settle the Map ---
    # Iterate 1000 times to discard initial transient values.
    # This makes the sequence more chaotic and less dependent on the exact x0.
    x = x0
    for _ in range(1000):
        x = mu * x * (1 - x)
        
    # --- 2. Generate Keystream ---
    keystream_float = np.zeros(size)
    for i in range(size):
        x = mu * x * (1 - x)
        keystream_float[i] = x
        
    # --- 3. Convert to Bytes ---
    # Convert the float sequence [0, 1] to a byte sequence [0, 255]
    keystream_bytes = (keystream_float * 255).astype(np.uint8)
    return keystream_bytes

def encrypt_decrypt_chaos(input_image_path, output_image_path, key_x0, key_mu):
    """
    Encrypts or decrypts an image using a chaos-based stream cipher (XOR).
    This function is symmetric; running it on an encrypted image decrypts it.

    Args:
        input_image_path (str): Path to the image to process.
        output_image_path (str): Path to save the processed image.
        key_x0 (float): The 'x0' key for the logistic map.
        key_mu (float): The 'mu' key for the logistic map.
    """
    try:
        # --- 1. Load Image ---
        # Read the image. Note: We read it in color (3 channels) by default.
        image = cv2.imread(input_image_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image from {input_image_path}")
            
        original_shape = image.shape
        
        # --- 2. Flatten Image ---
        # Convert the 3D (height, width, channels) image to a 1D stream of bytes
        image_flat = image.flatten()
        
        # --- 3. Generate Keystream ---
        # Generate a keystream of the *exact same size* as the flattened image
        keystream = generate_logistic_keystream(key_x0, key_mu, len(image_flat))
        
        # --- 4. Apply XOR ---
        # This is the core of the stream cipher.
        # (Image) XOR (Key) = Encrypted
        # (Encrypted) XOR (Key) = Image
        processed_flat = np.bitwise_xor(image_flat, keystream)
        
        # --- 5. Reshape and Save ---
        # Reshape the 1D processed stream back to the original image's 3D shape
        processed_image = processed_flat.reshape(original_shape)
        
        cv2.imwrite(output_image_path, processed_image)
        print(f"Chaos process complete. Output saved to {output_image_path}")

    except Exception as e:
        print(f"Error during chaos cipher: {e}")