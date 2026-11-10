"""
styles.py - Typography, Color Palette, and Academic Layout Tokens
Standardized for Universitas Gadjah Mada (UGM) Computer Science Capstone Reports.
Strictly adheres to booktabs academic table styling and clean typography without emojis.
"""

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import TableStyle

# ---------------------------------------------------------
# UGM Academic Palette Tokens
# ---------------------------------------------------------
UGM_NAVY = colors.HexColor("#0B2545")       # Primary UGM Deep Navy
UGM_GOLD = colors.HexColor("#B8860B")       # Accent UGM Gold
UGM_BLUE = colors.HexColor("#134074")       # Secondary Deep Blue
TEXT_DARK = colors.HexColor("#1A202C")      # Primary Body Text
TEXT_MUTED = colors.HexColor("#4A5568")     # Subdued Metadata Text
BG_SURFACE = colors.HexColor("#F8FAFC")     # Soft Panel Background
BORDER_LIGHT = colors.HexColor("#CBD5E1")   # Dividing Borders
BORDER_DARK = colors.HexColor("#334155")    # Booktabs Anchor Lines
SUCCESS_GREEN = colors.HexColor("#15803D")  # Metric High Performance
ALERT_AMBER = colors.HexColor("#B45309")    # Discrepancy / Warning Flag
DANGER_RED = colors.HexColor("#B91C1C")     # Critical Anomaly / Error


