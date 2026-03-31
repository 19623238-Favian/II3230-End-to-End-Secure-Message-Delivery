import socket
import json
import base64
import threading
import tkinter as tk
from tkinter import scrolledtext
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class BobGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bob - Secure Receiver")

        self.ip = "10.79.89.12"

        tk.Label(root, text="Pesan Masuk (Log Verifikasi):").pack(pady=5)
        self.log_area = scrolledtext.ScrolledText(root, width=65, height=25)
        self.log_area.pack(pady=5)
        
        # Thread untuk listen socket tanpa membekukan GUI
        self.thread = threading.Thread(target=self.start_server, daemon=True)
        self.thread.start()

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 5005))
            s.listen()
            self.log("[*] Menunggu koneksi dari Alice...")
            
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(8192)
                    if data:
                        self.process_incoming(data)

    def process_incoming(self, raw_data):
        try:
            payload = json.loads(raw_data.decode())
            self.log(f"\n--- DATA DITERIMA DARI ALICE {payload['source_ip']} ---")

            # 1. Decrypt AES Key
            with open("bob_private.pem", "rb") as f:
                bob_priv = serialization.load_pem_private_key(f.read(), password=None)
            
            enc_key = base64.b64decode(payload['encrypted_key'])
            aes_key = bob_priv.decrypt(
                enc_key,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            self.log("[STEP 1] AES Key berhasil didekripsi menggunakan Private Key Bob.")
            
            # 2. Decrypt Ciphertext
            ciphertext = base64.b64decode(payload['ciphertext'])
            iv = base64.b64decode(payload['iv'])
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded_pt = decryptor.update(ciphertext) + decryptor.finalize()
            
            pad_len = padded_pt[-1]
            plaintext = padded_pt[:-pad_len]
            self.log(f"[STEP 2] Plaintext Didekripsi: {plaintext.decode()}")

            # 3. Hash Verification
            received_hash = base64.b64decode(payload['hash'])
            digest = hashes.Hash(hashes.SHA256())
            digest.update(plaintext)
            local_hash = digest.finalize()
            print(f"Hash yang dihitung Bob untuk Verifikasi: {base64.b64encode(local_hash).decode()}")
            print(f"Hash yang diterima Bob dari Alice: {base64.b64encode(received_hash).decode()}")
            
            hash_status = "VALID ✅" if local_hash == received_hash else "INVALID ❌"
            self.log(f"[STEP 3] Integritas Pesan (Hash): {hash_status}")

            # 4. Signature Verification
            with open("alice_public.pem", "rb") as f:
                alice_pub = serialization.load_pem_public_key(f.read())
            
            sig = base64.b64decode(payload['signature'])
            try:
                alice_pub.verify(
                    sig, local_hash,
                    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                    hashes.SHA256()
                )
                self.log("[STEP 4] Digital Signature: VALID ✅ (Pesan otentik dari Alice)")
            except:
                self.log("[STEP 4] Digital Signature: INVALID ❌")

        except Exception as e:
            self.log(f"[ERROR] Gagal memproses data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BobGUI(root)
    root.mainloop()