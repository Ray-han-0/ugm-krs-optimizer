"""
exporter.py - Timetable visualization and Google Calendar (.ics) export engine
Provides students with immediate actionable schedule files without requiring Google OAuth/APIs.
"""

import datetime
from typing import List, Dict
try:
    from .models import ScheduleSolution, ClassSection, TimeSlot
except ImportError:
    from models import ScheduleSolution, ClassSection, TimeSlot


DAY_MAP_ICS = {
    "senin": "MO",
    "selasa": "TU",
    "rabu": "WE",
    "kamis": "TH",
    "jumat": "FR",
    "sabtu": "SA",
}

DAY_ORDER = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]


def export_to_ics(solution: ScheduleSolution, semester_start_date: datetime.date = None) -> str:
    """
    Generates standard RFC 5545 iCalendar (.ics) string.
    Maps weekly repeating university classes over a 16-week academic semester.
    """
    if semester_start_date is None:
        # Default to a Monday reference date
        semester_start_date = datetime.date(2026, 2, 9)  # Semester Genap 2025/2026

    # Calculate day offsets from Monday
    day_offset = {
        "senin": 0,
        "selasa": 1,
        "rabu": 2,
        "kamis": 3,
        "jumat": 4,
        "sabtu": 5,
    }

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//UGM Computer Science//KRS Optimizer Local//ID",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Jadwal Kuliah Mahasiswa UGM",
        "X-WR-TIMEZONE:Asia/Jakarta",
    ]

    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for sec in solution.selected_sections:
        for slot in sec.slots:
            offset = day_offset.get(slot.day.lower(), 0)
            class_date = semester_start_date + datetime.timedelta(days=offset)

            dt_start = f"{class_date.strftime('%Y%m%d')}T{slot.start_hour:02d}{slot.start_min:02d}00"
            dt_end = f"{class_date.strftime('%Y%m%d')}T{slot.end_hour:02d}{slot.end_min:02d}00"
            uid = f"UGM_{sec.course_code}_{sec.section_name}_{slot.day}_{slot.start_hour}{slot.start_min}@krs.ugm.ac.id"
            summary = f"[{sec.course_code}] {sec.course_name} ({sec.section_name})"
            description = f"Mata Kuliah: {sec.course_name}\\nKelas: {sec.section_name}\\nSKS: {sec.sks}\\nDosen: {sec.lecturer}\\nRuang: {sec.room}"
            rrule = f"FREQ=WEEKLY;COUNT=16;BYDAY={DAY_MAP_ICS.get(slot.day.lower(), 'MO')}"

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now_utc}",
                f"DTSTART;TZID=Asia/Jakarta:{dt_start}",
                f"DTEND;TZID=Asia/Jakarta:{dt_end}",
                f"RRULE:{rrule}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{description}",
                f"LOCATION:{sec.room}",
                "STATUS:CONFIRMED",
                "END:VEVENT",
            ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def format_weekly_matrix(solution: ScheduleSolution) -> Dict[str, List[Dict[str, str]]]:
    """
    Constructs a structured weekly matrix representation (Senin to Jumat)
    ordered by start time for UI rendering and reporting.
    """
    matrix: Dict[str, List[Dict[str, str]]] = {day: [] for day in DAY_ORDER}

    for sec in solution.selected_sections:
        for slot in sec.slots:
            if slot.day in matrix:
                matrix[slot.day].append({
                    "course_code": sec.course_code,
                    "course_name": sec.course_name,
                    "section": sec.section_name,
                    "sks": str(sec.sks),
                    "room": sec.room,
                    "lecturer": sec.lecturer,
                    "time": f"{slot.start_hour:02d}:{slot.start_min:02d} - {slot.end_hour:02d}:{slot.end_min:02d}",
                    "start_min": slot.start_minutes,
                })

    for day in matrix:
        matrix[day].sort(key=lambda item: item["start_min"])

    return matrix


def render_ascii_schedule_matrix(solution: ScheduleSolution) -> str:
    """
    Renders a formatted ASCII table representation of the weekly schedule
    with course code, section, room, and time for terminal visualization.
    """
    matrix = format_weekly_matrix(solution)
    lines = []
    lines.append("=" * 86)
    lines.append(f" JADWAL KULIAH MAHASISWA OPTIMAL (Total: {solution.total_sks} SKS | Skor Kepuasan: {solution.preference_score}%)")
    lines.append("=" * 86)
    lines.append(f"{'Hari':<10} | {'Jam':<15} | {'Kode':<10} | {'Mata Kuliah':<28} | {'Kls':<5} | {'Ruang':<8}")
    lines.append("-" * 86)

    for day in DAY_ORDER:
        day_items = matrix.get(day, [])
        if not day_items:
            lines.append(f"{day:<10} | {'-- Libur / Kosong --':<73}")
        else:
            for idx, item in enumerate(day_items):
                day_col = day if idx == 0 else ""
                short_name = item['course_name'][:26] + ".." if len(item['course_name']) > 28 else item['course_name']
                sec_code = item['section'].replace("Kelas ", "")
                lines.append(
                    f"{day_col:<10} | {item['time']:<15} | {item['course_code']:<10} | {short_name:<28} | {sec_code:<5} | {item['room']:<8}"
                )
        lines.append("-" * 86)

    lines.append(f"Detail Skor Preferensi:")
    for k, v in solution.score_breakdown.items():
        lines.append(f"  - {k.replace('_', ' ').title()}: {v:.1f}%")
    lines.append("=" * 86)
    return "\n".join(lines)

