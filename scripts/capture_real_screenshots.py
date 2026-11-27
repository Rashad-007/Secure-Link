import os
import sys
import io
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from database.db import init_db, execute_db
from services.key_management import create_user_keys
from services.encryption_service import process_and_encrypt_upload
from services.transfer_service import decrypt_and_verify_transfer, simulate_tampering_attack
from crypto.hashing import hash_user_password
from werkzeug.datastructures import FileStorage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DOCS_SCREENSHOTS_DIR = os.path.join(BASE_DIR, "docs", "screenshots")
TEMP_HTML_DIR = os.path.join(BASE_DIR, "rendered_app_pages")

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def take_chrome_screenshot(html_file, output_png, window_size="1280,850"):
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={window_size}",
        f"--screenshot={output_png}",
        f"file:///{html_file.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def inject_base_url(html_bytes):
    html_text = html_bytes.decode('utf-8')
    # Inject base href to resolve local static assets properly in Chrome
    base_tag = f'<base href="file:///{BASE_DIR.replace(os.sep, "/")}/">\n'
    if "<head>" in html_text:
        html_text = html_text.replace("<head>", f"<head>\n{base_tag}", 1)
    return html_text

def run_capture_pipeline():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(DOCS_SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(TEMP_HTML_DIR, exist_ok=True)

    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    with app.app_context():
        # Setup demo users: Alice and Bob
        # Reset tables for clean demonstration
        execute_db("DELETE FROM transfers")
        execute_db("DELETE FROM audit_logs")
        execute_db("DELETE FROM login_attempts")
        execute_db("DELETE FROM users")

        alice_pub, alice_priv = create_user_keys("AliceMasterPassword2026!")
        bob_pub, bob_priv = create_user_keys("BobMasterPassword2026!")

        alice_id = execute_db(
            "INSERT INTO users (username, email, password_hash, public_key, encrypted_private_key) VALUES (?, ?, ?, ?, ?)",
            ("alice", "alice@university.edu", hash_user_password("AliceMasterPassword2026!"), alice_pub, alice_priv)
        )
        bob_id = execute_db(
            "INSERT INTO users (username, email, password_hash, public_key, encrypted_private_key) VALUES (?, ?, ?, ?, ?)",
            ("bob", "bob@university.edu", hash_user_password("BobMasterPassword2026!"), bob_pub, bob_priv)
        )

        # -------------------------------------------------------------
        # 1. Landing Page
        # -------------------------------------------------------------
        resp = client.get('/')
        p1_html = os.path.join(TEMP_HTML_DIR, "01_landing_page.html")
        with open(p1_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p1_png = os.path.join(SCREENSHOTS_DIR, "01_landing_page.png")
        take_chrome_screenshot(p1_html, p1_png)
        print(f"[+] Captured: {p1_png}")

        # -------------------------------------------------------------
        # 2. Login Page
        # -------------------------------------------------------------
        resp = client.get('/login')
        p2_html = os.path.join(TEMP_HTML_DIR, "02_login_page.html")
        with open(p2_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p2_png = os.path.join(SCREENSHOTS_DIR, "02_login_page.png")
        take_chrome_screenshot(p2_html, p2_png)
        print(f"[+] Captured: {p2_png}")

        # Authenticate Alice's Session
        with client.session_transaction() as sess:
            sess['user_id'] = alice_id
            sess['username'] = "alice"
            sess['email'] = "alice@university.edu"

        # -------------------------------------------------------------
        # 3. Dashboard (Alice)
        # -------------------------------------------------------------
        resp = client.get('/dashboard')
        p3_html = os.path.join(TEMP_HTML_DIR, "03_dashboard.html")
        with open(p3_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p3_png = os.path.join(SCREENSHOTS_DIR, "03_dashboard.png")
        take_chrome_screenshot(p3_html, p3_png)
        print(f"[+] Captured: {p3_png}")

        # -------------------------------------------------------------
        # 4. Send File Page
        # -------------------------------------------------------------
        resp = client.get('/send')
        p4_html = os.path.join(TEMP_HTML_DIR, "04_send_file_page.html")
        with open(p4_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p4_png = os.path.join(SCREENSHOTS_DIR, "04_send_file_page.png")
        take_chrome_screenshot(p4_html, p4_png)
        print(f"[+] Captured: {p4_png}")

        # -------------------------------------------------------------
        # 5. Successful Encryption & Dispatch (Alice sends file to Bob)
        # -------------------------------------------------------------
        sample_pdf = os.path.join(BASE_DIR, "sample_files", "confidential_project_report.pdf")
        with open(sample_pdf, "rb") as f:
            pdf_bytes = f.read()

        file_payload = (io.BytesIO(pdf_bytes), "confidential_project_report.pdf")
        resp = client.post('/send', data={"receiver_id": bob_id, "file": file_payload}, follow_redirects=True)
        p5_html = os.path.join(TEMP_HTML_DIR, "05_successful_encryption.html")
        with open(p5_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p5_png = os.path.join(SCREENSHOTS_DIR, "05_successful_encryption.png")
        take_chrome_screenshot(p5_html, p5_png)
        print(f"[+] Captured: {p5_png}")

        # Also send a notes.txt from Alice to Bob
        sample_txt = os.path.join(BASE_DIR, "sample_files", "network_security_notes.txt")
        with open(sample_txt, "rb") as f:
            txt_bytes = f.read()
        client.post('/send', data={"receiver_id": bob_id, "file": (io.BytesIO(txt_bytes), "network_security_notes.txt")}, follow_redirects=True)

        # -------------------------------------------------------------
        # Switch Session to Bob (Receiver)
        # -------------------------------------------------------------
        with client.session_transaction() as sess:
            sess['user_id'] = bob_id
            sess['username'] = "bob"
            sess['email'] = "bob@university.edu"

        # -------------------------------------------------------------
        # 6. Received Files Page (Bob's Inbox)
        # -------------------------------------------------------------
        resp = client.get('/received')
        p6_html = os.path.join(TEMP_HTML_DIR, "06_received_file_page.html")
        with open(p6_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p6_png = os.path.join(SCREENSHOTS_DIR, "06_received_file_page.png")
        take_chrome_screenshot(p6_html, p6_png)
        print(f"[+] Captured: {p6_png}")

        # -------------------------------------------------------------
        # 7 & 8. Successful Decryption & Integrity Verification Workbench
        # -------------------------------------------------------------
        from database.db import query_db
        transfers = query_db("SELECT transfer_id FROM transfers WHERE receiver_id = ? ORDER BY transfer_id ASC", (bob_id,))
        t1_id = transfers[0]['transfer_id']
        t2_id = transfers[1]['transfer_id']

        # Bob decrypts transfer #1 (confidential_project_report.pdf)
        resp = client.post(f'/decrypt/{t1_id}', data={"password": "BobMasterPassword2026!"})
        p7_html = os.path.join(TEMP_HTML_DIR, "07_successful_decryption.html")
        with open(p7_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p7_png = os.path.join(SCREENSHOTS_DIR, "07_successful_decryption.png")
        p8_png = os.path.join(SCREENSHOTS_DIR, "08_integrity_verification.png")
        take_chrome_screenshot(p7_html, p7_png)
        take_chrome_screenshot(p7_html, p8_png)
        print(f"[+] Captured: {p7_png}")
        print(f"[+] Captured: {p8_png}")

        # -------------------------------------------------------------
        # 9. Transfer History Audit Page
        # -------------------------------------------------------------
        resp = client.get('/history')
        p9_html = os.path.join(TEMP_HTML_DIR, "09_transfer_history.html")
        with open(p9_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p9_png = os.path.join(SCREENSHOTS_DIR, "09_transfer_history.png")
        take_chrome_screenshot(p9_html, p9_png)
        print(f"[+] Captured: {p9_png}")

        # -------------------------------------------------------------
        # 10. Security Information Page
        # -------------------------------------------------------------
        resp = client.get('/security')
        p10_html = os.path.join(TEMP_HTML_DIR, "10_security_information_page.html")
        with open(p10_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p10_png = os.path.join(SCREENSHOTS_DIR, "10_security_information_page.png")
        take_chrome_screenshot(p10_html, p10_png, window_size="1280,1100")
        print(f"[+] Captured: {p10_png}")

        # -------------------------------------------------------------
        # 11. Profile & PKI Identity Page
        # -------------------------------------------------------------
        resp = client.get('/profile')
        p11_html = os.path.join(TEMP_HTML_DIR, "11_pki_profile.html")
        with open(p11_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p11_png = os.path.join(SCREENSHOTS_DIR, "11_pki_profile.png")
        take_chrome_screenshot(p11_html, p11_png)
        print(f"[+] Captured: {p11_png}")

        # -------------------------------------------------------------
        # 12. Ciphertext Tamper Attack Alert (Simulate tampering on transfer #2)
        # -------------------------------------------------------------
        client.post(f'/tamper/{t2_id}')
        # Bob attempts to decrypt transfer #2
        resp = client.post(f'/decrypt/{t2_id}', data={"password": "BobMasterPassword2026!"})
        p12_html = os.path.join(TEMP_HTML_DIR, "12_ciphertext_tamper_alert.html")
        with open(p12_html, "w", encoding="utf-8") as f:
            f.write(inject_base_url(resp.data))
        p12_png = os.path.join(SCREENSHOTS_DIR, "12_ciphertext_tamper_alert.png")
        take_chrome_screenshot(p12_html, p12_png)
        print(f"[+] Captured: {p12_png}")

        # Sync all screenshots to docs/screenshots as well
        import shutil
        for filename in os.listdir(SCREENSHOTS_DIR):
            if filename.endswith(".png"):
                src = os.path.join(SCREENSHOTS_DIR, filename)
                dst = os.path.join(DOCS_SCREENSHOTS_DIR, filename)
                shutil.copyfile(src, dst)

    print("[*] All 12 real application screenshots captured successfully from actual running Flask application!")

if __name__ == "__main__":
    run_capture_pipeline()
