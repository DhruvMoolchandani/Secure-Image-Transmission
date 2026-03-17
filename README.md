# 🔒 Secure Image Transmission System (Defense-in-Depth)
### A Web-Based Approach using DWT Watermarking & AES-GCM Encryption

**Course:** Image Forensics and Security  
**Topic:** Multimedia Security / Digital Watermarking

🚀 **Live Web App:** [https://secure-image-transmission.vercel.app/](https://secure-image-transmission.vercel.app/)

---

## 📖 Project Overview
This project implements a **Defense-in-Depth** strategy for securing digital images in highly sensitive environments. It addresses the critical issues of unauthorized interception, data tampering, and copyright theft during digital transmission.

By combining **Discrete Wavelet Transform (DWT)** for robust watermarking and **AES-GCM** for authenticated encryption, this system ensures:

1.  **Confidentiality:** The image is inaccessible to unauthorized users (AES Encryption).
2.  **Integrity:** Any tampering with the encrypted file is immediately detected and blocked (GCM Tagging).
3.  **Authenticity:** The source of the image is verified via secret keys and extracted watermarks.
4.  **Robustness:** Ownership proof (watermark) survives signal degradation.

---

## 🛡️ Real-World Defense & Security Applications
This technology pipeline is directly applicable to modern defense, intelligence, and military operations:

*   🚁 **Secure UAV Transmission:** Drones embed covert signatures (like GPS) before AES-GCM encryption. If adversaries alter the signal mid-air, GCM authentication fails instantly, alerting command to a cyberattack.
*   🕵️ **Traitor Tracing:** Classified maps are uniquely watermarked before distribution to different commanders. If a map leaks online, extraction reveals the exact source, even if the image is printed, photographed, or cropped.
*   📡 **Covert Communications (Steganography):** Operatives embed secret orders as a watermark inside innocent-looking photos to avoid suspicion during device searches in hostile territory.
*   🛡️ **Battlefield Authentication:** The watermark acts as a built-in stamp. Field units extract it to verify the origin of tactical updates and avoid spoofed enemy ambushes.

---

## 🛠️ Technology Stack
*   **Backend & API:** `Python 3.x`, `Flask`, `Werkzeug`
*   **Frontend UI:** Vanilla `HTML5`, `CSS3` (Glassmorphism), `JavaScript`
*   **Watermarking:** `PyWavelets` (Discrete Wavelet Transform), `opencv-python`
*   **Encryption:** `pycryptodome` (AES-GCM Mode, Chaos Ciper)

---

## 🚀 Installation & Setup

### 1. Requirements
Ensure you have Python installed. If not, download it from [python.org](https://www.python.org/).

### 2. Install Dependencies
Open your terminal in the project directory and run:
cd Temp
pip install -r requirements.txt

### 3. Run the Web Application
Start the Flask backend server:
python app.py

Then, open your web browser and navigate to:
http://localhost:5000

---

## ⚙️ Methodology

### 1. Robust Watermarking (DWT)
Unlike fragile LSB watermarking, we embed the watermark into the **frequency domain** of the image using DWT.
*   **Process:** The host image is decomposed into sub-bands (LL, LH, HL, HH). The watermark is embedded into the high-frequency bands.
*   **Strength:** We use dynamic alpha strength to ensure the watermark survives signal degradation while remaining invisible.

### 2. Authenticated Encryption (AES-GCM)
We use **AES-256 in Galois/Counter Mode (GCM)**.
*   **Why GCM?** Unlike standard modes (ECB/CBC) which only provide confidentiality, GCM provides an **Integrity Tag**.
*   **Mechanism:** If a single bit of the encrypted file is flipped during transmission, the GCM tag verification fails, and the system refuses to decrypt the file.

---
**Disclaimer:** This software is developed for educational purposes within the context of an Image Forensics and Security course.