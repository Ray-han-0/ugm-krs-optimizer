"""
parser.py - Ingestion engine for semester schedule documents (Excel, CSV, JSON)
Parses official faculty timetable files without requiring closed university APIs.
"""

import os
import json
import csv
from typing import List, Dict, Any
try:
    from .models import Course, ClassSection, TimeSlot
except ImportError:
    from models import Course, ClassSection, TimeSlot


def parse_time_string(time_str: str) -> (int, int, int, int):
    """
    Parses strings like '08:00-09:40', '08.00 - 09.40', or '08:00 s/d 09:40' into start/end hours and minutes.
    """
    cleaned = (
        time_str.replace("s/d", "-")
        .replace("sd", "-")
        .replace("–", "-")
        .replace("—", "-")
        .replace(".", ":")
        .replace(" ", "")
    )
    parts = cleaned.split("-")
    if len(parts) != 2:
        raise ValueError(f"Format jam tidak valid: {time_str}")

    start_parts = parts[0].split(":")
    end_parts = parts[1].split(":")

    start_h, start_m = int(start_parts[0]), int(start_parts[1])
    end_h, end_m = int(end_parts[0]), int(end_parts[1])

    return start_h, start_m, end_h, end_m


def parse_schedule_json(data: List[Dict[str, Any]]) -> List[Course]:
    """
    Parses a structured JSON list of courses into Course objects with Sections and TimeSlots.
    """
    course_map: Dict[str, Course] = {}

    for item in data:
        code = item["course_code"]
        name = item["course_name"]
        sks = int(item["sks"])
        section_name = item.get("section", "Kelas A")
        lecturer = item.get("lecturer", "Dosen Pengampu")
        room = item.get("room", "Ruang R.301")

        if code not in course_map:
            course_map[code] = Course(code=code, name=name, sks=sks, sections=[])

        slots = []
        for slot_def in item.get("slots", []):
            day = slot_def["day"]
            s_h, s_m, e_h, e_m = parse_time_string(slot_def["time"])
            slots.append(TimeSlot(day=day, start_hour=s_h, start_min=s_m, end_hour=e_h, end_min=e_m))

        section = ClassSection(
            course_code=code,
            course_name=name,
            section_name=section_name,
            sks=sks,
            lecturer=lecturer,
            room=room,
            slots=slots,
        )
        course_map[code].sections.append(section)

    return list(course_map.values())


def parse_schedule_csv(filepath: str) -> List[Course]:
    """
    Parses CSV with columns: Kode, Mata Kuliah, SKS, Kelas, Dosen, Ruang, Hari, Jam
    """
    course_map: Dict[str, Course] = {}
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["Kode"].strip()
            name = row["Mata Kuliah"].strip()
            sks = int(row["SKS"].strip())
            sec_name = row["Kelas"].strip()
            lecturer = row.get("Dosen", "Dosen Pengampu").strip()
            room = row.get("Ruang", "Ruang Kuliah").strip()
            day = row["Hari"].strip()
            time_str = row["Jam"].strip()

            s_h, s_m, e_h, e_m = parse_time_string(time_str)
            slot = TimeSlot(day=day, start_hour=s_h, start_min=s_m, end_hour=e_h, end_min=e_m)

            if code not in course_map:
                course_map[code] = Course(code=code, name=name, sks=sks, sections=[])

            # Check if section already exists (e.g. multiple slots per week)
            existing_sec = next((s for s in course_map[code].sections if s.section_name == sec_name), None)
            if existing_sec:
                existing_sec.slots.append(slot)
            else:
                new_sec = ClassSection(
                    course_code=code,
                    course_name=name,
                    section_name=sec_name,
                    sks=sks,
                    lecturer=lecturer,
                    room=room,
                    slots=[slot]
                )
                course_map[code].sections.append(new_sec)

    return list(course_map.values())


def parse_schedule_excel(filepath: str) -> List[Course]:
    """
    Parses Excel schedule file using openpyxl.
    """
    from openpyxl import load_workbook
    wb = load_workbook(filepath, data_only=True)
    sheet = wb.active

    course_map: Dict[str, Course] = {}
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []

    # Map headers
    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    header_indices = {h.lower(): i for i, h in enumerate(headers)}

    def get_val(row, name, default=""):
        idx = header_indices.get(name.lower())
        if idx is not None and idx < len(row) and row[idx] is not None:
            return str(row[idx]).strip()
        return default

    for row in rows[1:]:
        code = get_val(row, "kode")
        if not code:
            continue
        name = get_val(row, "mata kuliah", "Mata Kuliah")
        sks = int(get_val(row, "sks", "3"))
        sec_name = get_val(row, "kelas", "Kelas A")
        lecturer = get_val(row, "dosen", "Dosen")
        room = get_val(row, "ruang", "R.201")
        day = get_val(row, "hari", "Senin")
        time_str = get_val(row, "jam", "08:00-09:40")

        try:
            s_h, s_m, e_h, e_m = parse_time_string(time_str)
            slot = TimeSlot(day=day, start_hour=s_h, start_min=s_m, end_hour=e_h, end_min=e_m)
        except Exception:
            continue

        if code not in course_map:
            course_map[code] = Course(code=code, name=name, sks=sks, sections=[])

        existing_sec = next((s for s in course_map[code].sections if s.section_name == sec_name), None)
        if existing_sec:
            existing_sec.slots.append(slot)
        else:
            course_map[code].sections.append(ClassSection(
                course_code=code,
                course_name=name,
                section_name=sec_name,
                sks=sks,
                lecturer=lecturer,
                room=room,
                slots=[slot]
            ))

    return list(course_map.values())


