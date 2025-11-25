import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import random

def plot_binary_histogram(bin_file_path, output_path):
    """
    Generates and saves a histogram for a raw binary file (like AES output).
    """
    try:
        data = np.fromfile(bin_file_path, dtype=np.uint8)
        
        if data.size == 0:
            print(f"Error: Binary file is empty: {bin_file_path}")
            return

        hist, bin_edges = np.histogram(data, bins=256, range=(0, 256))

        plt.figure(figsize=(10, 6))
        plt.plot(bin_edges[0:-1], hist, color='purple') 
        plt.title(f'Byte Frequency Histogram for {os.path.basename(bin_file_path)}')
        plt.xlabel('Byte Value (0-255)')
        plt.ylabel('Frequency (Count)')
        plt.xlim([0, 256])
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.fill_between(bin_edges[0:-1], hist, color='purple', alpha=0.3)

        plt.savefig(output_path)
        plt.close()
        print(f"Binary histogram saved to {output_path}")

    except FileNotFoundError:
         print(f"Error: File not found at {bin_file_path}")
    except Exception as e:
        print(f"Error plotting binary histogram: {e}")

def plot_comparison_histogram(original_path, watermarked_path, output_path):
    """
    Plots the histogram of the Original vs Watermarked image on the SAME graph.
    Original = Red Line
    Watermarked = Green Line
    """
    try:
        # Read both images in Grayscale to compare intensity distribution
        img_orig = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
        img_water = cv2.imread(watermarked_path, cv2.IMREAD_GRAYSCALE)

        if img_orig is None:
            print(f"Error: Could not read original image at {original_path}")
            return
        if img_water is None:
            print(f"Error: Could not read watermarked image at {watermarked_path}")
            return

        # Calculate histograms
        hist_orig = cv2.calcHist([img_orig], [0], None, [256], [0, 256])
        hist_water = cv2.calcHist([img_water], [0], None, [256], [0, 256])

        # Plotting
        plt.figure(figsize=(10, 6))
        
        # Plot Original in RED
        plt.plot(hist_orig, color='red', label='Original Image', linewidth=1.5)
        
        # Plot Watermarked in GREEN (dashed to make overlap visible)
        plt.plot(hist_water, color='green', label='Watermarked Image', linewidth=1.5, linestyle='--')

        plt.title('Histogram Comparison: Original vs Watermarked')
        plt.xlabel('Pixel Intensity (0-255)')
        plt.ylabel('Number of Pixels')
        plt.xlim([0, 256])
        plt.legend() # Shows the labels
        plt.grid(True, linestyle='--', alpha=0.6)

        plt.savefig(output_path)
        plt.close()
        print(f"Comparison histogram saved to {output_path}")

    except Exception as e:
        print(f"Error plotting comparison histogram: {e}")

def plot_pixel_correlation(image_path, output_path, num_pixels=5000):
    """Generates and saves a pixel correlation plot."""
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"Error: Could not read image at {image_path}")
            return

        h, w = image.shape
        x_coords = []
        y_coords = []

        for _ in range(num_pixels):
            rand_x = random.randint(0, w - 2)
            rand_y = random.randint(0, h - 1)
            
            x_coords.append(image[rand_y, rand_x])
            y_coords.append(image[rand_y, rand_x + 1])

        plt.figure(figsize=(8, 8))
        plt.scatter(x_coords, y_coords, s=1)
        plt.title(f'Pixel Correlation for {os.path.basename(image_path)}')
        plt.xlabel('Pixel Intensity at (x, y)')
        plt.ylabel('Pixel Intensity at (x+1, y)')
        plt.xlim([0, 256])
        plt.ylim([0, 256])
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig(output_path)
        plt.close()
        print(f"Correlation plot saved to {output_path}")

    except Exception as e:
        print(f"Error plotting correlation: {e}")

if __name__ == "__main__":
    print("="*60)
    print("### Security Analysis Plot Generator ###")
    print("="*60)
    
    # --- 1. Get inputs from user ---
    file_original = input("Enter ORIGINAL host image (e.g., cover.png): ")
    file_watermarked = input("Enter WATERMARKED image (e.g., attack_host_watermarked.png): ")
    file_aes = input("Enter AES BINARY file (e.g., cover_aes.bin): ")

    print("\n[INFO] Generating plots...")

    # --- 2. Generate Comparison Histogram (Red vs Green) ---
    if os.path.exists(file_original) and os.path.exists(file_watermarked):
        plot_comparison_histogram(file_original, file_watermarked, "analysis_hist_comparison.png")
    else:
        print("Skipping comparison histogram: One or both image files not found.")
    
    # --- 3. Generate AES Binary Histogram ---
    if os.path.exists(file_aes):
        plot_binary_histogram(file_aes, "analysis_hist_aes.png")
    else:
        print(f"Skipping AES histogram: {file_aes} not found.")

    # --- 4. Generate Correlation Plots ---
    if os.path.exists(file_original):
        plot_pixel_correlation(file_original, "analysis_corr_original.png")
    
    # We usually also check correlation of encrypted file (if it were an image), 
    # but since it's binary, the Histogram is the best proof.
        
    print("\n" + "="*60)
    print("Analysis Complete.")