# 📄 Smart Doc Scanner

Aplikasi scan dokumen dari kamera smartphone — mirip **CamScanner** / **vFlat Scanner** — dibuat dengan **Python + Streamlit + OpenCV**, dan bisa dihosting **gratis** di GitHub + Streamlit Community Cloud.

## ✨ Fitur

- 📷 Ambil foto langsung dari kamera HP lewat browser (tidak perlu install apa-apa)
- 🤖 **Deteksi otomatis tepi dokumen** + perspective correction (dokumen otomatis "diratakan" seperti hasil scan)
- 🎨 Filter hasil: Warna Asli, Ditingkatkan (Auto/CLAHE), Abu-abu, Hitam-Putih ala dokumen
- ↺↻ Rotasi manual jika foto miring
- 👀 **Preview sebelum disimpan** — jika hasil belum pas, tinggal klik **Scan Ulang**
- 📚 Multi-halaman: kumpulkan beberapa halaman lalu unduh sekaligus
- ⬇️ Ekspor ke **PDF** atau **ZIP gambar**
- 📱 UI responsif, dioptimalkan untuk layar smartphone

## 🗂️ Struktur Project

```
scanner-app/
├── app.py                 # Aplikasi utama Streamlit
├── scanner_utils.py        # Logika deteksi tepi & pemrosesan citra (OpenCV)
├── requirements.txt        # Dependensi Python
├── packages.txt             # Dependensi sistem (untuk Streamlit Cloud)
├── .streamlit/config.toml  # Tema & konfigurasi Streamlit
└── .gitignore
```

## 🚀 Menjalankan di Lokal

Pastikan Python 3.9+ terpasang.

```bash
# 1. Clone repo
git clone https://github.com/USERNAME/scanner-app.git
cd scanner-app

# 2. (opsional) buat virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependensi
pip install -r requirements.txt

# 4. Jalankan aplikasi
streamlit run app.py
```

Buka `http://localhost:8501` di browser. Untuk akses dari HP di jaringan yang sama, gunakan alamat IP lokal komputer, contoh: `http://192.168.1.10:8501`.

> ⚠️ Fitur kamera browser (`st.camera_input`) membutuhkan koneksi **HTTPS** atau **localhost**. Saat sudah dideploy ke Streamlit Cloud, koneksinya otomatis HTTPS sehingga kamera HP bisa diakses dengan aman.

## ☁️ Deploy ke GitHub + Streamlit Cloud (Gratis)

### 1. Push ke GitHub

```bash
git init
git add .
git commit -m "Initial commit: Smart Doc Scanner"
git branch -M main
git remote add origin https://github.com/USERNAME/scanner-app.git
git push -u origin main
```

### 2. Deploy di Streamlit Community Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io) dan login dengan akun GitHub.
2. Klik **"New app"**.
3. Pilih repository `scanner-app`, branch `main`, dan file utama `app.py`.
4. Klik **Deploy**.
5. Tunggu proses build selesai — aplikasi akan mendapat URL publik seperti:
   `https://scanner-app-xxxxx.streamlit.app`

### 3. Akses dari Smartphone

- Buka URL Streamlit Cloud tadi langsung di browser HP (Chrome/Safari).
- Izinkan akses kamera saat diminta.
- (Opsional) Tambahkan ke **Home Screen** dari menu browser agar terasa seperti aplikasi native.

## 📱 Cara Pakai

1. **Ambil Foto** — arahkan kamera ke dokumen, pastikan semua sisi kertas terlihat & pencahayaan cukup.
2. **Tinjau Hasil** — aplikasi otomatis mendeteksi tepi dokumen dan meratakan perspektifnya. Pilih filter yang diinginkan, putar jika perlu.
3. Jika hasil belum sesuai → klik **🔄 Scan Ulang** untuk memfoto ulang.
4. Jika sudah sesuai → klik **✅ Simpan Halaman Ini**.
5. Ulangi untuk halaman berikutnya (multi-halaman didukung).
6. Klik **⬇️ Unduh PDF** atau **⬇️ Unduh ZIP** untuk menyimpan hasil akhir.

## 🛠️ Tips Hasil Scan Lebih Rapi

- Gunakan alas/latar belakang gelap & polos agar tepi kertas lebih mudah terdeteksi.
- Pastikan pencahayaan merata, hindari bayangan tajam di atas dokumen.
- Jika deteksi otomatis gagal, gunakan mode **"✋ Gunakan foto penuh (tanpa crop)"** sebagai cadangan.

## 🧩 Teknologi

- [Streamlit](https://streamlit.io/) — UI web & hosting
- [OpenCV](https://opencv.org/) — deteksi tepi & perspective transform
- [Pillow](https://python-pillow.org/) — pemrosesan gambar
- [img2pdf](https://pypi.org/project/img2pdf/) — ekspor PDF

## 📄 Lisensi

Bebas digunakan dan dimodifikasi untuk keperluan pribadi maupun proyek lain.