def parse_schedule_pdf(filepath: str) -> List[Course]:
    """
    Parses faculty timetable PDF document using pdfplumber.
    Supports both structured PDF tables and line-by-line formatted schedules.
    """
    import pdfplumber
    import re
    course_map: Dict[str, Course] = {}

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    headers = [str(c).strip().lower() if c else "" for c in table[0]]

                    def find_idx(keywords):
                        for kw in keywords:
                            for idx, h in enumerate(headers):
                                if kw in h:
                                    return idx
                        return None

                    code_idx = find_idx(["kode", "code"])
                    name_idx = find_idx(["mata kuliah", "matakuliah", "course", "nama"])
                    sks_idx = find_idx(["sks", "kredit", "credit"])
                    sec_idx = find_idx(["kelas", "section", "kls"])
                    dosen_idx = find_idx(["dosen", "lecturer", "pengampu"])
                    ruang_idx = find_idx(["ruang", "room"])
                    hari_idx = find_idx(["hari", "day"])
                    jam_idx = find_idx(["jam", "waktu", "time"])

                    if code_idx is not None and hari_idx is not None and jam_idx is not None:
                        for row in table[1:]:
                            if not row or len(row) <= code_idx:
                                continue
                            code = str(row[code_idx]).strip() if row[code_idx] else ""
                            if not code or code.lower() in ("kode", "total", "keterangan"):
                                continue
                            name = str(row[name_idx]).strip() if name_idx is not None and len(row) > name_idx and row[name_idx] else "Mata Kuliah"
                            sks_raw = str(row[sks_idx]).strip() if sks_idx is not None and len(row) > sks_idx and row[sks_idx] else "3"
                            try:
                                sks = int(re.sub(r"\D", "", sks_raw)) if re.sub(r"\D", "", sks_raw) else 3
                            except ValueError:
                                sks = 3
                            sec_name = str(row[sec_idx]).strip() if sec_idx is not None and len(row) > sec_idx and row[sec_idx] else "Kelas A"
                            lecturer = str(row[dosen_idx]).strip() if dosen_idx is not None and len(row) > dosen_idx and row[dosen_idx] else "Dosen Pengampu"
                            room = str(row[ruang_idx]).strip() if ruang_idx is not None and len(row) > ruang_idx and row[ruang_idx] else "Ruang Kuliah"
                            day = str(row[hari_idx]).strip() if len(row) > hari_idx and row[hari_idx] else "Senin"
                            time_str = str(row[jam_idx]).strip() if len(row) > jam_idx and row[jam_idx] else "08:00-09:40"

                            try:
                                s_h, s_m, e_h, e_m = parse_time_string(time_str)
                                slot = TimeSlot(day=day.title(), start_hour=s_h, start_min=s_m, end_hour=e_h, end_min=e_m)
                            except Exception:
                                continue

                            if code not in course_map:
                                course_map[code] = Course(code=code, name=name, sks=sks, sections=[])

                            existing_sec = next((s for s in course_map[code].sections if s.section_name == sec_name), None)
                            if existing_sec:
                                existing_sec.slots.append(slot)
                            else:
                                course_map[code].sections.append(ClassSection(
                                    course_code=code,
                                    course_name=name,
                                    section_name=sec_name,
                                    sks=sks,
                                    lecturer=lecturer,
                                    room=room,
                                    slots=[slot]
                                ))

            # If no tables found or empty, fallback to text regex parsing
            if not course_map:
                text = page.extract_text()
                if text:
                    for line in text.split("\n"):
                        m = re.search(r"([A-Z]{2,4}-?\d{3,4})\s+(.+?)\s+(\d)\s+(Kelas\s+[A-Z]|[A-Z])\s+.*?(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu)\s+([\d\.:]+(?:\s*-\s*|\s*s/d\s*)[\d\.:]+)", line, re.IGNORECASE)
                        if m:
                            code, name, sks, sec_name, day, time_str = m.group(1), m.group(2).strip(), int(m.group(3)), m.group(4).strip(), m.group(5), m.group(6)
                            try:
                                s_h, s_m, e_h, e_m = parse_time_string(time_str)
                                slot = TimeSlot(day=day.title(), start_hour=s_h, start_min=s_m, end_hour=e_h, end_min=e_m)
                            except Exception:
                                continue

                            if code not in course_map:
                                course_map[code] = Course(code=code, name=name, sks=sks, sections=[])

                            existing_sec = next((s for s in course_map[code].sections if s.section_name == sec_name), None)
                            if existing_sec:
                                existing_sec.slots.append(slot)
                            else:
                                course_map[code].sections.append(ClassSection(
                                    course_code=code,
                                    course_name=name,
                                    section_name=sec_name,
                                    sks=sks,
                                    lecturer="Dosen Pengampu",
                                    room="R. Kuliah",
                                    slots=[slot]
                                ))


    return list(course_map.values())

