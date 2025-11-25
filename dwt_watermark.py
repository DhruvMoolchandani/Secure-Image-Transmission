import cv2
import numpy as np
import pywt

def embed_dwt(host_image_path, watermark_image_path, output_path, alpha=0.1):
    """
    Embeds a watermark into a host image using DWT.

    Args:
        host_image_path (str): Path to the original host image.
        watermark_image_path (str): Path to the watermark image.
        output_path (str): Path to save the watermarked image.
        alpha (float): Embedding strength. A small value (e.g., 0.1) is less
                       visible but less robust.
    """
    try:
        # --- 1. Load Images ---
        # Read the host image in grayscale
        host_img = cv2.imread(host_image_path, cv2.IMREAD_GRAYSCALE).astype(float)
        
        # Read the watermark image in grayscale
        watermark_img = cv2.imread(watermark_image_path, cv2.IMREAD_GRAYSCALE).astype(float)

        # --- 2. Apply DWT to Host Image ---
        # Use 'haar' wavelet, apply 1-level DWT
        coeffs_host = pywt.dwt2(host_img, 'haar')
        # Get the 4 sub-bands
        LL, (LH, HL, HH) = coeffs_host
        
        # --- 3. Prepare Watermark ---
        # Resize watermark to match the size of the high-frequency bands
        # (LH, HL, HH) are all the same size
        watermark_resized = cv2.resize(watermark_img, (LH.shape[1], LH.shape[0]))
        # Normalize watermark to range 0-1
        watermark_norm = watermark_resized / 255.0

        # --- 4. Embed Watermark ---
        # Add the normalized watermark, scaled by alpha, to the high-frequency bands
        # This is where the magic happens.
        LH_w = LH + alpha * watermark_norm
        HL_w = HL + alpha * watermark_norm
        HH_w = HH + alpha * watermark_norm
        
        # --- 5. Reconstruct Image ---
        # Apply Inverse DWT (IDWT)
        coeffs_watermarked = (LL, (LH_w, HL_w, HH_w))
        watermarked_img = pywt.idwt2(coeffs_watermarked, 'haar')
        
        # --- 6. Save Image ---
        # Clip values to 0-255 and convert to 8-bit unsigned integer
        watermarked_img = np.clip(watermarked_img, 0, 255)
        cv2.imwrite(output_path, watermarked_img.astype(np.uint8))
        print(f"Watermark embedded and saved to {output_path}")

    except Exception as e:
        print(f"Error during embedding: {e}")

def extract_dwt(original_host_path, watermarked_image_path, output_path, alpha=0.1):
    """
    Extracts a watermark from a watermarked image using DWT.
    This is NON-BLIND, meaning it requires the original host image.

    Args:
        original_host_path (str): Path to the *original* host image.
        watermarked_image_path (str): Path to the watermarked image.
        output_path (str): Path to save the extracted watermark.
        alpha (float): The *same* embedding strength used during embedding.
    """
    try:
        # --- 1. Load Images ---
        original_img = cv2.imread(original_host_path, cv2.IMREAD_GRAYSCALE).astype(float)
        watermarked_img = cv2.imread(watermarked_image_path, cv2.IMREAD_GRAYSCALE).astype(float)

        # --- 2. Apply DWT to Both Images ---
        coeffs_original = pywt.dwt2(original_img, 'haar')
        _, (LH_o, HL_o, HH_o) = coeffs_original
        
        coeffs_watermarked = pywt.dwt2(watermarked_img, 'haar')
        _, (LH_w, HL_w, HH_w) = coeffs_watermarked

        # --- 3. Extract Watermark ---
        # Reverse the embedding formula: W_norm = (Band_w - Band_o) / alpha
        # We can average the result from the 3 bands to get a cleaner extraction
        ex_LH = (LH_w - LH_o) / alpha
        ex_HL = (HL_w - HL_o) / alpha
        ex_HH = (HH_w - HH_o) / alpha
        
        # Average the three extracted watermarks
        extracted_norm = (ex_LH + ex_HL + ex_HH) / 3.0
        
        # --- 4. Save Extracted Watermark ---
        # De-normalize (scale back to 0-255)
        extracted_img = extracted_norm * 255.0
        
        # Clip values and save
        extracted_img = np.clip(extracted_img, 0, 255)
        cv2.imwrite(output_path, extracted_img.astype(np.uint8))
        print(f"Watermark extracted and saved to {output_path}")
        
    except Exception as e:
        print(f"Error during extraction: {e}")