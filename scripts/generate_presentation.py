import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    pptx_path = os.path.join(docs_dir, "SecureLink_Presentation.pptx")
    diagrams_dir = os.path.join(docs_dir, "diagrams")
    screenshots_dir = os.path.join(docs_dir, "screenshots")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Color Palette
    COLOR_BG = RGBColor(11, 15, 25)        # #0B0F19 Dark Navy/Charcoal
    COLOR_CARD = RGBColor(22, 32, 50)      # #162032 Surface Card
    COLOR_CARD_BORDER = RGBColor(36, 52, 77)
    COLOR_CYAN = RGBColor(0, 240, 255)     # #00F0FF Neon Cyan
    COLOR_BLUE = RGBColor(56, 189, 248)    # #38BDF8 Sky Blue
    COLOR_GREEN = RGBColor(16, 185, 129)   # #10B981 Emerald
    COLOR_PURPLE = RGBColor(129, 140, 248) # #818CF8 Indigo
    COLOR_WHITE = RGBColor(241, 245, 249)  # Text main
    COLOR_MUTED = RGBColor(148, 163, 184)  # Text secondary

    def set_slide_background(slide):
        bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = COLOR_BG
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(slide, title_text, category_text="DATA NETWORK SECURITY"):
        # Category pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_CYAN

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11), Inches(0.8))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE

    def add_card(slide, left, top, width, height, title="", body_bullets=None, border_color=COLOR_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)

        if title:
            p_head = tf.paragraphs[0]
            p_head.text = title
            p_head.font.size = Pt(14)
            p_head.font.bold = True
            p_head.font.color.rgb = COLOR_CYAN
            p_head.space_after = Pt(8)

        if body_bullets:
            for i, b in enumerate(body_bullets):
                p = tf.add_paragraph() if (title or i > 0) else tf.paragraphs[0]
                p.text = f"•  {b}"
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_MUTED
                p.space_after = Pt(6)

        return card

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "COLLEGE ACADEMIC MINI-PROJECT  •  DATA NETWORK SECURITY"
    p_badge.font.size = Pt(12)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_CYAN
    p_badge.space_after = Pt(12)

    p_main = tf1.add_paragraph()
    p_main.text = "SecureLink: Hybrid Cryptography File Transfer System"
    p_main.font.size = Pt(32)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_WHITE
    p_main.space_after = Pt(14)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Defense-in-Depth Confidentiality, Authenticity, and Verifiable Data Integrity\nCombining AES-256-GCM, RSA-3072 OAEP, and SHA-256 Hashing"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_MUTED

    # Meta card
    add_card(s1, Inches(1.0), Inches(4.7), Inches(11.3), Inches(1.8),
             title="Academic Presentation Credentials",
             body_bullets=[
                 "Course: CS-DNS-502 | Data Network Security (B.Tech / B.E. Computer Science & Engineering)",
                 "Technologies: Python 3, Flask, Cryptography (OpenSSL Libcrypto), SQLite3, HTML5/CSS3",
                 "Candidate: [Student Name Placeholder]  |  Roll No: [Register Number Placeholder]  |  Academic Year: 2025–2026"
             ],
             border_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 2: Introduction
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Introduction & Network Security Domain Overview")

    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="The Need for Confidential Transfer",
             body_bullets=[
                 "Network transmission across public LANs, WANs, and Wi-Fi leaves files exposed to passive packet sniffing and interception.",
                 "Traditional protocols (FTP, unencrypted HTTP, shared folders) provide zero protection against active eavesdroppers.",
                 "Symmetric cryptography (AES) offers high-throughput encryption but suffers from the Key Distribution Dilemma.",
                 "Asymmetric cryptography (RSA) solves key exchange via public keys but is too slow for bulk multi-megabyte payloads.",
                 "SecureLink bridges this gap using Hybrid Cryptography."
             ])

    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="SecureLink Core Architectural Pillars",
             body_bullets=[
                 "Bulk Payload Encryption: AES-256-GCM authenticated cipher with 96-bit random nonces.",
                 "Key Encapsulation (KEM): RSA-3072 with Optimal Asymmetric Encryption Padding (OAEP) and SHA-256 MGF1.",
                 "Dual-Layer Integrity Verification: 128-bit GHASH authentication tag + SHA-256 constant-time hash verification.",
                 "Zero-Plaintext Storage: Server stores only ciphertext; AES keys are encrypted with receiver's public key.",
                 "Private Key Protection at Rest: PKCS#8 encrypted with user master password via PBKDF2/scrypt."
             ],
             border_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 3: Problem Statement
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Problem Statement & Primary Threat Vectors")

    threats = [
        ("Passive Eavesdropping", [
            "Attackers sniffing network packets on Wi-Fi or router switches can capture raw unencrypted file bytes.",
            "Solution: AES-256-GCM bulk payload encryption renders all packets indecipherable without the session key."
        ], COLOR_BLUE),
        ("Key Distribution Bottleneck", [
            "How do two parties agree on a shared 256-bit symmetric key over an insecure transmission medium?",
            "Solution: Asymmetric RSA-3072 public-key encapsulation encrypts the session key uniquely for the receiver."
        ], COLOR_PURPLE),
        ("Active Bit-Flipping & Tampering", [
            "Unauthenticated ciphers (AES-CBC) allow adversaries to tamper with ciphertext without detection.",
            "Solution: AES-256-GCM calculates a 128-bit GHASH tag. Even 1 altered bit causes instant decryption abort."
        ], COLOR_GREEN),
        ("Server-Side Inode Compromise", [
            "If the central server storage is leaked or accessed by a rogue admin, stored files are vulnerable.",
            "Solution: Zero-plaintext server policy. Only ciphertext and wrapped keys are retained on disk."
        ], COLOR_CYAN)
    ]

    for idx, (title, bullets, b_col) in enumerate(threats):
        x = Inches(0.8 + (idx % 2) * 6.0)
        y = Inches(1.8 + (idx // 2) * 2.6)
        add_card(s3, x, y, Inches(5.6), Inches(2.3), title=title, body_bullets=bullets, border_color=b_col)

    # =========================================================================
    # SLIDE 4: Objectives
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Project Objectives & Design Mandates")

    objs = [
        ("1. Real-World Hybrid Crypto", "Implement true hybrid cryptography where files are encrypted using symmetric AES-256-GCM and session keys are encapsulated using RSA-3072."),
        ("2. Authenticated Integrity", "Provide mathematical proof of file authenticity through 128-bit GHASH tags and pre/post-decryption SHA-256 hash comparisons."),
        ("3. Granular Access Control", "Enforce strict receiver-only decryption rights. An unauthorized user cannot unlock someone else's file even if authenticated."),
        ("4. Zero Plaintext Inode Storage", "Ensure unencrypted files and raw symmetric keys are immediately purged from server memory upon dispatch."),
        ("5. Academic Attack Simulation Lab", "Equip students and evaluators with a live tamper demonstration button to simulate active attacks and observe GCM tag rejection."),
        ("6. Standards Compliance", "Comply with NIST SP 800-57, FIPS 140-3, and RFC 8017 guidelines for long-term cryptographic equivalence beyond 2030.")
    ]

    for idx, (head, desc) in enumerate(objs):
        x = Inches(0.8 + (idx % 2) * 6.0)
        y = Inches(1.8 + (idx // 2) * 1.7)
        add_card(s4, x, y, Inches(5.6), Inches(1.5), title=head, body_bullets=[desc])

    # =========================================================================
    # SLIDE 5: Existing vs Proposed System
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Comparative Analysis: Conventional vs. SecureLink")

    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="Conventional File Transfer Systems",
             body_bullets=[
                 "Cipher Mode: Uses legacy unauthenticated modes (AES-CBC or ECB) vulnerable to padding oracle attacks.",
                 "Key Exchange: Manual pre-shared passwords sent over email, chat, or phone, introducing human vulnerability.",
                 "Integrity Check: Relies on simple CRC32 checksums easily forged by an adversary.",
                 "Server Storage: Files stored in plaintext or with a single server master key vulnerable to insider breach.",
                 "Tamper Detection: Corruptions only noticed after opening or executing the corrupted file.",
                 "Demonstration: Static code with no dynamic attack simulation capability."
             ],
             border_color=RGBColor(244, 63, 94))

    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="SecureLink Proposed Architecture",
             body_bullets=[
                 "Cipher Mode: Modern AES-256-GCM (AEAD) combining counter encryption with 128-bit GHASH authentication.",
                 "Key Exchange: Automated Public Key Infrastructure (PKI) using RSA-3072 with OAEP padding.",
                 "Integrity Check: Dual-layer defense: GCM GHASH tag verification + SHA-256 constant-time comparison.",
                 "Server Storage: Zero-Plaintext storage. Server holds only ciphertext; keys are wrapped with receiver's public key.",
                 "Tamper Detection: Instant cryptographic abort upon 1-bit alteration via InvalidTag exception.",
                 "Demonstration: Interactive academic attack simulation workbench for live college viva demonstrations."
             ],
             border_color=COLOR_GREEN)

    # =========================================================================
    # SLIDE 6: System Architecture Diagram
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "System Architecture & Cryptographic Flow")

    arch_img = os.path.join(diagrams_dir, "hybrid_crypto_architecture.png")
    if os.path.exists(arch_img):
        s6.shapes.add_picture(arch_img, Inches(0.8), Inches(1.6), Inches(8.0), Inches(5.2))

    add_card(s6, Inches(9.1), Inches(1.6), Inches(3.4), Inches(5.2),
             title="Architecture Highlights",
             body_bullets=[
                 "Modular 5-tier architecture: Presentation, Controller, Cryptography, Storage, Database.",
                 "Plaintext never written to permanent disk.",
                 "AES session key generated fresh per transmission.",
                 "RSA-3072 wraps only the 32-byte AES key.",
                 "Receiver unlocks private key with master password.",
                 "GCM tag check precedes file release."
             ],
             border_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 7: Hybrid Cryptography Workflow
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Step-by-Step Hybrid Cryptography Workflow")

    steps = [
        ("Step 1: Hash Ingestion", "Sender uploads file. SHA-256 digest is computed from streaming plaintext bytes for post-decryption comparison."),
        ("Step 2: Ephemeral AES Key", "256-bit AES key and 96-bit nonce are randomly generated using CSPRNG. Nonce is unique per file."),
        ("Step 3: AES-256-GCM Encrypt", "File payload is encrypted using AES-GCM. Produces ciphertext and a 128-bit GHASH authentication tag."),
        ("Step 4: RSA-OAEP Key Wrap", "Receiver's RSA-3072 public key is retrieved from SQLite. Ephemeral AES key is encrypted via RSA-OAEP (SHA-256)."),
        ("Step 5: Zero-Plaintext Commit", "Ciphertext saved to disk. Wrapped AES key, nonce, tag, and SHA-256 stored in DB. Plaintext purged from RAM."),
        ("Step 6: Decrypt & Verify", "Receiver unlocks RSA private key with password, decapsulates AES key, decrypts ciphertext, validates GCM tag, and verifies SHA-256.")
    ]

    for idx, (head, desc) in enumerate(steps):
        x = Inches(0.8 + (idx % 3) * 4.0)
        y = Inches(1.8 + (idx // 3) * 2.6)
        add_card(s7, x, y, Inches(3.7), Inches(2.3), title=head, body_bullets=[desc], border_color=COLOR_BLUE)

    # =========================================================================
    # SLIDE 8: AES-256-GCM Implementation
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "AES-256-GCM Authenticated Encryption Deep Dive")

    gcm_img = os.path.join(diagrams_dir, "aes_gcm_internals.png")
    if os.path.exists(gcm_img):
        s8.shapes.add_picture(gcm_img, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.0))

    add_card(s8, Inches(8.6), Inches(1.6), Inches(3.9), Inches(5.2),
             title="Key Cryptographic Parameters",
             body_bullets=[
                 "Key Size: 256 bits (32 bytes) providing 128-bit quantum security level against Grover's algorithm.",
                 "Nonce (IV): 96 bits (12 bytes) CSPRNG random. Prevents keystream reuse attacks.",
                 "CTR Mode Keystream: S_i = CIPH_k(Nonce || counter_i). Extremely fast, hardware-accelerated.",
                 "GHASH Tag: 128 bits (16 bytes) computed over binary Galois field GF(2^128).",
                 "Associated Data: Binds original filename to authentication tag, preventing filename spoofing."
             ],
             border_color=COLOR_GREEN)

    # Bottom summary box on slide 8
    add_card(s8, Inches(0.8), Inches(5.8), Inches(7.5), Inches(1.0),
             title="Why GCM over CBC?",
             body_bullets=["AES-GCM combines encryption and authentication in a single pass without needing a separate HMAC."],
             border_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 9: RSA-3072 and SHA-256
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Asymmetric RSA-3072 & SHA-256 Integrity Verification")

    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="RSA-3072 with OAEP Padding",
             body_bullets=[
                 "Modulus Size: 3072 bits (two 1536-bit prime factors).",
                 "Security Equivalence: 128-bit security level per NIST SP 800-57 (RSA-2048 only offers 112 bits).",
                 "Public Exponent: e = 65537 (2^16 + 1) for rapid encryption while preventing low-exponent attacks.",
                 "OAEP Padding: Optimal Asymmetric Encryption Padding with SHA-256 MGF1 renders cipher IND-CCA2 secure.",
                 "Private Key Protection: Stored encrypted via PKCS#8 AES-256-CBC using PBKDF2 salt and user master password."
             ],
             border_color=COLOR_PURPLE)

    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="SHA-256 Integrity vs. GCM Tag",
             body_bullets=[
                 "SHA-256 Role: Unkeyed one-way cryptographic digest computed over raw plaintext bytes.",
                 "Pre-Encryption Hash: Stored in transfer metadata upon upload.",
                 "Post-Decryption Hash: Recomputed after successful AES-GCM decryption.",
                 "Constant-Time Verification: Compared using hmac.compare_digest to prevent side-channel timing attacks.",
                 "Crucial Distinction: GCM tag verifies ciphertext authenticity; SHA-256 verifies plaintext file integrity."
             ],
             border_color=COLOR_GREEN)

    # =========================================================================
    # SLIDE 10: Application Features
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Application Modules & Defensive Security Hardening")

    feats = [
        ("Authentication & Rate Limiting", [
            "Salted password hashing via Werkzeug (scrypt/PBKDF2).",
            "Automatic IP and username rate-limiting (lockout after 5 failed attempts in 10 minutes)."
        ]),
        ("Relational SQLite PKI Schema", [
            "Stores public keys in SubjectPublicKeyInfo PEM format.",
            "Stores private keys in PKCS#8 encrypted format.",
            "Strict foreign keys and cascade delete rules."
        ]),
        ("Zero-Plaintext Server Policy", [
            "Server disk only contains high-entropy ciphertext files.",
            "AES keys are never retained unencrypted on server disk.",
            "Plaintext and raw keys wiped from memory on dispatch."
        ]),
        ("Interactive Attack Simulation Lab", [
            "Demonstration feature allows intentionally modifying bytes on server disk.",
            "Receiver attempt immediately triggers InvalidTag alert, proving GCM tamper defense."
        ])
    ]

    for idx, (title, bullets) in enumerate(feats):
        x = Inches(0.8 + (idx % 2) * 6.0)
        y = Inches(1.8 + (idx // 2) * 2.6)
        add_card(s10, x, y, Inches(5.6), Inches(2.3), title=title, body_bullets=bullets, border_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 11: Screenshots and Demonstration
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Live Application Interfaces & Demonstration")

    dash_shot = os.path.join(screenshots_dir, "03_dashboard.png")
    if os.path.exists(dash_shot):
        s11.shapes.add_picture(dash_shot, Inches(0.8), Inches(1.8), Inches(5.6), Inches(3.4))

    dec_shot = os.path.join(screenshots_dir, "07_successful_decryption.png")
    if os.path.exists(dec_shot):
        s11.shapes.add_picture(dec_shot, Inches(6.8), Inches(1.8), Inches(5.6), Inches(3.4))

    add_card(s11, Inches(0.8), Inches(5.4), Inches(11.6), Inches(1.5),
             title="Demonstration Workflow for Academic Evaluators",
             body_bullets=[
                 "1. Register Alice and Bob -> Observe automated RSA-3072 key pair generation and public key registration.",
                 "2. Alice uploads and encrypts 'confidential_report.pdf' -> Inspect storage/encrypted/ to confirm zero-plaintext ciphertext.",
                 "3. Bob logs in, provides master password -> AES key is recovered, GCM tag validated, SHA-256 match confirmed.",
                 "4. Click 'Simulate Ciphertext Tampering Attack' -> Decrypt again -> Observe immediate InvalidTag security rejection!"
             ],
             border_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 12: Testing and Results
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Automated Testing Suite & Experimental Results")

    add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="Pytest Test Suite Summary",
             body_bullets=[
                 "Total Automated Test Cases: 25 tests executed.",
                 "Test Pass Rate: 100% (25 passed, 0 failed).",
                 "Execution Runtime: 7.56 seconds on Python 3.14.",
                 "AES Cryptographic Unit Tests: Key generation, nonce randomness, wrong key rejection, 1-bit flip tamper detection.",
                 "RSA Asymmetric Unit Tests: Key pair generation, PKCS#8 password encryption, OAEP encapsulation, wrong key failure.",
                 "SHA-256 Hash Tests: Byte hashing against known NIST test vectors, constant-time comparison."
             ],
             border_color=COLOR_GREEN)

    add_card(s12, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             title="File Compatibility & Security Scenarios",
             body_bullets=[
                 "Plaintext Files (TXT): Verified bit-for-bit fidelity.",
                 "Binary PDF Documents: Preserved structure and digital contents.",
                 "Image Media (PNG / JPG): Recovered full raster payloads intact.",
                 "Formatted Documents (DOCX): Validated ZIP container preservation.",
                 "Large Files (1 MB Archive): High throughput bulk transfer verified.",
                 "Attack Simulation: Corrupted ciphertext in storage successfully triggered AES-GCM InvalidTag rejection.",
                 "Access Control: Verified User C cannot decrypt transmissions between User A and User B."
             ],
             border_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 13: Future Enhancements
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Future Enhancements & Post-Quantum Horizon")

    enhancements = [
        ("Post-Quantum Cryptography (ML-KEM)", [
            "Shor's algorithm on quantum computers will eventually break 3072-bit RSA.",
            "Future roadmap: Migrate from RSA-3072 to NIST-standardized FIPS 203 ML-KEM (Kyber-768/1024) lattice-based KEM."
        ]),
        ("Client-Side WebCrypto Decryption", [
            "Currently, private keys are decrypted briefly in server RAM.",
            "Future roadmap: Decrypt files client-side in the browser using the WebCrypto API, enabling true zero-knowledge transfer."
        ]),
        ("Multi-Recipient Encapsulation", [
            "Enable encrypted group sharing by encapsulating the AES session key with multiple recipient RSA public keys."
        ]),
        ("Decentralized Storage Backends", [
            "Store encrypted ciphertext chunks across distributed storage systems (e.g. IPFS) with zero risk of unauthorized inspection."
        ])
    ]

    for idx, (title, bullets) in enumerate(enhancements):
        x = Inches(0.8 + (idx % 2) * 6.0)
        y = Inches(1.8 + (idx // 2) * 2.6)
        add_card(s13, x, y, Inches(5.6), Inches(2.3), title=title, body_bullets=bullets, border_color=COLOR_BLUE)

    # =========================================================================
    # SLIDE 14: Conclusion and Thank You
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)

    t_box14 = s14.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(2.0))
    tf14 = t_box14.text_frame
    tf14.word_wrap = True

    p_badge14 = tf14.paragraphs[0]
    p_badge14.text = "DATA NETWORK SECURITY MINI-PROJECT"
    p_badge14.font.size = Pt(12)
    p_badge14.font.bold = True
    p_badge14.font.color.rgb = COLOR_CYAN
    p_badge14.space_after = Pt(10)

    p_main14 = tf14.add_paragraph()
    p_main14.text = "Conclusion & Viva Voce Summary"
    p_main14.font.size = Pt(28)
    p_main14.font.bold = True
    p_main14.font.color.rgb = COLOR_WHITE

    add_card(s14, Inches(1.0), Inches(3.2), Inches(11.3), Inches(2.6),
             title="Project Achievements & Summary",
             body_bullets=[
                 "Successfully harmonized AES-256-GCM symmetric speed with RSA-3072 asymmetric key exchange.",
                 "Defeated eavesdropping, key interception, MITM bit-flipping, and server-side data leakage.",
                 "Dual verification with GCM GHASH tag and constant-time SHA-256 comparison proves both authenticity and integrity.",
                 "Passed all 25 automated unit and end-to-end integration tests with 100% success rate.",
                 "Fully functional, demonstrable web application suitable for college academic evaluation and viva voce examination."
             ],
             border_color=COLOR_GREEN)

    t_thank = s14.shapes.add_textbox(Inches(1.0), Inches(6.0), Inches(11.3), Inches(0.8))
    tf_th = t_thank.text_frame
    p_th = tf_th.paragraphs[0]
    p_th.alignment = PP_ALIGN.CENTER
    p_th.text = "Thank You! Questions & Discussion Welcomed."
    p_th.font.size = Pt(18)
    p_th.font.bold = True
    p_th.font.color.rgb = COLOR_CYAN

    prs.save(pptx_path)
    print(f"[+] Successfully compiled PowerPoint Presentation: {pptx_path}")

if __name__ == "__main__":
    build_presentation()

