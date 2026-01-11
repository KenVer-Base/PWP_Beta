# 🐦 Whistle - Social Media Platform

**Whistle** adalah aplikasi media sosial sederhana mirip Twitter/X yang dibangun menggunakan **Python Flask**.  
Proyek ini berfokus pada interaksi pengguna secara **real-time** (Chat & Notifikasi) serta pengalaman pengguna yang mulus tanpa *reload* halaman berlebih menggunakan **AJAX**.

> Dibuat sebagai **Proyek Perkuliahan Pemrograman Web**

---

## ✨ Fitur Utama

### 1. Linimasa & Posting
- **Postingan Multimedia**: Mendukung teks, gambar, dan video
- **Explore & Following**:
  - *Explore* → semua postingan global  
  - *Home* → postingan dari user yang diikuti
- **Hashtag & Mention**: Mendukung format teks kaya (*rich text*) sederhana

### 2. Interaksi Pengguna (AJAX)
- **Like tanpa Reload** menggunakan Fetch API
- **Komentar Real-time** tanpa refresh halaman
- **Follow / Unfollow** pengguna lain

### 3. Real-time Chat (Socket.IO) 💬
- **Private Messaging** antar pengguna
- **Live Chat Bubble** tanpa refresh
- **Smart Sorting** berdasarkan pesan terbaru
- **Unread Indicator** (badge merah)
- **Mutual Filter** (prioritas user yang saling follow)

### 4. Profil & Personalisasi
- Foto profil, banner/cover, dan bio
- **Auto Avatar** dari `ui-avatars.com` jika user tidak upload foto
- Edit profil & pengaturan akun

---

## 🛠️ Teknologi yang Digunakan

### Backend
- Python 3.x
- Flask
- Flask-SocketIO
- Flask-MySQLdb

### Frontend
- HTML5, CSS3
- JavaScript (Vanilla JS + Fetch API)
- Bootstrap 5
- Bootstrap Icons

### Database
- MySQL 

---

## 🚀 Cara Instalasi & Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/username/whistle-clone.git
cd whistle-clone
```

### 2. Buat Virtual Environment
```bash
python -m venv env
.\env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Database
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'whistle_db'
```

### 5. Jalankan Aplikasi
```bash
python run.py
```

Akses aplikasi:
http://127.0.0.1:5000

---

## 📡 Dokumentasi API & Socket

### AJAX Endpoint

| Method | Endpoint |
|------|---------|
| POST | /like/<post_id> |
| POST | /comment/<post_id> |

### Socket.IO Events

| Event | Arah |
|------|------|
| join | Client → Server |
| send_message | Client → Server |
| receive_message | Server → Client |

---

## 👤 Author

**Faqih Al Bashori**  
Mahasiswa Informatika  
Universitas Teknologi Yogyakarta (2024)

Dibuat dengan ❤️ dan kopi ☕
