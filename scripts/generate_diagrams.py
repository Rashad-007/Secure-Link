import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_all_diagrams():
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    diagrams_dir = os.path.join(docs_dir, "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)

    # -------------------------------------------------------------
    # Diagram 1: Hybrid Cryptography Architecture Flow
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.axis('off')

    plt.title("SecureLink - Hybrid Cryptography Architecture Flow", 
              fontsize=16, fontweight='bold', color='#00F0FF', pad=20)

    # Boxes styling helper
    def add_box(x, y, w, h, title, subtitle, color, edgecolor='#00F0FF'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", 
                                      facecolor=color, edgecolor=edgecolor, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.62, title, ha='center', va='center', 
                color='#FFFFFF', fontsize=11, fontweight='bold')
        ax.text(x + w/2, y + h*0.32, subtitle, ha='center', va='center', 
                color='#94A3B8', fontsize=8.5)

    # 1. Plaintext File
    add_box(0.04, 0.65, 0.22, 0.18, "Plaintext File", "SHA-256 Pre-Hash Digest", '#162032', '#38BDF8')

    # 2. AES-256-GCM Bulk Encryptor
    add_box(0.38, 0.65, 0.24, 0.18, "AES-256-GCM Engine", "Ephemeral 256-bit Key + 96-bit IV", '#162032', '#00F0FF')

    # 3. Encrypted Ciphertext + Tag
    add_box(0.74, 0.65, 0.22, 0.18, "Zero-Plaintext Storage", "Ciphertext + 128-bit GHASH Tag", '#162032', '#10B981')

    # 4. RSA-3072 Key Wrap (Bottom sender flow)
    add_box(0.38, 0.30, 0.24, 0.18, "RSA-3072 OAEP Wrap", "Receiver Public Key (3072-bit)", '#162032', '#818CF8')

    # 5. Encrypted AES Key
    add_box(0.74, 0.30, 0.22, 0.18, "Wrapped Session Key", "Encrypted with SHA-256 MGF1", '#162032', '#F59E0B')

    # 6. Receiver Decryption
    add_box(0.38, 0.02, 0.58, 0.18, "Receiver Decryption & Integrity Verification", 
            "Private Key Unlocks AES Key -> AES-GCM Verifies Tag -> SHA-256 Match Verification", '#162032', '#00F0FF')

    # Arrows
    arrow_props = dict(arrowstyle="->", color='#00F0FF', lw=2)
    # File to AES
    ax.annotate("", xy=(0.38, 0.74), xytext=(0.26, 0.74), arrowprops=arrow_props)
    ax.text(0.32, 0.76, "Payload", color='#38BDF8', fontsize=8.5, ha='center')

    # AES to Storage
    ax.annotate("", xy=(0.74, 0.74), xytext=(0.62, 0.74), arrowprops=arrow_props)
    ax.text(0.68, 0.76, "Ciphertext", color='#10B981', fontsize=8.5, ha='center')

    # AES to RSA Wrap
    ax.annotate("", xy=(0.50, 0.48), xytext=(0.50, 0.65), arrowprops=arrow_props)
    ax.text(0.51, 0.56, "AES Key", color='#F59E0B', fontsize=8.5)

    # RSA Wrap to Wrapped Key
    ax.annotate("", xy=(0.74, 0.39), xytext=(0.62, 0.39), arrowprops=arrow_props)

    # Wrapped Key to Receiver
    ax.annotate("", xy=(0.85, 0.20), xytext=(0.85, 0.30), arrowprops=arrow_props)

    # Storage to Receiver
    ax.annotate("", xy=(0.80, 0.20), xytext=(0.80, 0.65), 
                arrowprops=dict(arrowstyle="->", color='#10B981', lw=1.5, ls='--'))

    path1 = os.path.join(diagrams_dir, "hybrid_crypto_architecture.png")
    plt.tight_layout()
    plt.savefig(path1, dpi=200, facecolor='#0B0F19')
    plt.close()
    print(f"[+] Generated: {path1}")

    # -------------------------------------------------------------
    # Diagram 2: Database Entity-Relationship Diagram (ERD)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6), facecolor='#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.axis('off')

    plt.title("SecureLink - Relational Database Schema (SQLite)", 
              fontsize=16, fontweight='bold', color='#00F0FF', pad=15)

    # Users Table Card
    u_rect = patches.FancyBboxPatch((0.05, 0.25), 0.38, 0.65, boxstyle="round,pad=0.03", 
                                    facecolor='#162032', edgecolor='#38BDF8', linewidth=1.5)
    ax.add_patch(u_rect)
    ax.text(0.24, 0.84, "TABLE: users", ha='center', color='#38BDF8', fontsize=12, fontweight='bold')
    users_fields = [
        "PK  user_id (INTEGER)",
        "    username (TEXT, UNIQUE)",
        "    email (TEXT, UNIQUE)",
        "    password_hash (TEXT)",
        "    public_key (TEXT, RSA-3072 PEM)",
        "    encrypted_private_key (TEXT, PKCS#8)",
        "    created_at (TIMESTAMP)"
    ]
    for idx, field in enumerate(users_fields):
        ax.text(0.08, 0.77 - idx*0.07, field, color='#E2E8F0', fontsize=9.5, fontfamily='monospace')

    # Transfers Table Card
    t_rect = patches.FancyBboxPatch((0.55, 0.10), 0.40, 0.80, boxstyle="round,pad=0.03", 
                                    facecolor='#162032', edgecolor='#10B981', linewidth=1.5)
    ax.add_patch(t_rect)
    ax.text(0.75, 0.84, "TABLE: transfers", ha='center', color='#10B981', fontsize=12, fontweight='bold')
    trans_fields = [
        "PK  transfer_id (INTEGER)",
        "FK  sender_id -> users(user_id)",
        "FK  receiver_id -> users(user_id)",
        "    original_filename (TEXT)",
        "    encrypted_filename (TEXT)",
        "    file_size (INTEGER)",
        "    encrypted_aes_key (BLOB)",
        "    nonce (BLOB, 96-bit)",
        "    auth_tag (BLOB, 128-bit)",
        "    original_sha256 (TEXT)",
        "    transfer_status (TEXT)",
        "    is_tampered (INTEGER)"
    ]
    for idx, field in enumerate(trans_fields):
        ax.text(0.58, 0.77 - idx*0.055, field, color='#E2E8F0', fontsize=9, fontfamily='monospace')

    # Connecting relation line
    ax.annotate("", xy=(0.55, 0.65), xytext=(0.43, 0.65), 
                arrowprops=dict(arrowstyle="<->", color='#00F0FF', lw=2))
    ax.text(0.49, 0.68, "1 : N (Transfers)", color='#00F0FF', fontsize=9, ha='center', fontweight='bold')

    path2 = os.path.join(diagrams_dir, "database_er_diagram.png")
    plt.tight_layout()
    plt.savefig(path2, dpi=200, facecolor='#0B0F19')
    plt.close()
    print(f"[+] Generated: {path2}")

    # -------------------------------------------------------------
    # Diagram 3: AES-256-GCM Internal Mechanics
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor='#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.axis('off')

    plt.title("AES-256-GCM: Counter (CTR) Mode & Galois Universal Hashing (GHASH)", 
              fontsize=15, fontweight='bold', color='#00F0FF', pad=15)

    def draw_box_simple(x, y, w, h, text, color, border):
        r = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", facecolor=color, edgecolor=border, lw=1.2)
        ax.add_patch(r)
        ax.text(x+w/2, y+h/2, text, ha='center', va='center', color='#FFF', fontsize=9.5, fontweight='bold')

    # Nonce + Counter
    draw_box_simple(0.05, 0.65, 0.25, 0.20, "96-bit Nonce + \n32-bit Counter i", '#162032', '#38BDF8')
    draw_box_simple(0.38, 0.65, 0.24, 0.20, "AES-256 Core\nCIPH_k(Nonce || i)", '#162032', '#00F0FF')
    draw_box_simple(0.70, 0.65, 0.25, 0.20, "Keystream Block\nS_i", '#162032', '#818CF8')

    # Plaintext XOR
    draw_box_simple(0.70, 0.35, 0.25, 0.18, "XOR with Plaintext\nP_i -> C_i", '#162032', '#10B981')
    draw_box_simple(0.20, 0.08, 0.60, 0.18, "GHASH Multiplier over GF(2^128)\nComputes 128-bit Authentication Tag T", '#162032', '#F43F5E')

    # Connectors
    ax.annotate("", xy=(0.38, 0.75), xytext=(0.30, 0.75), arrowprops=arrow_props)
    ax.annotate("", xy=(0.70, 0.75), xytext=(0.62, 0.75), arrowprops=arrow_props)
    ax.annotate("", xy=(0.82, 0.53), xytext=(0.82, 0.65), arrowprops=arrow_props)
    ax.annotate("", xy=(0.82, 0.26), xytext=(0.82, 0.35), arrowprops=arrow_props)

    path3 = os.path.join(diagrams_dir, "aes_gcm_internals.png")
    plt.tight_layout()
    plt.savefig(path3, dpi=200, facecolor='#0B0F19')
    plt.close()
    print(f"[+] Generated: {path3}")

if __name__ == "__main__":
    generate_all_diagrams()

