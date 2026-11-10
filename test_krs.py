"""
test_krs.py - Comprehensive Unit & Integration Tests for KRS Optimizer
Tests CSP solver logic, clash detection, soft preference scoring, and ICS exporting.
"""

import unittest
import time
import os
import sys

# Ensure current module directory is on sys.path
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if CURR_DIR not in sys.path:
    sys.path.insert(0, CURR_DIR)

from models import Course, ClassSection, TimeSlot, SchedulePreference, ScheduleSolution
from csp_solver import KRSCSPProblem, solve_krs_schedule
from exporter import export_to_ics, format_weekly_matrix, render_ascii_schedule_matrix
from parser import parse_schedule_pdf, parse_time_string



class TestKRSOptimizer(unittest.TestCase):
    def setUp(self):
        # Sample realistic UGM CS Courses
        self.course_ai = Course(
            code="MII-3101", name="Kecerdasan Buatan", sks=3,
            sections=[
                ClassSection("MII-3101", "Kecerdasan Buatan", "Kelas A", 3, "Dr. Mardhani", "R.301",
                             [TimeSlot("Senin", 8, 0, 9, 40)]),
                ClassSection("MII-3101", "Kecerdasan Buatan", "Kelas B", 3, "Dr. Mardhani", "R.302",
                             [TimeSlot("Rabu", 10, 0, 11, 40)]),
            ]
        )
        self.course_os = Course(
            code="MII-2104", name="Sistem Operasi", sks=3,
            sections=[
                ClassSection("MII-2104", "Sistem Operasi", "Kelas A", 3, "Prof. Wibowo", "R.201",
                             [TimeSlot("Senin", 8, 30, 10, 10)]),  # Clashes with AI Kelas A!
                ClassSection("MII-2104", "Sistem Operasi", "Kelas B", 3, "Prof. Wibowo", "R.202",
                             [TimeSlot("Kamis", 13, 0, 14, 40)]),
            ]
        )
        self.course_db = Course(
            code="MII-2201", name="Basis Data", sks=3,
            sections=[
                ClassSection("MII-2201", "Basis Data", "Kelas A", 3, "Ir. Retno, M.Kom.", "R.105",
                             [TimeSlot("Selasa", 10, 0, 11, 40)]),
                ClassSection("MII-2201", "Basis Data", "Kelas B", 3, "Ir. Retno, M.Kom.", "R.106",
                             [TimeSlot("Jumat", 8, 0, 9, 40)]),
            ]
        )

    def test_timeslot_clash_detection(self):
        slot1 = TimeSlot("Senin", 8, 0, 9, 40)
        slot2 = TimeSlot("Senin", 9, 0, 10, 40)  # Overlaps
        slot3 = TimeSlot("Senin", 9, 40, 11, 20) # Back-to-back (not overlapping)
        slot4 = TimeSlot("Selasa", 8, 0, 9, 40)  # Different day

        self.assertTrue(slot1.overlaps_with(slot2))
        self.assertFalse(slot1.overlaps_with(slot3))
        self.assertFalse(slot1.overlaps_with(slot4))

    def test_hard_constraint_zero_clash_solver(self):
        courses = [self.course_ai, self.course_os, self.course_db]
        solutions = solve_krs_schedule(courses)

        self.assertGreater(len(solutions), 0)
        for sol in solutions:
            self.assertEqual(len(sol.selected_sections), 3)
            # Verify 0 minutes intersection between any selected pair
            for i in range(len(sol.selected_sections)):
                for j in range(i + 1, len(sol.selected_sections)):
                    self.assertFalse(sol.selected_sections[i].clashes_with(sol.selected_sections[j]))

    def test_soft_constraint_free_friday_preference(self):
        courses = [self.course_ai, self.course_os, self.course_db]
        pref_free_friday = SchedulePreference(free_days=["Jumat"])
        solutions = solve_krs_schedule(courses, preferences=pref_free_friday)

        self.assertGreater(len(solutions), 0)
        best_sol = solutions[0]
        # Basis Data Kelas B is on Friday, Kelas A is on Tuesday
        # The best solution should pick Kelas A to satisfy Friday free preference
        db_sec = next(s for s in best_sol.selected_sections if s.course_code == "MII-2201")
        self.assertEqual(db_sec.section_name, "Kelas A")
        self.assertEqual(best_sol.score_breakdown["free_day_compliance"], 100.0)

    def test_sks_limit_validation(self):
        courses = [self.course_ai, self.course_os, self.course_db]
        # Restrict max SKS to 5 (courses total 9 SKS)
        strict_pref = SchedulePreference(max_total_sks=5)
        with self.assertRaises(ValueError):
            solve_krs_schedule(courses, preferences=strict_pref)

    def test_export_to_ics(self):
        courses = [self.course_ai, self.course_os]
        solutions = solve_krs_schedule(courses)
        self.assertTrue(len(solutions) > 0)

        ics_content = export_to_ics(solutions[0])
        self.assertIn("BEGIN:VCALENDAR", ics_content)
        self.assertIn("RRULE:FREQ=WEEKLY", ics_content)
        self.assertIn("Kecerdasan Buatan", ics_content)
        self.assertIn("END:VCALENDAR", ics_content)

    def test_solver_latency_benchmark(self):
        # 5 Variations Benchmark: 4, 6, 8, 10, and 12 courses
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        times = [(8, 0, 9, 40), (10, 0, 11, 40), (13, 0, 14, 40), (15, 0, 16, 40)]

        course_counts = [4, 6, 8, 10, 12]
        for count in course_counts:
            test_courses = []
            for c_idx in range(count):
                sections = []
                for sec_idx in range(3):
                    d = days[(c_idx + sec_idx) % len(days)]
                    sh, sm, eh, em = times[(c_idx * 2 + sec_idx) % len(times)]
                    slot = TimeSlot(d, sh, sm, eh, em)
                    sec = ClassSection(
                        course_code=f"CS-{100+c_idx}",
                        course_name=f"Course {c_idx+1}",
                        section_name=f"Kelas {chr(65+sec_idx)}",
                        sks=3, lecturer="Lecturer", room="R.101",
                        slots=[slot]
                    )
                    sections.append(sec)
                test_courses.append(Course(code=f"CS-{100+c_idx}", name=f"Course {c_idx+1}", sks=3, sections=sections))

            pref = SchedulePreference(max_total_sks=count * 3 + 6)
            t_start = time.perf_counter()
            sols = solve_krs_schedule(test_courses, preferences=pref, max_solutions=3)
            elapsed = time.perf_counter() - t_start

            # Must finish well under 3.0 seconds
            self.assertLess(elapsed, 3.0, f"Solver took {elapsed:.4f}s for {count} courses, exceeding 3s limit")

    def test_render_ascii_schedule_matrix(self):
        courses = [self.course_ai, self.course_os]
        sols = solve_krs_schedule(courses)
        self.assertTrue(len(sols) > 0)
        table_str = render_ascii_schedule_matrix(sols[0])
        self.assertIn("JADWAL KULIAH MAHASISWA OPTIMAL", table_str)
        self.assertIn("Kecerdasan Buatan", table_str)

    def test_parse_schedule_pdf(self):
        # Generate a temporary PDF schedule using reportlab
        import tempfile
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table as RLTable
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
            temp_pdf = tf.name

        try:
            doc = SimpleDocTemplate(temp_pdf, pagesize=letter)
            data = [
                ["Kode", "Mata Kuliah", "SKS", "Kelas", "Dosen", "Ruang", "Hari", "Jam"],
                ["CS-101", "Algoritma Pemrograman", "3", "Kelas A", "Dr. Budi", "R.101", "Senin", "08:00-09:40"],
                ["CS-101", "Algoritma Pemrograman", "3", "Kelas B", "Dr. Budi", "R.102", "Rabu", "10:00-11:40"],
                ["CS-102", "Struktur Data", "3", "Kelas A", "Ir. Retno", "R.103", "Selasa", "13:00-14:40"]
            ]
            from reportlab.lib import colors
            t = RLTable(data)
            t.setStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.black)])
            doc.build([t])


            parsed_courses = parse_schedule_pdf(temp_pdf)
            self.assertEqual(len(parsed_courses), 2)
            codes = [c.code for c in parsed_courses]
            self.assertIn("CS-101", codes)
            self.assertIn("CS-102", codes)
            cs101 = next(c for c in parsed_courses if c.code == "CS-101")
            self.assertEqual(len(cs101.sections), 2)
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)

    def test_empty_courses_and_impossible_clashes(self):
        # Empty courses list
        self.assertEqual(solve_krs_schedule([]), [])

        # Course with zero sections
        empty_sec_course = Course("CS-EMPTY", "Kosong", 3, sections=[])
        self.assertEqual(solve_krs_schedule([empty_sec_course]), [])

        # Impossible clash: two courses with only 1 section each at the exact same time
        c1 = Course("CS-A", "A", 3, [ClassSection("CS-A", "A", "K1", 3, "D1", "R1", [TimeSlot("Senin", 8, 0, 10, 0)])])
        c2 = Course("CS-B", "B", 3, [ClassSection("CS-B", "B", "K1", 3, "D2", "R2", [TimeSlot("Senin", 8, 0, 10, 0)])])
        self.assertEqual(solve_krs_schedule([c1, c2]), [])

    def test_duplicate_courses_deduplication(self):
        # Passing duplicate Course objects with same code should be gracefully de-duplicated
        c1 = Course("CS-AI", "AI", 3, [ClassSection("CS-AI", "AI", "K1", 3, "D1", "R1", [TimeSlot("Senin", 8, 0, 9, 40)])])
        c2 = Course("CS-AI", "AI", 3, [ClassSection("CS-AI", "AI", "K1", 3, "D1", "R1", [TimeSlot("Senin", 8, 0, 9, 40)])])
        sols = solve_krs_schedule([c1, c2])
        self.assertEqual(len(sols), 1)
        self.assertEqual(len(sols[0].selected_sections), 1)

    def test_parse_time_string_delimiters(self):
        # Standard hyphen
        self.assertEqual(parse_time_string("08:00-09:40"), (8, 0, 9, 40))
        self.assertEqual(parse_time_string("08.00 - 09.40"), (8, 0, 9, 40))
        # s/d and sd delimiter variations common in Indonesian faculty schedules
        self.assertEqual(parse_time_string("08:00 s/d 09:40"), (8, 0, 9, 40))
        self.assertEqual(parse_time_string("10.00 sd 11.40"), (10, 0, 11, 40))
        # En-dash and em-dash
        self.assertEqual(parse_time_string("13:00–14:40"), (13, 0, 14, 40))
        self.assertEqual(parse_time_string("15:00—16:40"), (15, 0, 16, 40))


if __name__ == "__main__":
    unittest.main()


