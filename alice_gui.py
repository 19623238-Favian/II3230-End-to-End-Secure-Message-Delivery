import socket
import json
import base64
import tkinter as tk
from tkinter import scrolledtext
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class AliceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alice - Secure Sender")
        
        # UI Elements
        tk.Label(root, text="Pesan Plaintext:").pack(pady=5)
        self.entry_msg = tk.Entry(root, width=50)
        self.entry_msg.pack(pady=5)
        self.entry_msg.insert(0, "Halo Bob, ini pesan rahasia!")

        self.btn_send = tk.Button(root, text="Kirim Terenkripsi", command=self.send_secure_message, bg="green", fg="white")
        self.btn_send.pack(pady=10)

        tk.Label(root, text="Detail Proses Kriptografi:").pack(pady=5)
        self.log_area = scrolledtext.ScrolledText(root, width=60, height=20)
        self.log_area.pack(pady=5)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def send_secure_message(self):
        try:
            plaintext = self.entry_msg.get().encode()
            self.log_area.delete(1.0, tk.END)
            self.log("--- MEMULAI PROSES PENGIRIMAN ---")

            # 1. AES Key Generation
            aes_key = os.urandom(32)
            iv = os.urandom(16)
            self.log(f"[STEP 1] Membuat AES-256 Key: {aes_key.hex()[:20]}...")

            # 2. Symmetric Encryption (AES-CBC)
            pad_len = 16 - (len(plaintext) % 16)
            padded_plaintext = plaintext + bytes([pad_len] * pad_len)
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            self.log(f"[STEP 2] Ciphertext: {base64.b64encode(ciphertext).decode()[:30]}...")

            # 3. Encrypt AES Key with Bob's Public Key
            with open("bob_public.pem", "rb") as f:
                bob_pub = serialization.load_pem_public_key(f.read())
            enc_key = bob_pub.encrypt(
                aes_key,
                padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            self.log("[STEP 3] AES Key telah dienkripsi dengan RSA Public Key Bob.")

            # 4. Hashing
            digest = hashes.Hash(hashes.SHA256())
            digest.update(plaintext)
            msg_hash = digest.finalize()
            self.log(f"[STEP 4] Hash SHA-256: {msg_hash.hex()}")

            # 5. Digital Signature
            with open("alice_private.pem", "rb") as f:
                alice_priv = serialization.load_pem_private_key(f.read(), password=None)
            sig = alice_priv.sign(
                msg_hash,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            self.log("[STEP 5] Digital Signature berhasil dibuat dengan Private Key Alice.")

            # 6. Socket Sending
            payload = {
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "iv": base64.b64encode(iv).decode(),
                "encrypted_key": base64.b64encode(enc_key).decode(),
                "hash": base64.b64encode(msg_hash).decode(),
                "signature": base64.b64encode(sig).decode()
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 5005))
                s.sendall(json.dumps(payload).encode())
            
            self.log("\n[SUCCESS] Payload berhasil dikirim ke IP Bob!")
            
        except Exception as e:
            self.log(f"\n[ERROR] {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AliceGUI(root)
    root.mainloop()