def get_ugm_styles():
    """
    Returns an academic ReportLab stylesheet conforming to UGM thesis formatting.
    Margins: Left 4cm, Right 3cm, Top 3cm, Bottom 3cm.
    Font sizing and leading follow formal publication standards.
    """
    base_styles = getSampleStyleSheet()

    custom_styles = {
        # Cover Page Styles
        "CoverUniversity": ParagraphStyle(
            "CoverUniversity",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=UGM_NAVY,
            spaceAfter=6,
        ),
        "CoverFaculty": ParagraphStyle(
            "CoverFaculty",
            parent=base_styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=TEXT_MUTED,
            spaceAfter=24,
        ),
        "CoverDocType": ParagraphStyle(
            "CoverDocType",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            alignment=TA_CENTER,
            textColor=UGM_GOLD,
            spaceAfter=12,
        ),
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=24,
            alignment=TA_CENTER,
            textColor=UGM_NAVY,
            spaceAfter=14,
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base_styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=TEXT_MUTED,
            spaceAfter=36,
        ),
        "CoverIdentity": ParagraphStyle(
            "CoverIdentity",
            parent=base_styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=TEXT_DARK,
        ),
        "CoverYear": ParagraphStyle(
            "CoverYear",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=UGM_NAVY,
            spaceBefore=24,
        ),

        # Chapter Headings (BAB I, BAB II, etc.)
        "ChapterHeading": ParagraphStyle(
            "ChapterHeading",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=UGM_NAVY,
            spaceBefore=14,
            spaceAfter=12,
            keepWithNext=True,
        ),
        "SectionHeading": ParagraphStyle(
            "SectionHeading",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            textColor=UGM_BLUE,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "SubSectionHeading": ParagraphStyle(
            "SubSectionHeading",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            alignment=TA_LEFT,
            textColor=TEXT_DARK,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        ),

        # Body Text & Paragraphs
        "AcademicBody": ParagraphStyle(
            "AcademicBody",
            parent=base_styles["Normal"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=15,
            alignment=TA_JUSTIFY,
            firstLineIndent=20,
            textColor=TEXT_DARK,
            spaceAfter=6,
        ),
        "AcademicBodyNoIndent": ParagraphStyle(
            "AcademicBodyNoIndent",
            parent=base_styles["Normal"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=15,
            alignment=TA_JUSTIFY,
            firstLineIndent=0,
            textColor=TEXT_DARK,
            spaceAfter=6,
        ),
        "AcademicBullet": ParagraphStyle(
            "AcademicBullet",
            parent=base_styles["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            leftIndent=18,
            textColor=TEXT_DARK,
            spaceAfter=3,
        ),

        # Formula / Code Block Display
        "FormulaBlock": ParagraphStyle(
            "FormulaBlock",
            parent=base_styles["Normal"],
            fontName="Courier-Oblique",
            fontSize=9.5,
            leading=13,
            alignment=TA_CENTER,
            textColor=UGM_NAVY,
            spaceBefore=6,
            spaceAfter=6,
        ),
        "PseudocodeBlock": ParagraphStyle(
            "PseudocodeBlock",
            parent=base_styles["Normal"],
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            alignment=TA_LEFT,
            leftIndent=10,
            textColor=TEXT_DARK,
        ),

        # Table & Figure Captions
        "TableCaption": ParagraphStyle(
            "TableCaption",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=UGM_NAVY,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "FigureCaption": ParagraphStyle(
            "FigureCaption",
            parent=base_styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=TEXT_MUTED,
            spaceBefore=4,
            spaceAfter=8,
        ),

        # Table Cell Typography
        "TableHeaderCell": ParagraphStyle(
            "TableHeaderCell",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.whitesmoke,
        ),
        "TableCellLeft": ParagraphStyle(
            "TableCellLeft",
            parent=base_styles["Normal"],
            fontName="Times-Roman",
            fontSize=8.5,
            leading=11,
            alignment=TA_LEFT,
            textColor=TEXT_DARK,
        ),
        "TableCellCenter": ParagraphStyle(
            "TableCellCenter",
            parent=base_styles["Normal"],
            fontName="Times-Roman",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=TEXT_DARK,
        ),
        "TableCellRight": ParagraphStyle(
            "TableCellRight",
            parent=base_styles["Normal"],
            fontName="Times-Roman",
            fontSize=8.5,
            leading=11,
            alignment=TA_RIGHT,
            textColor=TEXT_DARK,
        ),
        "TableCellCode": ParagraphStyle(
            "TableCellCode",
            parent=base_styles["Normal"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
            textColor=UGM_BLUE,
        ),

        # Callout Boxes
        "CalloutText": ParagraphStyle(
            "CalloutText",
            parent=base_styles["Normal"],
            fontName="Times-Italic",
            fontSize=9.5,
            leading=13.5,
            alignment=TA_JUSTIFY,
            textColor=TEXT_DARK,
        ),

        # Bibliography Entry
        "BibEntry": ParagraphStyle(
            "BibEntry",
            parent=base_styles["Normal"],
            fontName="Times-Roman",
            fontSize=9,
            leading=13,
            alignment=TA_LEFT,
            leftIndent=24,
            firstLineIndent=-24,
            textColor=TEXT_DARK,
            spaceAfter=5,
        ),
    }

    return custom_styles


def get_booktabs_style(row_count=0):
    """
    Constructs a formal Booktabs table style:
    - Thick top horizontal line (toprule)
    - Medium header bottom line (midrule)
    - Thick table bottom line (bottomrule)
    - Zero vertical lines
    - Clean padding and alternate row striping
    """
    style_commands = [
        ("LINEABOVE", (0, 0), (-1, 0), 1.5, UGM_NAVY),
        ("BACKGROUND", (0, 0), (-1, 0), UGM_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, UGM_GOLD),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, UGM_NAVY),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
    ]

    # Alternate row striping
    if row_count > 1:
        for r in range(1, row_count):
            if r % 2 == 1:
                style_commands.append(("BACKGROUND", (0, r), (-1, r), BG_SURFACE))

    return TableStyle(style_commands)


def get_callout_box_style():
    """
    Style for shaded executive summary or principle callout boxes.
    """
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_SURFACE),
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER_LIGHT),
        ("LINELEFT", (0, 0), (0, -1), 3.0, UGM_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ])
