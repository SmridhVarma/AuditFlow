"""
PDF Generator using ReportLab
Creates professional insurance audit reports
"""

import io
from datetime import datetime
from typing import List, Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def get_value(obj, key, default=None):
    """Safely get value from dict or Pydantic object"""
    if isinstance(obj, dict):
        return obj.get(key, default)
    elif hasattr(obj, key):
        return getattr(obj, key, default)
    elif hasattr(obj, 'model_dump'):
        return obj.model_dump().get(key, default)
    elif hasattr(obj, 'dict'):
        return obj.dict().get(key, default)
    return default


class AuditPDFGenerator:
    """Generates professional PDF audit reports for insurance claims"""
    
    # Color scheme
    COLORS = {
        "primary": colors.HexColor("#1a365d"),  # Dark blue
        "secondary": colors.HexColor("#2c5282"),  # Medium blue
        "accent": colors.HexColor("#3182ce"),  # Light blue
        "success": colors.HexColor("#38a169"),  # Green
        "warning": colors.HexColor("#d69e2e"),  # Yellow
        "danger": colors.HexColor("#e53e3e"),  # Red
        "neutral": colors.HexColor("#718096"),  # Gray
        "light": colors.HexColor("#f7fafc"),  # Light gray
    }
    
    DECISION_COLORS = {
        "COVERED": colors.HexColor("#38a169"),
        "NOT_COVERED": colors.HexColor("#e53e3e"),
        "PARTIAL": colors.HexColor("#d69e2e"),
        "NEEDS_REVIEW": colors.HexColor("#3182ce"),
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=self.styles["Heading1"],
            fontSize=24,
            textColor=self.COLORS["primary"],
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=self.COLORS["secondary"],
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=5,
        ))
        
        # Subsection header
        self.styles.add(ParagraphStyle(
            name="SubsectionHeader",
            parent=self.styles["Heading3"],
            fontSize=12,
            textColor=self.COLORS["accent"],
            spaceBefore=10,
            spaceAfter=5,
        ))
        
        # Body text (renamed to avoid conflict with built-in BodyText)
        self.styles.add(ParagraphStyle(
            name="CustomBodyText",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ))
        
        # Quote/Evidence style
        self.styles.add(ParagraphStyle(
            name="Evidence",
            parent=self.styles["Normal"],
            fontSize=9,
            textColor=self.COLORS["neutral"],
            leftIndent=20,
            rightIndent=20,
            spaceBefore=5,
            spaceAfter=5,
            borderColor=self.COLORS["accent"],
            borderWidth=1,
            borderPadding=10,
            backColor=self.COLORS["light"],
        ))
        
        # Step style
        self.styles.add(ParagraphStyle(
            name="ReasoningStep",
            parent=self.styles["Normal"],
            fontSize=9,
            leftIndent=15,
            spaceAfter=5,
        ))
    
    def generate(
        self,
        claim_id: str,
        claim_text: str,
        region: str,
        category: str,
        decision: str,
        confidence: float,
        summary: str,
        reasoning_trace: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
        exclusions: List[str],
        limits: List[str],
    ) -> bytes:
        """Generate the PDF report and return as bytes"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        story = []
        
        # Title
        story.append(Paragraph("AuditFlow", self.styles["ReportTitle"]))
        story.append(Paragraph("Insurance Claim Analysis Report", self.styles["Heading2"]))
        story.append(Spacer(1, 20))
        
        # Horizontal line
        story.append(HRFlowable(
            width="100%",
            thickness=2,
            color=self.COLORS["primary"],
            spaceBefore=10,
            spaceAfter=20,
        ))
        
        # Claim Summary Section
        story.append(Paragraph("1. Claim Summary", self.styles["SectionHeader"]))
        
        claim_data = [
            ["Claim ID:", claim_id],
            ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Region:", f"{region} ({'Singapore' if region == 'SG' else 'Australia'})"],
            ["Category:", category],
        ]
        
        claim_table = Table(claim_data, colWidths=[100, 350])
        claim_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), self.COLORS["neutral"]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(claim_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("<b>Claim Description:</b>", self.styles["CustomBodyText"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(claim_text, self.styles["Evidence"]))
        story.append(Spacer(1, 20))
        
        # Decision Section
        story.append(Paragraph("2. Decision", self.styles["SectionHeader"]))
        
        decision_color = self.DECISION_COLORS.get(decision, self.COLORS["neutral"])
        decision_style = ParagraphStyle(
            name="DecisionText",
            parent=self.styles["Heading1"],
            fontSize=18,
            textColor=decision_color,
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10,
        )
        story.append(Paragraph(decision, decision_style))
        
        confidence_text = f"Confidence: {confidence * 100:.1f}%"
        story.append(Paragraph(confidence_text, ParagraphStyle(
            name="ConfidenceText",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=self.COLORS["neutral"],
            alignment=TA_CENTER,
        )))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph("<b>Summary:</b>", self.styles["CustomBodyText"]))
        story.append(Paragraph(summary, self.styles["CustomBodyText"]))
        
        # Evidence Section
        story.append(Spacer(1, 10))
        story.append(Paragraph("3. Policy Evidence", self.styles["SectionHeader"]))
        story.append(Spacer(1, 10))
        story.append(Spacer(1, 20))
        
        if evidence:
            for i, ev in enumerate(evidence, 1):
                policy_name = get_value(ev, "policy_name", "Unknown Policy")
                section = get_value(ev, "section", "")
                relevance = get_value(ev, "relevance_score", 0) * 100
                
                story.append(Paragraph(
                    f"<b>Evidence {i}:</b> {policy_name} {f'- {section}' if section else ''} "
                    f"<font color='gray'>(Relevance: {relevance:.0f}%)</font>",
                    self.styles["SubsectionHeader"]
                ))
                story.append(Spacer(1, 10))
                story.append(Spacer(1, 10))
                story.append(Paragraph(
                    get_value(ev, "content", "No content available"),
                    self.styles["Evidence"]
                ))
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph(
                "No policy evidence was retrieved for this claim.",
                self.styles["CustomBodyText"]
            ))
            story.append(Spacer(1, 10))
        
        # Exclusions & Limits
        if exclusions or limits:
            story.append(Paragraph("4. Exclusions & Limits", self.styles["SectionHeader"]))
            
            if exclusions:
                story.append(Paragraph("<b>Exclusions Found:</b>", self.styles["SubsectionHeader"]))
                for exc in exclusions:
                    story.append(Paragraph(f"• {exc}", self.styles["CustomBodyText"]))
            
            if limits:
                story.append(Paragraph("<b>Coverage Limits:</b>", self.styles["SubsectionHeader"]))
                for lim in limits:
                    story.append(Paragraph(f"• {lim}", self.styles["CustomBodyText"]))
        
        # Reasoning Trace
        section_num = 5 if (exclusions or limits) else 4
        story.append(Paragraph(f"{section_num}. Reasoning Trace", self.styles["SectionHeader"]))
        story.append(Paragraph(
            "The following shows the step-by-step reasoning process used to analyze this claim:",
            self.styles["CustomBodyText"]
        ))
        story.append(Spacer(1, 10))
        
        step_colors = {
            "THINK": self.COLORS["secondary"],
            "ACT": self.COLORS["accent"],
            "OBSERVE": self.COLORS["success"],
            "DECIDE": self.COLORS["primary"],
        }
        
        for step in reasoning_trace:
            step_type = get_value(step, "step_type", "UNKNOWN")
            step_num = get_value(step, "step_number", 0)
            content = get_value(step, "content", "")
            tool_used = get_value(step, "tool_used", "")
            
            color = step_colors.get(step_type, self.COLORS["neutral"])
            
            step_header = f"<font color='{color.hexval()}'>Step {step_num} [{step_type}]</font>"
            if tool_used:
                step_header += f" - Tool: {tool_used}"
            
            story.append(Paragraph(step_header, self.styles["SubsectionHeader"]))
            story.append(Paragraph(content[:500], self.styles["ReasoningStep"]))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.COLORS["neutral"],
            spaceBefore=20,
            spaceAfter=10,
        ))
        
        footer_text = (
            f"<font size='8' color='gray'>"
            f"Generated by AuditFlow Agentic Claims Processing System<br/>"
            f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            f"This report is for internal use only and requires human adjuster review."
            f"</font>"
        )
        story.append(Paragraph(footer_text, self.styles["Normal"]))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
