# 🔒 Secure Image Transmission System
### A Hybrid Approach using DWT Watermarking & AES-GCM Encryption

**Course:** Image Forensics and Security  
**Topic:** Multimedia Security / Digital Watermarking

---

## 📖 Project Overview
This project implements a **Defense-in-Depth** strategy for securing digital images. It addresses the critical issues of unauthorized interception, data tampering, and copyright theft during digital transmission.

By combining **Discrete Wavelet Transform (DWT)** for robust watermarking and **AES-GCM** for authenticated encryption, this system ensures:

1.  **Confidentiality:** The image is inaccessible to unauthorized users (Encryption).
2.  **Integrity:** Any tampering with the encrypted file is immediately detected and blocked.
3.  **Authenticity:** The source of the image is verified via secret keys.
4.  **Robustness:** Ownership proof (watermark) survives attacks like JPEG compression and Gaussian Noise even after decryption.

---

## 🛠️ Technology Stack
* **Language:** Python 3.x
* **Watermarking:** `PyWavelets` (Discrete Wavelet Transform)
* **Encryption:** `pycryptodome` (AES-GCM Mode)
* **Image Processing:** `opencv-python` (OpenCV), `numpy`
* **Analysis:** `matplotlib` (Histograms), `scikit-image` (SSIM Metrics)

---

## ⚙️ Methodology

### 1. Robust Watermarking (DWT)
Unlike fragile LSB watermarking, we embed the watermark into the **frequency domain** of the image using DWT.
* **Process:** The host image is decomposed into sub-bands (LL, LH, HL, HH). The watermark is embedded into the high-frequency bands.
* **Strength:** We use an alpha factor of **25.0** to ensure the watermark survives signal degradation.

### 2. Authenticated Encryption (AES-GCM)
We use **AES-256 in Galois/Counter Mode (GCM)**.
* **Why GCM?** Unlike standard modes (ECB/CBC) which only provide confidentiality, GCM provides an **Integrity Tag**.
* **Mechanism:** If a single bit of the encrypted file is flipped during transmission, the GCM tag verification fails, and the system refuses to decrypt the file (protecting the user from corrupted data).

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/Secure-Image-Transmission.git](https://github.com/YOUR_USERNAME/Secure-Image-Transmission.git)
cd Secure-Image-Transmission