# 🗳️ Election App - KPU PPI Osaka-Nara

Sistem pemilihan online yang aman dan transparan untuk Komisi Pemilihan Umum PPI Osaka-Nara. Aplikasi ini memungkinkan pemilih melakukan voting secara online dengan sistem token unik yang dikirim via email.

[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## ✨ Fitur Utama

### Untuk Pemilih
- ✅ **Login dengan Token Unik** - Setiap pemilih mendapat token rahasia via email
- ✅ **Voting Aman** - Satu email hanya bisa vote sekali per election
- ✅ **Transparansi** - Lihat kandidat dan visi/misi mereka
- ✅ **Hasil Real-time** - Hasil voting ditampilkan setelah election selesai
- ✅ **Pelaporan Kecurangan** - Fitur untuk melaporkan indikasi fraud

### Untuk Admin (KPU)
- ✅ **Election Management** - Buat dan kelola election dengan mudah
- ✅ **Candidate Management** - Tambah, edit, hapus kandidat
- ✅ **Voter Management** - Import voter dari CSV, generate token otomatis
- ✅ **Email Automation** - Kirim token voting via email secara bulk
- ✅ **Statistics Dashboard** - Monitor jumlah voter, yang sudah vote, dll
- ✅ **Results Control** - Kontrol kapan hasil voting ditampilkan

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐
│   Frontend      │
│   (Vue.js)      │
│   Port: 80/443  │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Nginx  │
    │ Reverse │
    │  Proxy  │
    └────┬────┘
         │
    ┌────┴──────────────┬─────────────┐
    │                   │             │
┌───▼────┐      ┌──────▼──────┐  ┌──▼────────┐
│Backend │      │  Static/    │  │ PostgreSQL│
│Django  │      │  Media Files│  │ Database  │
│Rest API│      │             │  │           │
└────────┘      └─────────────┘  └───────────┘
```

## 🛠️ Tech Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL 15** - Database
- **Gunicorn** - WSGI server
- **Pillow** - Image processing

### Frontend
- **Vue.js 3.5** - Progressive JavaScript framework
- **Vuetify 3** - Material Design component framework
- **Axios** - HTTP client
- **Pinia** - State management
- **Vite** - Build tool

### DevOps
- **Docker & Docker Compose** - Containerization
- **Nginx** - Web server & reverse proxy
- **Let's Encrypt** - SSL/TLS certificates
- **AWS EC2** - Cloud hosting

# Made with ❤️ by xevworks for PPI Osaka-Nara
