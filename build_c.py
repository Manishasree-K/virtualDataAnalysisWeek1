from docx import Document as D2
from docx.shared import Pt as P2, Inches as I2, RGBColor as R2
from docx.enum.text import WD_ALIGN_PARAGRAPH as A2
from docx.enum.table import WD_TABLE_ALIGNMENT as T2
from docx.oxml.ns import qn as Q2
from docx.oxml import OxmlElement as O2
doc = D2('stage1_tmp.docx')
NAVY = R2(0x1B, 0x3A, 0x5C); ACCENT = R2(0x0E, 0x7C, 0x6B)
def shade2(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = O2('w:shd')
    shd.set(Q2('w:fill'), color); shd.set(Q2('w:val'), 'clear')
    tcPr.append(shd)
def para(text, bold=False, size=10.5, color=None, align=None, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold; r.italic = italic; r.font.size = P2(size)
    if color: r.font.color.rgb = color
    if align: p.alignment = align
    return p
def bullet(text, head=None):
    p = doc.add_paragraph(style='List Bullet')
    if head:
        a = p.add_run(head); a.bold = True; a.font.size = P2(10.5)
        b = p.add_run(text); b.font.size = P2(10.5)
    else:
        a = p.add_run(text); a.font.size = P2(10.5)
    return p
def table(headers, rows):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'; t.alignment = T2.CENTER
    import docx.shared as _sh
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ''
        r = c.paragraphs[0].add_run(h)
        r.bold = True; r.font.size = P2(9.5)
        shade2(c, '1B3A5C')
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = P2(9.2)
    doc.add_paragraph()
    return t
def h1b(num, title):
    h = doc.add_heading(level=1); h.text = ''
    r = h.add_run(num + '  ' + title)
    r.font.color.rgb = NAVY; r.font.size = P2(15)
def h2b(title):
    h = doc.add_heading(level=2); h.text = ''
    r = h.add_run(title)
    r.font.color.rgb = ACCENT; r.font.size = P2(12)
END_HDR = 1
h1b('5.', 'Analytical Framework & Methodology')
para('CRISP-DM flow with two quality gates (G1 data readiness, G2 insight readiness).', size=10.5)
para('UNDERSTAND -> COLLECT -> CLEAN [G1] -> EXPLORE -> MODEL [G2] -> EVALUATE -> INSIGHT', bold=True, size=9.5, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER)
h2b('5.1 Data collection')
table(['Source', 'Captured', 'Method', 'Ethics'], [['Logs', 'ID, service, time, status, channel', 'API/DB extract to CSV', 'Minimise PII; role access'], ['Feedback', 'CSAT 1-5, grievance text', 'Survey + helpline export', 'Consent; optional'], ['Admin', 'District, staffing, CSC hours', 'Dept template', 'Authorisation'], ['Context', 'Aggregates only', 'Census/telecom', 'No linkage']])
para('Week-1 sampling is stratified by service x channel (n=500+) so Kiosk/CSC minorities survive. Full project: 12-month extract, monthly refresh.', size=10)
h2b('5.2 Statistical methods')
table(['Question', 'Method', 'Tool', 'Output'], [['Baseline?', 'Descriptives; SLA%; funnels', 'pandas/matplotlib', 'KPI cards'], ['Group gaps?', 'Chi-square; ANOVA/Kruskal', 'scipy', 'League tables'], ['CSAT drivers?', 'Spearman; ordinal logit', 'statsmodels', 'Driver ranking'], ['Segments?', 'K-means + profiles', 'sklearn', '3-4 personas'], ['SLA breach?', 'LogReg vs RF, CV', 'sklearn', 'Risk score']])
h2b('5.3 Reproducibility')
bullet('Python 3.10+: pandas, numpy, matplotlib, sklearn, scipy, python-docx.', head='Stack - ')
bullet('seeded scripts; raw never edited; log auto-written.', head='Discipline - ')
h2b('5.4 Gates')
table(['Gate', 'Test'], [['G1 data readiness', 'Nulls <1%; dups 0; dates 95%+ parsed'], ['G2 insight readiness', 'Dashboard reviewed; F1 reported; limits logged']])
h1b('6.', 'Data Cleaning & Preprocessing Framework')
para('Theory first, then exactly how the script resolves each issue.', size=10.5)
h2b('6.1 Detection (how issues are found)')
table(['Dimension', 'Rule', 'Found in raw sample'], [['Completeness', 'isnull().sum(); flag >5%', 'district 73, channel 105, CSAT 39 nulls'], ['Uniqueness', 'duplicated() on business key', '9 duplicate rows'], ['Consistency', 'value_counts variants', 'Completed/completed/COMPLETED; lucknow vs Lucknow'], ['Validity', 'ranges: age 18-100; time>=0', 'ages 5,-3,120,200; times 250,-5; bad dates'], ['Outliers', 'percentile review; cap 60d', '7 cases >60 days'], ['Timeliness', "mixed-format parse", '12 unparseable dates']])
h2b('6.2 Resolution (how fixed + why)')
table(['Issue', 'Fix', 'Why'], [['Text', 'strip + Title + map (Itr->ITR)', 'Reversible; logged'], ['Dups', 'drop_duplicates, keep first', 'Stops double count (9 cut)'], ['Ages', 'null bad -> median 50', 'Robust; no sample bias'], ['Times', 'neg->median; >60 cap p99', 'Keeps backlog signal'], ['CSAT', 'service-wise median', 'Least-biased impute'], ['Dates', 'coerce mixed -> fallback', '12 counted + filled'], ['Blanks', "fill 'Unknown'", 'Mode would inflate bias']])
para('Result: 510 rows -> 501; nulls 177 -> 0; dups 9 -> 0. Full log in cleaning_report.txt.', bold=True, size=10)
h2b('6.3 Preprocessing for modelling')
bullet('one-hot encode nominals; scale time for distance models.', head='Encode/scale - ')
bullet('stratified split + 5-fold CV; class weights.', head='Validation - ')
doc.save('stage2_tmp.docx')
print('stage2 ok')
