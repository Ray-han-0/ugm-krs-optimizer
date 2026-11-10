"""
pdf_engine.py - Core ReportLab PDF Generation Engine for UGM Capstone Reports
Implements strict UGM academic standards:
- Paper: A4 (210 x 297 mm)
- Margins: Left 4.0 cm, Right 3.0 cm, Top 3.0 cm, Bottom 3.0 cm
- NumberedCanvas: Two-pass dynamic page numbering ("Halaman X dari Y")
- Flowable builders: Cover Page, Chapter Headings, Booktabs Tables, Visual Diagram Tables, Callout Boxes.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from shared.styles import (
    get_ugm_styles, get_booktabs_style, get_callout_box_style,
    UGM_NAVY, UGM_GOLD, UGM_BLUE, TEXT_MUTED, TEXT_DARK, BORDER_LIGHT, BG_SURFACE
)

# Page geometry constants
PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 4.0 * cm
RIGHT_MARGIN = 3.0 * cm
TOP_MARGIN = 3.0 * cm
BOTTOM_MARGIN = 3.0 * cm
USABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN  # ~14.0 cm


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for dynamic total page count computation and UGM running headers/footers.
    Excludes headers and footers on the cover page (Page 1).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        # Do not print running headers and footers on Cover Page (page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)

        # Running Header
        header_text = "Laporan Teknis Proyek Capstone Mandiri - DIKE FMIPA UGM"
        self.drawString(LEFT_MARGIN, PAGE_HEIGHT - TOP_MARGIN + 15, header_text)
        self.setStrokeColor(BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(LEFT_MARGIN, PAGE_HEIGHT - TOP_MARGIN + 10, PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - TOP_MARGIN + 10)

        # Running Footer
        footer_left = "Departemen Ilmu Komputer dan Elektronika"
        footer_right = f"Halaman {self._pageNumber} dari {total_pages}"
        self.drawString(LEFT_MARGIN, BOTTOM_MARGIN - 20, footer_left)
        self.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, BOTTOM_MARGIN - 20, footer_right)
        self.line(LEFT_MARGIN, BOTTOM_MARGIN - 12, PAGE_WIDTH - RIGHT_MARGIN, BOTTOM_MARGIN - 12)

        self.restoreState()


class UGMReportBuilder:
    """
    High-level factory to construct modular, publication-quality UGM Capstone PDFs.
    """
    def __init__(self, output_filepath, document_title):
        self.output_filepath = output_filepath
        self.document_title = document_title
        self.styles = get_ugm_styles()
        self.story = []
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)

    def add_cover_page(self, module_num, module_name, app_subtitle, student_name="Rayhan M. P.", student_nim="22/498765/PA/21345", academic_year="2025/2026"):
        """
        Builds formal UGM Capstone Cover Page.
        """
        self.story.append(Spacer(1, 1.5 * cm))
        self.story.append(Paragraph("UNIVERSITAS GADJAH MADA", self.styles["CoverUniversity"]))
        self.story.append(Paragraph("FAKULTAS MATEMATIKA DAN ILMU PENGETAHUAN ALAM<br/>DEPARTEMEN ILMU KOMPUTER DAN ELEKTRONIKA", self.styles["CoverFaculty"]))
        self.story.append(Spacer(1, 1.0 * cm))

        self.story.append(HRFlowable(width="60%", thickness=1.5, color=UGM_GOLD, spaceBefore=0, spaceAfter=20, hAlign="CENTER"))
        self.story.append(Paragraph("LAPORAN TEKNIS PROYEK CAPSTONE MANDIRI", self.styles["CoverDocType"]))
        self.story.append(Paragraph(f"MODUL {module_num:02d}: {module_name.upper()}", self.styles["CoverTitle"]))
        self.story.append(Paragraph(app_subtitle, self.styles["CoverSubtitle"]))
        self.story.append(HRFlowable(width="60%", thickness=1.5, color=UGM_GOLD, spaceBefore=0, spaceAfter=30, hAlign="CENTER"))

        self.story.append(Spacer(1, 2.0 * cm))
        ident_text = (
            f"<b>Disusun Oleh:</b><br/>"
            f"<b>{student_name}</b><br/>"
            f"NIM: {student_nim}<br/>"
            f"Program Studi Sarjana Ilmu Komputer"
        )
        self.story.append(Paragraph(ident_text, self.styles["CoverIdentity"]))

        self.story.append(Spacer(1, 2.5 * cm))
        year_text = f"YOGYAKARTA<br/>TAHUN AKADEMIK {academic_year}"
        self.story.append(Paragraph(year_text, self.styles["CoverYear"]))
        self.story.append(PageBreak())

    def add_chapter_heading(self, bab_num_roman, bab_title):
        """
        Appends centered uppercase formal chapter heading (e.g. BAB I - PENDAHULUAN).
        """
        text = f"BAB {bab_num_roman}<br/>{bab_title.upper()}"
        self.story.append(Paragraph(text, self.styles["ChapterHeading"]))
        self.story.append(Spacer(1, 8))

    def add_section_heading(self, numbering, title):
        """
        Appends formal section heading (e.g. 1.1 Latar Belakang).
        """
        text = f"{numbering} {title}"
        self.story.append(Paragraph(text, self.styles["SectionHeading"]))

    def add_subsection_heading(self, numbering, title):
        """
        Appends formal subsection heading (e.g. 1.1.1 Urgensi Masalah).
        """
        text = f"{numbering} {title}"
        self.story.append(Paragraph(text, self.styles["SubSectionHeading"]))

    def add_paragraph(self, text, indent=True):
        """
        Appends academic justified paragraph with optional first-line indent.
        """
        style = self.styles["AcademicBody"] if indent else self.styles["AcademicBodyNoIndent"]
        self.story.append(Paragraph(text, style))

    def add_bullet(self, bold_prefix, text):
        """
        Appends bullet point item.
        """
        content = f"&bull; <b>{bold_prefix}:</b> {text}"
        self.story.append(Paragraph(content, self.styles["AcademicBullet"]))

    def add_callout(self, title, text):
        """
        Appends framed callout box with gold accent on left.
        """
        p_content = f"<b>{title.upper()}</b><br/>{text}"
        p = Paragraph(p_content, self.styles["CalloutText"])
        tbl = Table([[p]], colWidths=[USABLE_WIDTH])
        tbl.setStyle(get_callout_box_style())
        self.story.append(Spacer(1, 4))
        self.story.append(tbl)
        self.story.append(Spacer(1, 6))

    def add_formula_block(self, formula_text, label=""):
        """
        Appends centered monospace formula block with optional right-aligned label.
        """
        lbl = f"&nbsp;&nbsp;&nbsp;&nbsp;({label})" if label else ""
        text = f"<b>{formula_text}</b>{lbl}"
        self.story.append(Paragraph(text, self.styles["FormulaBlock"]))

    def add_pseudocode_block(self, lines, caption=""):
        """
        Appends clean monospace algorithm block.
        """
        formatted_code = "<br/>".join([line.replace(" ", "&nbsp;") for line in lines])
        p = Paragraph(formatted_code, self.styles["PseudocodeBlock"])
        tbl = Table([[p]], colWidths=[USABLE_WIDTH])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_SURFACE),
            ("BOX", (0, 0), (-1, -1), 0.75, BORDER_LIGHT),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        if caption:
            self.story.append(Paragraph(f"<b>Algoritma: {caption}</b>", self.styles["TableCaption"]))
        self.story.append(tbl)
        self.story.append(Spacer(1, 6))

    def add_booktabs_table(self, headers, rows_data, col_proportions, caption=""):
        """
        Appends strict booktabs table with auto-wrapped Paragraph cells.
        col_proportions should sum to 1.0 (or normalized automatically).
        """
        total_p = sum(col_proportions)
        col_widths = [(p / total_p) * USABLE_WIDTH for p in col_proportions]

        # Wrap headers
        header_cells = [
            Paragraph(f"<b>{h}</b>", self.styles["TableHeaderCell"]) for h in headers
        ]
        table_rows = [header_cells]

        # Wrap rows
        for row in rows_data:
            wrapped_row = []
            for cell_val in row:
                wrapped_row.append(Paragraph(str(cell_val), self.styles["TableCellLeft"]))
            table_rows.append(wrapped_row)

        tbl = Table(table_rows, colWidths=col_widths)
        tbl.setStyle(get_booktabs_style(len(table_rows)))

        if caption:
            self.story.append(Paragraph(f"<b>{caption}</b>", self.styles["TableCaption"]))
        self.story.append(tbl)
        self.story.append(Spacer(1, 8))

    def add_pipeline_flowchart(self, step_list, caption=""):
        """
        Draws vector-styled sequence pipeline with connector markers.
        step_list: list of tuples (step_name, description)
        """
        rows = []
        for idx, (name, desc) in enumerate(step_list):
            num_str = f"Langkah {idx+1}"
            cell_content = f"<b>[{num_str}] {name}</b><br/><font color='#4A5568'>{desc}</font>"
            p = Paragraph(cell_content, self.styles["TableCellLeft"])
            rows.append([p])
            if idx < len(step_list) - 1:
                arrow_p = Paragraph("<font color='#0B2545'><b>&darr;&nbsp; [Alur Eksekusi Data Terbuka] &darr;</b></font>", self.styles["TableCellCenter"])
                rows.append([arrow_p])

        tbl = Table(rows, colWidths=[USABLE_WIDTH])
        style_cmds = [
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        # Box only on even rows (the content blocks)
        for r_idx in range(len(rows)):
            if r_idx % 2 == 0:
                style_cmds.extend([
                    ("BACKGROUND", (0, r_idx), (-1, r_idx), BG_SURFACE),
                    ("BOX", (0, r_idx), (-1, r_idx), 1.0, UGM_BLUE),
                    ("TOPPADDING", (0, r_idx), (-1, r_idx), 6),
                    ("BOTTOMPADDING", (0, r_idx), (-1, r_idx), 6),
                    ("LEFTPADDING", (0, r_idx), (-1, r_idx), 12),
                    ("RIGHTPADDING", (0, r_idx), (-1, r_idx), 12),
                ])
            else:
                style_cmds.extend([
                    ("TOPPADDING", (0, r_idx), (-1, r_idx), 3),
                    ("BOTTOMPADDING", (0, r_idx), (-1, r_idx), 3),
                ])
        tbl.setStyle(TableStyle(style_cmds))

        if caption:
            self.story.append(Paragraph(f"<b>{caption}</b>", self.styles["FigureCaption"]))
        self.story.append(tbl)
        self.story.append(Spacer(1, 8))

    def add_page_break(self):
        self.story.append(PageBreak())

    def add_spacer(self, height_cm):
        self.story.append(Spacer(1, height_cm * cm))

    def add_bib_entry(self, ref_key, citation_text):
        """
        Appends IEEE/APA formatted bibliography item.
        """
        text = f"[{ref_key}] {citation_text}"
        self.story.append(Paragraph(text, self.styles["BibEntry"]))

    def build_pdf(self):
        """
        Compiles the story into the destination PDF file using NumberedCanvas.
        """
        doc = SimpleDocTemplate(
            self.output_filepath,
            pagesize=A4,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
            title=self.document_title,
            author="Departemen Ilmu Komputer dan Elektronika FMIPA UGM",
        )
        doc.build(self.story, canvasmaker=NumberedCanvas)
        return self.output_filepath
