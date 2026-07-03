import os
import sys

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import subprocess
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Ensure reportlab is installed
install_and_import("reportlab")

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        alignment=0, # Left align
        spaceAfter=20
    )
    story.append(Paragraph("Enterprise Cloud Operations - Q2 Financial Report", title_style))
    story.append(Spacer(1, 12))
    
    # Executive Summary Header
    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=12,
        spaceAfter=6
    )
    story.append(Paragraph("Executive Summary", h1_style))
    
    # Body text
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748")
    )
    summary_text = (
        "During the second quarter of the fiscal year, our enterprise cloud infrastructure "
        "operations experienced significant growth. Total data ingress volumes increased by "
        "35% quarter-over-quarter, driven by new enterprise client onboarding. While scaling "
        "the architecture, we focused heavily on high-performance vector search integration and "
        "optimizing local database operations. Although database connection pool exhaustion "
        "and gateway timeouts caused transient alerts (as detailed in server logs), our mitigation "
        "strategies successfully reduced average query latency to under 50ms by the end of June."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 15))
    
    # Financial Table Header
    story.append(Paragraph("Infrastructure Cost Breakdown (Q2)", h1_style))
    story.append(Spacer(1, 8))
    
    # Table data
    data = [
        ["Category", "April ($)", "May ($)", "June ($)", "Q2 Total ($)"],
        ["Compute (EC2/ECS)", "45,200", "48,500", "52,100", "145,800"],
        ["Database (Qdrant/Aurora)", "12,800", "13,400", "15,900", "42,100"],
        ["Storage (S3/EBS)", "8,400", "9,100", "10,200", "27,700"],
        ["Networking & CDN", "6,100", "6,800", "7,500", "20,400"],
        ["Total", "72,500", "77,800", "85,700", "236,000"]
    ]
    
    # Style Table
    t = Table(data, colWidths=[150, 75, 75, 75, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-2), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EDF2F7")),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor("#2D3748")),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 15))
    
    # Outlook Header
    story.append(Paragraph("Strategic Outlook & Privacy Mandate", h1_style))
    outlook_text = (
        "Looking forward to Q3, our cloud architecture budget is projected to rise as we deploy "
        "more localized vector search databases. Transitioning to privacy-first, fully-local embedding "
        "generation using models like 'all-MiniLM-L6-v2' will eliminate third-party API dependencies "
        "and reduce data egress fees. We estimate this architectural shift will save approximately "
        "15% in operational compute and network costs while ensuring strict data privacy and compliance."
    )
    story.append(Paragraph(outlook_text, body_style))
    
    doc.build(story)
    print(f"Successfully generated PDF at: {filename}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(out_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    pdf_path = os.path.join(data_dir, "financial_quarterly.pdf")
    generate_pdf(pdf_path)
