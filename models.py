"""
models.py - Data structures for KRS Optimizer
Defines Courses, Sections, Time Slots, Preferences, and Solution representations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import time


@dataclass(frozen=True)
class TimeSlot:
    day: str             # "Senin", "Selasa", "Rabu", "Kamis", "Jumat"
    start_hour: int
    start_min: int
    end_hour: int
    end_min: int

    @property
    def start_minutes(self) -> int:
        return self.start_hour * 60 + self.start_min

    @property
    def end_minutes(self) -> int:
        return self.end_hour * 60 + self.end_min

    def overlaps_with(self, other: "TimeSlot") -> bool:
        """
        Hard constraint check: two time slots clash if they are on the same day
        and their time intervals overlap (start1 < end2 and start2 < end1).
        """
        if self.day.lower() != other.day.lower():
            return False
        return max(self.start_minutes, other.start_minutes) < min(self.end_minutes, other.end_minutes)

    def formatted(self) -> str:
        return f"{self.day} {self.start_hour:02d}:{self.start_min:02d}-{self.end_hour:02d}:{self.end_min:02d}"


@dataclass
class ClassSection:
    course_code: str
    course_name: str
    section_name: str     # e.g., "Kelas A", "Kelas B"
    sks: int
    lecturer: str
    room: str
    slots: List[TimeSlot] = field(default_factory=list)

    @property
    def full_id(self) -> str:
        return f"{self.course_code}_{self.section_name}"

    def clashes_with(self, other: "ClassSection") -> bool:
        """
        Returns True if any time slot of this section clashes with any time slot of other section.
        """
        for s1 in self.slots:
            for s2 in other.slots:
                if s1.overlaps_with(s2):
                    return True
        return False


@dataclass
class Course:
    code: str
    name: str
    sks: int
    sections: List[ClassSection] = field(default_factory=list)


@dataclass
class SchedulePreference:
    free_days: List[str] = field(default_factory=list)          # e.g., ["Jumat"]
    preferred_min_start_hour: int = 8                          # Avoid classes before this hour
    preferred_max_end_hour: int = 16                           # Avoid classes after this hour
    min_lunch_break_minutes: int = 30                          # Lunch break between 11:30 and 13:30
    max_gap_minutes: int = 120                                 # Avoid empty gaps > 2 hours between classes
    max_total_sks: int = 24


@dataclass
class ScheduleSolution:
    selected_sections: List[ClassSection]
    total_sks: int
    preference_score: float                                    # 0.0 to 100.0%
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    execution_time_ms: float = 0.0
