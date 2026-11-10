"""
csp_solver.py - Constraint Satisfaction Problem (CSP) Solver for KRS Timetables
Implements Backtracking Search with Forward Checking, MRV variable ordering,
and multi-attribute soft-constraint preference evaluation.
"""

import time
from typing import List, Dict, Optional, Tuple, Set
try:
    from .models import Course, ClassSection, TimeSlot, SchedulePreference, ScheduleSolution
except ImportError:
    from models import Course, ClassSection, TimeSlot, SchedulePreference, ScheduleSolution


class KRSCSPProblem:
    def __init__(self, selected_courses: List[Course], preferences: SchedulePreference):
        self.courses = selected_courses
        self.preferences = preferences

        # Map course code to Course
        self.course_map = {c.code: c for c in selected_courses}

        # Initial domains: each course code maps to its available sections
        self.domains: Dict[str, List[ClassSection]] = {
            c.code: list(c.sections) for c in selected_courses
        }

    def is_consistent(self, section: ClassSection, assignment: Dict[str, ClassSection]) -> bool:
        """
        Hard constraint: Check if this section clashes with any already assigned section.
        """
        for assigned_sec in assignment.values():
            if section.clashes_with(assigned_sec):
                return False
        return True

    def forward_check(self, assigned_var: str, assigned_val: ClassSection,
                      domains: Dict[str, List[ClassSection]],
                      unassigned_vars: List[str]) -> Tuple[bool, Dict[str, List[ClassSection]]]:
        """
        Prunes values from unassigned variables' domains that clash with assigned_val.
        Returns (success_boolean, pruned_domains_dict).
        """
        new_domains = {var: list(sec_list) for var, sec_list in domains.items()}

        for var in unassigned_vars:
            valid_secs = [sec for sec in new_domains[var] if not sec.clashes_with(assigned_val)]
            if not valid_secs:
                # Domain wipeout! Forward checking failed.
                return False, domains
            new_domains[var] = valid_secs

        return True, new_domains

    def select_unassigned_variable_mrv(self, assignment: Dict[str, ClassSection],
                                      domains: Dict[str, List[ClassSection]]) -> Optional[str]:
        """
        Minimum Remaining Values (MRV) heuristic:
        Picks unassigned variable with smallest remaining domain size.
        """
        unassigned = [c.code for c in self.courses if c.code not in assignment]
        if not unassigned:
            return None

        return min(unassigned, key=lambda code: len(domains.get(code, [])))

    def order_domain_values(self, var: str, domains: Dict[str, List[ClassSection]]) -> List[ClassSection]:
        """
        Orders domain values by individual soft preference alignment.
        """
        sections = domains.get(var, [])

        def section_penalty(sec: ClassSection) -> float:
            penalty = 0.0
            for slot in sec.slots:
                if slot.day in self.preferences.free_days:
                    penalty += 30.0
                if slot.start_hour < self.preferences.preferred_min_start_hour:
                    penalty += (self.preferences.preferred_min_start_hour - slot.start_hour) * 10.0
                if slot.end_hour > self.preferences.preferred_max_end_hour:
                    penalty += (slot.end_hour - self.preferences.preferred_max_end_hour) * 10.0
            return penalty

        return sorted(sections, key=section_penalty)

    def calculate_preference_score(self, sections: List[ClassSection]) -> Tuple[float, Dict[str, float]]:
        """
        Evaluates soft constraints and returns a 0.0 - 100.0% satisfaction score.
        """
        breakdown = {
            "free_day_compliance": 100.0,
            "time_window_compliance": 100.0,
            "gap_compactness": 100.0,
            "lunch_break_compliance": 100.0
        }

        # 1. Free day penalty
        if self.preferences.free_days:
            clash_free_days = 0
            for sec in sections:
                for slot in sec.slots:
                    if slot.day in self.preferences.free_days:
                        clash_free_days += 1
            if clash_free_days > 0:
                breakdown["free_day_compliance"] = max(0.0, 100.0 - (clash_free_days * 35.0))

        # 2. Time window penalty
        window_violations = 0
        for sec in sections:
            for slot in sec.slots:
                if slot.start_hour < self.preferences.preferred_min_start_hour:
                    window_violations += 1
                if slot.end_hour > self.preferences.preferred_max_end_hour:
                    window_violations += 1
        if window_violations > 0:
            breakdown["time_window_compliance"] = max(0.0, 100.0 - (window_violations * 20.0))

        # 3. Gaps and Lunch break per day
        slots_by_day: Dict[str, List[TimeSlot]] = {}
        for sec in sections:
            for slot in sec.slots:
                slots_by_day.setdefault(slot.day, []).append(slot)

        gap_penalties = 0
        lunch_violations = 0

        for day, slots in slots_by_day.items():
            sorted_slots = sorted(slots, key=lambda s: s.start_minutes)
            for i in range(len(sorted_slots) - 1):
                gap = sorted_slots[i+1].start_minutes - sorted_slots[i].end_minutes
                if gap > self.preferences.max_gap_minutes:
                    gap_penalties += 1

            # Check lunch window: 11:30 (690 min) to 13:30 (810 min)
            lunch_start, lunch_end = 690, 810
            # If student has classes spanning through lunch, check if there is at least min_lunch_break_minutes free
            spans_lunch = any(s.start_minutes < lunch_end and s.end_minutes > lunch_start for s in sorted_slots)
            if spans_lunch:
                # Find maximum continuous free interval inside lunch window
                intervals = [(s.start_minutes, s.end_minutes) for s in sorted_slots]
                # Check overlap
                busy_in_lunch = any(start <= lunch_start and end >= lunch_end for start, end in intervals)
                if busy_in_lunch:
                    lunch_violations += 1

        if gap_penalties > 0:
            breakdown["gap_compactness"] = max(0.0, 100.0 - (gap_penalties * 25.0))
        if lunch_violations > 0:
            breakdown["lunch_break_compliance"] = max(0.0, 100.0 - (lunch_violations * 30.0))

        # Weighted final score
        weights = {
            "free_day_compliance": 0.35,
            "time_window_compliance": 0.25,
            "gap_compactness": 0.20,
            "lunch_break_compliance": 0.20
        }
        final_score = sum(breakdown[k] * weights[k] for k in weights)
        return round(final_score, 2), breakdown


