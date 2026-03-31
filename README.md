# End-to-End Secure Message Delivery
## II3230 - Keamanan Informasi
Oleh:
1. Favian Rafi Laftiyanto / 18223036
2. Ahmad Evander Ruizhi Xavier / 18223064 

Proyek ini adalah implementasi dari tugas Keamanan Informasi yang menyimulasikan pengiriman pesan aman secara *end-to-end* menggunakan pendekatan kriptografi hibrida (*Digital Envelope*). Aplikasi dibangun menggunakan **Python Socket Programming** dengan antarmuka GUI sederhana berbasis **Tkinter**.

## Fitur Kriptografi yang Digunakan
Skenario ini mengamankan *plaintext* menggunakan kombinasi algoritma standar industri:
1. **Symmetric Encryption:** AES-256-CBC (untuk mengenkripsi isi pesan).
2. **Asymmetric Encryption:** RSA-2048 dengan OAEP (untuk mengenkripsi kunci AES).
3. **Hash Function:** SHA-256 (untuk memverifikasi integritas pesan).
4. **Digital Signature:** RSA-PSS (untuk autentikasi dan *non-repudiation* pengirim).

## Struktur File
* `keygen.py` : Script untuk menghasilkan pasangan kunci publik dan privat (RSA) untuk Alice dan Bob.
* `alice_gui.py` : Aplikasi *Client* (Pengirim) yang melakukan proses enkripsi, *hashing*, *signing*, dan mengirim *payload* JSON.
* `bob_gui.py` : Aplikasi *Server* (Penerima) yang mendengarkan koneksi masuk, mendekripsi paket, dan melakukan verifikasi keamanan.
* `alice_private.pem` : Private Key Alice
* `alice_public.pem` : Public Key Alice
* `bob_private.pem` : Private Key Bob
* `bob_public.pem` : Public Key Bob


## Persyaratan Sistem (Prerequisites)
Pastikan Anda telah menginstal **Python 3.x** di sistem Anda. Proyek ini sangat bergantung pada pustaka `cryptography`. 

Instal pustaka yang dibutuhkan menggunakan perintah berikut di terminal/CMD:
```bash
pip install cryptography
```
### Cara Menjalankan Program
#### 1: Generate RSA Keys
Sebelum memulai komunikasi, kita harus membuat Kunci Publik dan Kunci Privat untuk Alice dan Bob (Jika tidak menggunakan key *default* yang terdapat pada repositori).

Buka terminal/CMD di direktori proyek ini.

Jalankan perintah:

```Bash
python keygen.py
```
Pastikan 4 file .pem (alice_private.pem, alice_public.pem, bob_private.pem, bob_public.pem) berhasil terbuat di dalam folder yang sama. (Langkah ini cukup dilakukan satu kali saja).

#### 2: Jalankan Bob (Penerima / Server)
Bob harus dijalankan terlebih dahulu agar socket siap menerima (listening) koneksi dari Alice.

Buka terminal baru.

Jalankan perintah:

```Bash
python bob_gui.py
```
Jendela GUI Bob akan muncul dengan status "Menunggu koneksi dari Alice...". Biarkan jendela ini tetap terbuka.

#### 3: Jalankan Alice (Pengirim / Client)
Setelah Bob siap, kita jalankan aplikasi Alice untuk mengirim pesan.

Buka terminal baru (biarkan terminal Bob tetap berjalan).

Jalankan perintah:

```Bash
python alice_gui.py
```
Jendela GUI Alice akan muncul.

Ketikkan pesan rahasia pada kolom teks yang disediakan, lalu klik tombol "Kirim Terenkripsi".

### Hasil yang Diharapkan
Pada GUI Alice, Anda akan melihat log proses kriptografi (Step 1 hingga Step 5) beserta komponen Base64 yang dibungkus ke dalam JSON.

Pada GUI Bob, secara real-time Anda akan melihat log penerimaan data, proses dekripsi kunci, dekripsi pesan, hingga hasil akhir Verifikasi Hash (VALID) dan Verifikasi Digital Signature (VALID). Pesan asli akan terbaca kembali di layar Bob.