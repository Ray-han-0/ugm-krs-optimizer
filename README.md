# UGM KRS Optimizer

Penyusun Jadwal Kuliah Otomatis Bebas Bentrok (CSP Solver) - Capstone Project Ilmu Komputer UGM

Proyek Capstone Mandiri Mahasiswa Departemen Ilmu Komputer dan Elektronika (DIKE), Fakultas MIPA, Universitas Gadjah Mada (UGM).

---

## Prinsip Desain
- **Zero-Bureaucracy & 100% Student Control**: Dapat dijalankan sepenuhnya secara lokal tanpa ketergantungan pada izin birokrasi, MoU instansi, atau API berbayar.
- **Academic Rigor**: Dilengkapi dengan pengujian otomatis (*unit & integration tests*) dan laporan teknis komprehensif berstandar akademik.

---

## Dokumen Laporan Capstone (Lengkap Bab I - V)
Laporan teknis lengkap (Bab 1 Pendahuluan, Bab 2 Landasan Teori, Bab 3 Perancangan Sistem, Bab 4 Implementasi & Evaluasi, Bab 5 Kesimpulan, serta Daftar Pustaka IEEE/APA) tersedia dalam format PDF:
- [Lihat Berkas Laporan PDF (8 Halaman)](reports/Laporan_Modul_01_KRS_Optimizer.pdf)

Untuk mengompilasi ulang laporan teknis PDF secara lokal:
```bash
python generate_report.py
```

---

## Cara Menjalankan Aplikasi

### 1. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Antarmuka / CLI
```bash
python cli.py --help
```

### 3. Menjalankan Rangkaian Pengujian
```bash
python -m unittest discover -v
```

---

## Lisensi
Proyek Akademik Capstone - Ilmu Komputer UGM.