def solve_krs_schedule(courses: List[Course],
                       preferences: Optional[SchedulePreference] = None,
                       max_solutions: int = 5) -> List[ScheduleSolution]:
    """
    Main entry point: executes Backtracking + Forward Checking solver.
    Returns ranked valid clash-free solutions.
    """
    start_time = time.perf_counter()
    if preferences is None:
        preferences = SchedulePreference()

    if not courses:
        return []

    # De-duplicate courses by unique course code
    unique_courses = list({c.code: c for c in courses}.values())

    # If any course has zero sections available, no valid schedule exists
    if any(len(c.sections) == 0 for c in unique_courses):
        return []

    # Total SKS sanity check
    total_requested_sks = sum(c.sks for c in unique_courses)
    if total_requested_sks > preferences.max_total_sks:
        raise ValueError(
            f"Total SKS mata kuliah ({total_requested_sks}) melampaui batas maksimal ({preferences.max_total_sks} SKS)"
        )

    problem = KRSCSPProblem(unique_courses, preferences)
    all_solutions: List[List[ClassSection]] = []
    solution_target_cap = max(50, max_solutions * 10)

    def backtrack(assignment: Dict[str, ClassSection], current_domains: Dict[str, List[ClassSection]]):
        if len(all_solutions) >= solution_target_cap:
            return

        if len(assignment) == len(problem.courses):
            all_solutions.append(list(assignment.values()))
            return

        var = problem.select_unassigned_variable_mrv(assignment, current_domains)
        if not var:
            return

        ordered_values = problem.order_domain_values(var, current_domains)
        for section in ordered_values:
            if problem.is_consistent(section, assignment):
                # Speculatively assign
                assignment[var] = section

                # Forward checking
                unassigned = [c.code for c in problem.courses if c.code not in assignment]
                fc_success, pruned_domains = problem.forward_check(var, section, current_domains, unassigned)

                if fc_success:
                    backtrack(assignment, pruned_domains)

                # Backtrack
                del assignment[var]

    backtrack({}, problem.domains)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # Score and rank solutions
    results: List[ScheduleSolution] = []
    for sol_secs in all_solutions:
        score, breakdown = problem.calculate_preference_score(sol_secs)
        sol = ScheduleSolution(
            selected_sections=sol_secs,
            total_sks=sum(s.sks for s in sol_secs),
            preference_score=score,
            score_breakdown=breakdown,
            execution_time_ms=elapsed_ms
        )
        results.append(sol)

    # Sort descending by preference score
    results.sort(key=lambda s: s.preference_score, reverse=True)
    return results[:max_solutions]
