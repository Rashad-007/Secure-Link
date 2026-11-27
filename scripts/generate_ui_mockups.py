import os
from PIL import Image, ImageDraw, ImageFont

def create_ui_screenshots():
    screen_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "screenshots")
    os.makedirs(screen_dir, exist_ok=True)

    # Helper to draw a modern browser frame with cyber content
    def create_browser_canvas(title_text):
        img = Image.new('RGB', (1200, 750), color='#0B0F19')
        draw = ImageDraw.Draw(img)

        # Top Browser Title Bar
        draw.rectangle([0, 0, 1200, 45], fill='#111827')
        # Browser buttons
        draw.ellipse([15, 16, 27, 28], fill='#EF4444')
        draw.ellipse([35, 16, 47, 28], fill='#F59E0B')
        draw.ellipse([55, 16, 67, 28], fill='#10B981')

        # Address bar
        draw.rectangle([100, 10, 800, 35], fill='#162032', outline='#24344D', width=1)
        draw.text((120, 16), f"https://securelink.college.edu/ {title_text}", fill='#94A3B8')

        # Navbar
        draw.rectangle([0, 45, 1200, 105], fill='#111827', outline='#24344D', width=1)
        draw.text((40, 65), "SecureLink", fill='#00F0FF')
        draw.text((140, 67), "DNS Academic Mini-Project", fill='#64748B')
        draw.text((450, 68), "Dashboard    Send File    Received    Audit History    Security Arch", fill='#94A3B8')
        draw.text((1050, 67), "alice (RSA-3072)", fill='#38BDF8')

        return img, draw

    # 1. Dashboard Screenshot
    img, draw = create_browser_canvas("- Dashboard")
    # Header
    draw.text((40, 130), "Security Operations Dashboard", fill='#FFFFFF')
    draw.text((40, 160), "Logged in as alice | Authenticated Session", fill='#64748B')

    # Stat boxes
    stats = [
        ("FILES DISPATCHED", "12", "Total: 4.82 MB", '#38BDF8', 40),
        ("FILES RECEIVED", "9", "Total: 3.15 MB", '#6366F1', 320),
        ("INTEGRITY VERIFIED", "21", "Valid SHA-256 & GCM", '#10B981', 600),
        ("SECURITY ALERTS", "1", "Tamper Blocked", '#F43F5E', 880),
    ]
    for label, val, sub, col, x in stats:
        draw.rectangle([x, 200, x+280, 310], fill='#162032', outline='#24344D', width=1)
        draw.text((x+20, 215), label, fill='#94A3B8')
        draw.text((x+20, 240), val, fill=col)
        draw.text((x+20, 280), sub, fill='#64748B')

    # Active suite card
    draw.rectangle([40, 340, 500, 700], fill='#162032', outline='#24344D', width=1)
    draw.text((60, 360), "Active Cryptographic Parameters", fill='#00F0FF')
    draw.text((60, 410), "Bulk Cipher: AES-256-GCM (256-bit Key, 96-bit IV)", fill='#FFFFFF')
    draw.text((60, 460), "Key Exchange: RSA-3072 / OAEP / SHA-256", fill='#FFFFFF')
    draw.text((60, 510), "Integrity Hash: SHA-256 (Pre & Post verification)", fill='#FFFFFF')
    draw.text((60, 560), "Zero-Plaintext Storage: Verified on Disk", fill='#10B981')
    draw.text((60, 610), "Private Key Protection: PKCS#8 + PBKDF2 AES-CBC", fill='#F59E0B')

    # Activity table card
    draw.rectangle([530, 340, 1160, 700], fill='#162032', outline='#24344D', width=1)
    draw.text((550, 360), "Live Security Audit Log", fill='#00F0FF')
    logs = [
        ("[FILE_SENT]", "Encrypted 'report.pdf' (1.2MB) to bob", "2026-11-11 05:20"),
        ("[FILE_DECRYPTED]", "Decrypted 'notes.txt' - SHA-256 Valid", "2026-11-11 05:15"),
        ("[TAMPER_ALERT]", "AES-GCM tag mismatch on #4 (Attack Detected!)", "2026-11-11 05:08"),
        ("[USER_LOGIN]", "Session authenticated from 192.168.1.15", "2026-11-11 05:01"),
        ("[USER_REGISTERED]", "RSA-3072 key pair generated successfully", "2026-11-11 04:55"),
    ]
    for idx, (event, det, ts) in enumerate(logs):
        y = 410 + idx * 55
        draw.text((550, y), event, fill='#38BDF8')
        draw.text((700, y), det, fill='#E2E8F0')
        draw.text((1020, y), ts, fill='#64748B')

    p1 = os.path.join(screen_dir, "02_security_dashboard.png")
    img.save(p1)
    print(f"[+] Generated: {p1}")

    # 2. Decrypt & Verification Workbench Screenshot
    img2, draw2 = create_browser_canvas("- Decrypt & Verify")
    draw2.text((40, 130), "Cryptographic Inspection & Decryption", fill='#FFFFFF')
    draw2.text((40, 160), "Transmission #104 | confidential_project_report.pdf", fill='#64748B')

    # Verification Success Box
    draw2.rectangle([40, 200, 1160, 480], fill='#162032', outline='#10B981', width=2)
    draw2.text((60, 220), "DECRYPTION & INTEGRITY VERIFICATION SUCCESSFUL", fill='#10B981')
    draw2.text((60, 255), "AES-256-GCM authentication tag verified. SHA-256 bit-level match confirmed.", fill='#94A3B8')

    draw2.rectangle([60, 290, 1140, 410], fill='#060911', outline='#24344D', width=1)
    draw2.text((80, 310), "Original Plaintext SHA-256 Digest (Pre-Encryption):", fill='#94A3B8')
    draw2.text((80, 335), "7d9b93e62f0fcf9e1d897f259db85b30b42f618a803e7a02e6bdfd8a8f11599a", fill='#38BDF8')

    draw2.text((80, 365), "Decrypted Plaintext SHA-256 Digest (Post-Decryption):", fill='#94A3B8')
    draw2.text((80, 390), "7d9b93e62f0fcf9e1d897f259db85b30b42f618a803e7a02e6bdfd8a8f11599a", fill='#10B981')

    draw2.text((60, 435), "STATUS: SHA-256 HASH MATCH: YES | AES-GCM GHASH TAG: VALID (0 Tampering)", fill='#10B981')

    # Tamper simulation section
    draw2.rectangle([40, 510, 1160, 680], fill='#1F1318', outline='#F43F5E', width=1)
    draw2.text((60, 530), "Academic Attack Simulation Lab (DNS Viva Test)", fill='#F43F5E')
    draw2.text((60, 565), "Demonstrate how AES-256-GCM authenticated encryption defends against ciphertext manipulation.", fill='#94A3B8')
    draw2.rectangle([60, 600, 380, 650], fill='#F43F5E')
    draw2.text((80, 618), "Simulate Ciphertext Tampering Attack", fill='#FFFFFF')

    p2 = os.path.join(screen_dir, "05_decrypt_and_integrity_verification.png")
    img2.save(p2)
    print(f"[+] Generated: {p2}")

    # 3. Send Encrypted File Screenshot
    img3, draw3 = create_browser_canvas("- Send File")
    draw3.text((40, 130), "Encrypted File Dispatch", fill='#FFFFFF')
    draw3.text((40, 160), "AES-256-GCM Bulk Encryption + RSA-3072 Key Encapsulation", fill='#64748B')

    draw3.rectangle([40, 200, 800, 680], fill='#162032', outline='#24344D', width=1)
    draw3.text((70, 230), "Select Intended Recipient:", fill='#E2E8F0')
    draw3.rectangle([70, 260, 770, 305], fill='#0B0F19', outline='#24344D', width=1)
    draw3.text((90, 275), "bob (bob@university.edu) - RSA-3072 Public Key Active", fill='#38BDF8')

    draw3.text((70, 335), "Upload File:", fill='#E2E8F0')
    draw3.rectangle([70, 365, 770, 520], fill='#080D18', outline='#00F0FF', width=2)
    draw3.text((260, 420), "Drag and drop file here or click to browse", fill='#FFFFFF')
    draw3.text((250, 450), "confidential_project_report.pdf (1.2 MB selected)", fill='#00F0FF')

    draw3.rectangle([70, 550, 770, 640], fill='#060911', outline='#24344D', width=1)
    draw3.text((90, 570), "Cryptographic Sequence: 1. SHA-256 -> 2. AES-256-GCM -> 3. RSA-3072 OAEP", fill='#94A3B8')
    draw3.text((90, 600), "Zero retention guarantee: Plaintext and AES key purged from RAM upon dispatch.", fill='#10B981')

    # Right side guide
    draw3.rectangle([830, 200, 1160, 680], fill='#162032', outline='#24344D', width=1)
    draw3.text((850, 230), "Sender Guidelines", fill='#00F0FF')
    draw3.text((850, 270), "Max Content Limit: 16 MB", fill='#E2E8F0')
    draw3.text((850, 310), "Allowed Extensions: PDF, TXT,\nPNG, DOCX, ZIP, CSV", fill='#94A3B8')
    draw3.text((850, 370), "Security Guarantee:\nSender cannot decrypt the file\nonce wrapped with recipient's\npublic key.", fill='#F59E0B')

    p3 = os.path.join(screen_dir, "03_send_encrypted_file.png")
    img3.save(p3)
    print(f"[+] Generated: {p3}")

    # 4. Landing Page
    img4, draw4 = create_browser_canvas("- Home")
    draw4.text((40, 130), "SecureLink: Hybrid Cryptography File Transfer", fill='#FFFFFF')
    draw4.text((40, 160), "Data Network Security | Academic Mini-Project", fill='#64748B')
    draw4.rectangle([40, 200, 750, 420], fill='#162032', outline='#00F0FF', width=2)
    draw4.text((60, 230), "End-to-End Cryptographic Security", fill='#00F0FF')
    draw4.text((60, 270), "Harmonizing AES-256-GCM symmetric speed with RSA-3072 asymmetric key exchange\nand SHA-256 integrity verification.", fill='#E2E8F0')
    draw4.rectangle([60, 340, 240, 385], fill='#00F0FF')
    draw4.text((75, 355), "Create Cryptographic Identity", fill='#0B0F19')
    draw4.rectangle([260, 340, 400, 385], fill='#111827', outline='#38BDF8', width=1)
    draw4.text((285, 355), "Sign In to Account", fill='#38BDF8')

    draw4.rectangle([40, 450, 380, 680], fill='#162032', outline='#24344D', width=1)
    draw4.text((60, 470), "1. AES-256-GCM", fill='#38BDF8')
    draw4.text((60, 510), "Authenticated encryption\nproviding confidentiality\nand integrity in one pass.", fill='#94A3B8')

    draw4.rectangle([420, 450, 760, 680], fill='#162032', outline='#24344D', width=1)
    draw4.text((440, 470), "2. RSA-3072 OAEP", fill='#818CF8')
    draw4.text((440, 510), "Asymmetric key encapsulation\nsolving symmetric key distribution\nwith 128-bit quantum security.", fill='#94A3B8')

    draw4.rectangle([800, 450, 1160, 680], fill='#162032', outline='#24344D', width=1)
    draw4.text((820, 470), "3. SHA-256 Digest", fill='#34D399')
    draw4.text((820, 510), "Bit-for-bit file verification\nensuring complete fidelity\nbefore and after decryption.", fill='#94A3B8')

    p4 = os.path.join(screen_dir, "01_landing_page.png")
    img4.save(p4)
    print(f"[+] Generated: {p4}")

    # 5. Profile & PKI Key Info
    img5, draw5 = create_browser_canvas("- Profile & PKI")
    draw5.text((40, 130), "Cryptographic Identity & Keys", fill='#FFFFFF')
    draw5.text((40, 160), "Public Key Infrastructure (PKI) Profile for alice", fill='#64748B')
    draw5.rectangle([40, 200, 1160, 680], fill='#162032', outline='#24344D', width=1)
    draw5.text((60, 230), "Username: alice   |   Email: alice@university.edu   |   Identity Created: 2026-11-11", fill='#E2E8F0')
    draw5.text((60, 280), "Public Key SHA-256 Fingerprint:", fill='#94A3B8')
    draw5.text((60, 310), "e4b9c1825fa77319c5b290df627ea7d4e38c92b95fa979bc75841029c9183492", fill='#00F0FF')
    draw5.text((60, 360), "RSA-3072 Public Key (SubjectPublicKeyInfo PEM):", fill='#94A3B8')
    draw5.rectangle([60, 390, 1140, 580], fill='#060911', outline='#24344D', width=1)
    draw5.text((80, 410), "-----BEGIN PUBLIC KEY-----\nMIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEA1mO4kP0...\n-----END PUBLIC KEY-----", fill='#38BDF8')
    draw5.text((60, 610), "Private Key: Encrypted via PKCS#8 AES-256-CBC using master password. Never exposed.", fill='#F59E0B')

    p5 = os.path.join(screen_dir, "07_pki_profile.png")
    img5.save(p5)
    print(f"[+] Generated: {p5}")

if __name__ == "__main__":
    create_ui_screenshots()
