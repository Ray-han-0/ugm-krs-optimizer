"""
cli.py - Command Line User Interface for KRS Optimizer
Allows students to optimize course schedules from PDF/Excel/CSV files and export to Google Calendar.
"""

import argparse
import os
import sys
import datetime

# Ensure current module directory is on sys.path
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if CURR_DIR not in sys.path:
    sys.path.insert(0, CURR_DIR)

from models import Course, ClassSection, TimeSlot, SchedulePreference
from parser import parse_schedule_excel, parse_schedule_csv, parse_schedule_pdf
from csp_solver import solve_krs_schedule
from exporter import render_ascii_schedule_matrix, export_to_ics


def get_default_demo_courses():
    return [
        Course(
            code="MII-3101", name="Kecerdasan Buatan", sks=3,
            sections=[
                ClassSection("MII-3101", "Kecerdasan Buatan", "Kelas A", 3, "Dr. Mardhani", "R.301",
                             [TimeSlot("Senin", 8, 0, 9, 40)]),
                ClassSection("MII-3101", "Kecerdasan Buatan", "Kelas B", 3, "Dr. Mardhani", "R.302",
                             [TimeSlot("Rabu", 10, 0, 11, 40)]),
            ]
        ),
        Course(
            code="MII-2104", name="Sistem Operasi", sks=3,
            sections=[
                ClassSection("MII-2104", "Sistem Operasi", "Kelas A", 3, "Prof. Wibowo", "R.201",
                             [TimeSlot("Senin", 8, 30, 10, 10)]),
                ClassSection("MII-2104", "Sistem Operasi", "Kelas B", 3, "Prof. Wibowo", "R.202",
                             [TimeSlot("Kamis", 13, 0, 14, 40)]),
            ]
        ),
        Course(
            code="MII-2201", name="Basis Data", sks=3,
            sections=[
                ClassSection("MII-2201", "Basis Data", "Kelas A", 3, "Ir. Retno, M.Kom.", "R.105",
                             [TimeSlot("Selasa", 10, 0, 11, 40)]),
                ClassSection("MII-2201", "Basis Data", "Kelas B", 3, "Ir. Retno, M.Kom.", "R.106",
                             [TimeSlot("Jumat", 8, 0, 9, 40)]),
            ]
        ),
        Course(
            code="MII-2102", name="Rekayasa Perangkat Lunak", sks=3,
            sections=[
                ClassSection("MII-2102", "Rekayasa Perangkat Lunak", "Kelas A", 3, "Dr. Prasetyo", "R.304",
                             [TimeSlot("Rabu", 13, 0, 14, 40)]),
                ClassSection("MII-2102", "Rekayasa Perangkat Lunak", "Kelas B", 3, "Dr. Prasetyo", "R.305",
                             [TimeSlot("Kamis", 8, 0, 9, 40)]),
            ]
        ),
    ]


def main():
    parser = argparse.ArgumentParser(description="KRS Optimizer - Jadwal Kuliah Bebas Bentrok UGM")
    parser.add_argument("--input", "-i", type=str, help="Jalur berkas masukan (PDF, Excel .xlsx, atau CSV)")
    parser.add_argument("--free-day", type=str, default="Jumat", help="Hari kosong yang diinginkan (misal: Jumat)")
    parser.add_argument("--max-sks", type=int, default=24, help="Batas maksimal total SKS (default: 24)")
    parser.add_argument("--export-ics", "-o", type=str, help="Simpan solusi terbaik ke berkas Google Calendar (.ics)")
    args = parser.parse_args()

    courses = []
    if args.input:
        if not os.path.exists(args.input):
            print(f"[Error] Berkas masukan tidak ditemukan: {args.input}")
            sys.exit(1)
        ext = os.path.splitext(args.input)[1].lower()
        if ext == ".pdf":
            print(f"[*] Membaca jadwal dari PDF: {args.input}")
            courses = parse_schedule_pdf(args.input)
        elif ext in (".xlsx", ".xls"):
            print(f"[*] Membaca jadwal dari Excel: {args.input}")
            courses = parse_schedule_excel(args.input)
        elif ext == ".csv":
            print(f"[*] Membaca jadwal dari CSV: {args.input}")
            courses = parse_schedule_csv(args.input)
        else:
            print(f"[Error] Ekstensi berkas tidak didukung: {ext}")
            sys.exit(1)
    else:
        print("[*] Mode Demo: Menggunakan 4 mata kuliah representatif Ilmu Komputer UGM")
        courses = get_default_demo_courses()

    print(f"[*] Memuat {len(courses)} mata kuliah.")
    free_days = [d.strip() for d in args.free_day.split(",") if d.strip()]
    pref = SchedulePreference(free_days=free_days, max_total_sks=args.max_sks)

    print("[*] Mengeksekusi Backtracking Search & Forward Checking...")
    solutions = solve_krs_schedule(courses, preferences=pref, max_solutions=3)

    if not solutions:
        print("[!] Tidak ditemukan kombinasi jadwal yang bebas bentrok.")
        sys.exit(0)

    print(f"[+] Ditemukan {len(solutions)} solusi jadwal bebas bentrok!")
    best = solutions[0]
    print("\n" + render_ascii_schedule_matrix(best))

    if args.export_ics:
        ics_text = export_to_ics(best)
        with open(args.export_ics, "w", encoding="utf-8") as f:
            f.write(ics_text)
        print(f"\n[+] Berkas Google Calendar berhasil diekspor ke: {args.export_ics}")


if __name__ == "__main__":
    main()
