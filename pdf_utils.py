from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Image
from pathlib import Path
from datetime import datetime
import re

BLUE = colors.HexColor('#1E3A8A')
BLUE2 = colors.HexColor('#2563EB')
CYAN = colors.HexColor('#38BDF8')
TEXT = colors.HexColor('#0F172A')
MUTED = colors.HexColor('#64748B')
LIGHT = colors.HexColor('#EFF6FF')
BORDER = colors.HexColor('#BFDBFE')
SOFT = colors.HexColor('#F8FAFC')


def clean_filename(text):
    text = re.sub(r'[^a-zA-Z0-9_-]+', '_', text.strip())
    return text[:60] or 'plano_de_aula'


def clean_text(text):
    return (text or '').replace('**', '').replace('* ', '• ').replace('- ', '• ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def parse_sections(markdown_text):
    sections = []
    title = 'Conteúdo'
    lines = []
    for raw in markdown_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('# '):
            continue
        if line.startswith('## '):
            if lines:
                sections.append((title, '\n'.join(lines)))
            title = line.replace('## ', '').strip()
            lines = []
        else:
            lines.append(line)
    if lines:
        sections.append((title, '\n'.join(lines)))
    return sections


def cover(canvas, doc, meta):
    canvas.saveState()
    canvas.setFillColor(BLUE)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    logo_path = Path('assets/logo.png')
    if logo_path.exists():
        try:
            canvas.drawImage(str(logo_path), 2*cm, 22.1*cm, width=6.2*cm, height=4.4*cm, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 26)
    canvas.drawString(2*cm, 20.2*cm, 'Plano de Aula')
    canvas.setFont('Helvetica', 13)
    canvas.drawString(2*cm, 19.25*cm, 'Gerado com apoio pedagógico inteligente')
    canvas.setFillColor(CYAN)
    canvas.roundRect(2*cm, 17.5*cm, 4.8*cm, 0.9*cm, 10, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(2.32*cm, 17.78*cm, 'ODS 4 • Educação')
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 15)
    canvas.drawString(2*cm, 15.7*cm, str(meta.get('theme', 'Tema não informado'))[:76])
    y = 14.35*cm
    canvas.setFont('Helvetica', 11)
    for label, value in [('Professor', meta.get('teacher','Não informado')), ('Escola', meta.get('school','Não informada')), ('Componente', meta.get('subject','Não informado')), ('Ano/Série', meta.get('grade','Não informado')), ('Data', datetime.now().strftime('%d/%m/%Y %H:%M'))]:
        canvas.setFillColor(CYAN)
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(2*cm, y, label.upper())
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica', 11)
        canvas.drawString(5.2*cm, y, str(value)[:78])
        y -= .75*cm
    canvas.setFont('Helvetica', 9)
    canvas.drawString(2*cm, 2.2*cm, 'Desenvolvido por Lucas Lopes • ADS EAD • UNIFECAF')
    canvas.restoreState()


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(10.5*cm, 1.15*cm, f'EduPlan IA • Desenvolvido por Lucas Lopes • ADS EAD • UNIFECAF • Página {doc.page}')
    canvas.restoreState()


def key_value(line):
    if ':' in line and len(line.split(':', 1)[0]) <= 35:
        k, v = line.split(':', 1)
        return k.strip(), v.strip()
    return None


def escape_text(text):
    return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def format_line(line):
    line = line.strip().replace('**', '').replace('* ', '- ')
    m = re.match(r'^(\d+\.\s*[^:]{3,90}:)\s*(.*)$', line)
    if m:
        return f'<b>{escape_text(m.group(1))}</b> {escape_text(m.group(2))}'
    m = re.match(r'^(-\s*[^:]{3,90}:)\s*(.*)$', line)
    if m:
        return f'<b>{escape_text(m.group(1).replace("-", "•", 1))}</b> {escape_text(m.group(2))}'
    kv = key_value(line)
    if kv and not line.lower().startswith(('http', 'https')):
        return f'<b>{escape_text(kv[0])}:</b> {escape_text(kv[1])}'
    return clean_text(line)


def generate_pdf(title, content, meta=None):
    meta = meta or {}
    out = Path('exports')
    out.mkdir(exist_ok=True)
    path = out / f"{clean_filename(title)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=1.55*cm, leftMargin=1.55*cm, topMargin=1.5*cm, bottomMargin=1.75*cm)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=19, textColor=BLUE, spaceAfter=12)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.white, backColor=BLUE2, borderPadding=7, spaceBefore=13, spaceAfter=8, keepWithNext=True)
    body = ParagraphStyle('Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=9.4, leading=13.5, textColor=TEXT, spaceAfter=5, wordWrap='CJK')
    bullet = ParagraphStyle('Bullet', parent=body, leftIndent=12, firstLineIndent=-8, wordWrap='CJK')
    story = []
    logo_path = Path('assets/logo.png')
    if logo_path.exists():
        story.append(Image(str(logo_path), width=4.0*cm, height=3.0*cm, kind='proportional'))
    story.append(Paragraph('Plano de Aula', h1))
    meta_rows = [
        ['Professor', meta.get('teacher','Não informado'), 'Escola', meta.get('school','Não informada')],
        ['Componente', meta.get('subject','Não informado'), 'Ano/Série', meta.get('grade','Não informado')],
        ['Tema', meta.get('theme','Não informado'), '', ''],
        ['Geração', datetime.now().strftime('%d/%m/%Y %H:%M'), '', ''],
    ]
    meta_rows = [[Paragraph(f'<b>{escape_text(str(c))}</b>' if i in (0,2) else escape_text(str(c)), body) for i, c in enumerate(row)] for row in meta_rows]
    meta_table = Table(meta_rows, colWidths=[2.6*cm, 5.2*cm, 2.6*cm, 5.2*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),colors.white),
        ('BACKGROUND',(0,0),(0,-1),LIGHT),('BACKGROUND',(2,0),(2,1),LIGHT),
        ('BACKGROUND',(0,2),(0,3),LIGHT),
        ('TEXTCOLOR',(0,0),(0,-1),BLUE),('TEXTCOLOR',(2,0),(2,1),BLUE),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),('FONTNAME',(2,0),(2,1),'Helvetica-Bold'),
        ('SPAN',(1,2),(3,2)),('SPAN',(1,3),(3,3)),
        ('FONTSIZE',(0,0),(-1,-1),8.2),('GRID',(0,0),(-1,-1),0.4,BORDER),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)
    ]))
    story += [meta_table, Spacer(1,10), HRFlowable(width='100%', thickness=1, color=BORDER), Spacer(1,7)]
    for section, section_body in parse_sections(content):
        story.append(Paragraph(section.upper(), h2))
        kv_rows = []
        normal_items = []
        for raw in section_body.split('\n'):
            raw = raw.strip()
            if not raw: continue
            kv = key_value(raw)
            if kv and section.upper() == 'IDENTIFICAÇÃO':
                kv_rows.append([Paragraph(f'<b>{clean_text(kv[0])}</b>', body), Paragraph(clean_text(kv[1]), body)])
            else:
                style = bullet if raw.startswith('-') or raw.startswith('•') or re.match(r'^\d+\.', raw) else body
                normal_items.append(Paragraph(format_line(raw), style))
        if kv_rows:
            table = Table(kv_rows, colWidths=[4.2*cm, 11.2*cm])
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),SOFT),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#E2E8F0')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.append(table)
        story.extend(normal_items)
    story.append(Spacer(1,12))
    story.append(Paragraph('Observação: este documento foi gerado como apoio pedagógico e deve ser revisado pelo professor antes de sua aplicação.', ParagraphStyle('Note', parent=styles['Italic'], fontSize=8.7, textColor=MUTED)))
    doc.build([PageBreak()] + story, onFirstPage=lambda c,d: cover(c,d,meta), onLaterPages=footer)
    return str(path)
