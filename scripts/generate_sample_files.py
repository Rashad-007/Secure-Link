import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

def generate_samples():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_files")
    os.makedirs(sample_dir, exist_ok=True)

    # 1. Text sample
    txt_path = os.path.join(sample_dir, "network_security_notes.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(
            "===========================================================\n"
            "DATA NETWORK SECURITY (DNS) - COLLEGE LABORATORY EXPERIMENT\n"
            "Project: SecureLink Hybrid Cryptography File Transfer\n"
            "===========================================================\n\n"
            "Classification: CONFIDENTIAL ACADEMIC RECORD\n"
            "Ciphers Applied: AES-256-GCM (Authenticated Encryption)\n"
            "Key Exchange: RSA-3072 / OAEP with SHA-256 MGF1\n"
            "Integrity Verification: SHA-256 Constant-Time Comparison\n\n"
            "This document verifies that bulk plaintext has been successfully\n"
            "encrypted by the sender, encapsulated with the receiver's public key,\n"
            "stored as zero-plaintext ciphertext, and recovered intact by the receiver.\n"
        )
    print(f"[+] Generated: {txt_path}")

    # 2. PDF sample
    pdf_path = os.path.join(sample_dir, "confidential_project_report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setTitle("SecureLink Confidential Report")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, 720, "SecureLink - Academic Cryptographic Payload")
    c.setFont("Helvetica", 12)
    c.drawString(72, 690, "Subject: Data Network Security")
    c.drawString(72, 670, "Algorithm: AES-256-GCM + RSA-3072 + SHA-256")
    c.drawString(72, 640, "This PDF document demonstrates binary file preservation across transmission.")
    c.drawString(72, 620, "Every byte is authenticated by the 128-bit GHASH tag.")
    c.showPage()
    c.save()
    print(f"[+] Generated: {pdf_path}")

    # 3. PNG Image sample
    img_path = os.path.join(sample_dir, "network_topology.png")
    img = Image.new('RGB', (600, 300), color=(11, 15, 25))
    draw = ImageDraw.Draw(img)
    # Draw simple network topology nodes
    draw.rectangle([30, 30, 570, 270], outline=(0, 240, 255), width=2)
    draw.text((50, 50), "SecureLink Hybrid Cryptography Topology", fill=(0, 240, 255))
    draw.rectangle([60, 110, 200, 190], fill=(22, 32, 50), outline=(56, 189, 248), width=2)
    draw.text((75, 140), "Sender (Alice)\nAES-256-GCM", fill=(255, 255, 255))
    
    draw.line([200, 150, 390, 150], fill=(0, 240, 255), width=2)
    draw.text((230, 125), "Ciphertext Payload", fill=(148, 163, 184))

    draw.rectangle([390, 110, 530, 190], fill=(22, 32, 50), outline=(99, 102, 241), width=2)
    draw.text((405, 140), "Receiver (Bob)\nRSA-3072 Key", fill=(255, 255, 255))
    img.save(img_path)
    print(f"[+] Generated: {img_path}")

    # 4. CSV sample
    csv_path = os.path.join(sample_dir, "lab_test_data.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(
            "transfer_id,sender,receiver,algorithm,status,integrity_verified\n"
            "1,alice,bob,AES-256-GCM+RSA-3072,VERIFIED,true\n"
            "2,bob,alice,AES-256-GCM+RSA-3072,VERIFIED,true\n"
            "3,alice,bob,AES-256-GCM+RSA-3072,VERIFIED,true\n"
        )
    print(f"[+] Generated: {csv_path}")

if __name__ == "__main__":
    generate_samples()

