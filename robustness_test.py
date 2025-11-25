import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim

# Import all your functions
try:
    from dwt_watermark import embed_dwt, extract_dwt
except ImportError:
    print("FATAL: 'dwt_watermark.py' not found in this folder.")
    exit()

def calculate_similarity(original_img, extracted_img):
    # Resize extracted image to match original for a fair comparison
    original_resized = cv2.resize(original_img, (extracted_img.shape[1], extracted_img.shape[0]))
    # Calculate SSIM
    score = ssim(original_resized, extracted_img, data_range=extracted_img.max() - extracted_img.min())
    return score

def add_gaussian_noise(image):
    row, col = image.shape
    mean = 0
    var = 100 
    sigma = var**0.5
    gauss = np.random.normal(mean, sigma, (row, col))
    noisy_image = image + gauss
    noisy_image = np.clip(noisy_image, 0, 255)
    return noisy_image.astype(np.uint8)

if __name__ == "__main__":
    print("="*60)
    print("### Test 3: Robustness Attacks on Decrypted Image ###")
    print("="*60)
    
    # --- 1. Get User Input ---
    FILE_HOST = input("Enter ORIGINAL HOST image (e.g., Original_image.png): ")
    FILE_WATERMARK = input("Enter ORIGINAL WATERMARK image (e.g., watermark_logo.png): ")
    FILE_DECRYPTED = input("Enter DECRYPTED image (e.g., Original_image_aes_decrypted.png): ")
    
    if not (os.path.exists(FILE_DECRYPTED) and os.path.exists(FILE_HOST) and os.path.exists(FILE_WATERMARK)):
        print("Error: Files not found.")
        exit()

    # --- 2. Settings ---
    ALPHA_STRONG = 25.0
    print(f"\n[INFO] Using STRONG alpha = {ALPHA_STRONG}")

    # --- 3. Create Output Filenames ---
    base_name = os.path.splitext(FILE_DECRYPTED)[0]
    FILE_EXTRACT_CLEAN = f"{base_name}_EXTRACT_CLEAN.png" # <--- NEW
    FILE_ATTACK_JPEG = f"{base_name}_ATTACK_JPEG.jpg"
    FILE_ATTACK_NOISE = f"{base_name}_ATTACK_NOISE.png"
    FILE_EXTRACT_JPEG = f"{base_name}_EXTRACT_FROM_JPEG.png"
    FILE_EXTRACT_NOISE = f"{base_name}_EXTRACT_FROM_NOISE.png"

    # --- 4. Load the Decrypted Image ---
    watermarked_image = cv2.imread(FILE_DECRYPTED, cv2.IMREAD_GRAYSCALE)

    # =========================================================
    # TEST 0: CONTROL GROUP (NO ATTACK)
    # This proves your grayscale reading is correct.
    # =========================================================
    print("\n[STEP 0] Extracting from CLEAN image (No Attack)...")
    extract_dwt(FILE_HOST, FILE_DECRYPTED, FILE_EXTRACT_CLEAN, alpha=ALPHA_STRONG)
    print(f"   -> Saved: {FILE_EXTRACT_CLEAN}")

    # =========================================================
    # TEST 1: JPEG ATTACK
    # =========================================================
    print("\n[STEP 1] Performing JPEG Compression Attack...")
    cv2.imwrite(FILE_ATTACK_JPEG, watermarked_image, [cv2.IMWRITE_JPEG_QUALITY, 50])
    print(f"   -> Saved Attacked Image: {FILE_ATTACK_JPEG}")
    
    print(f"   -> Extracting watermark...")
    extract_dwt(FILE_HOST, FILE_ATTACK_JPEG, FILE_EXTRACT_JPEG, alpha=ALPHA_STRONG)
    
    # =========================================================
    # TEST 2: NOISE ATTACK
    # =========================================================
    print("\n[STEP 2] Performing Gaussian Noise Attack...")
    noisy_image = add_gaussian_noise(watermarked_image)
    cv2.imwrite(FILE_ATTACK_NOISE, noisy_image)
    print(f"   -> Saved Attacked Image: {FILE_ATTACK_NOISE}")
    
    print(f"   -> Extracting watermark...")
    extract_dwt(FILE_HOST, FILE_ATTACK_NOISE, FILE_EXTRACT_NOISE, alpha=ALPHA_STRONG)

    # --- 7. FINAL ANALYSIS ---
    print("\n" + "="*60)
    print("### Robustness Test Results ###")
    print("="*60)
    
    # Load images
    original_watermark_gray = cv2.imread(FILE_WATERMARK, cv2.IMREAD_GRAYSCALE)
    extracted_clean = cv2.imread(FILE_EXTRACT_CLEAN, cv2.IMREAD_GRAYSCALE) # <--- NEW
    extracted_jpeg = cv2.imread(FILE_EXTRACT_JPEG, cv2.IMREAD_GRAYSCALE)
    extracted_noise = cv2.imread(FILE_EXTRACT_NOISE, cv2.IMREAD_GRAYSCALE)

    if extracted_jpeg is None:
        print("Error: Extraction failed.")
    else:
        # Calculate scores
        score_clean = calculate_similarity(original_watermark_gray, extracted_clean)
        score_jpeg = calculate_similarity(original_watermark_gray, extracted_jpeg)
        score_noise = calculate_similarity(original_watermark_gray, extracted_noise)

        print(f"1. IDEAL CASE (No Attack):     {score_clean:.4f} (Should be near 1.0)")
        print(f"2. Similarity after JPEG (50): {score_jpeg:.4f}")
        print(f"3. Similarity after Noise:     {score_noise:.4f}")
