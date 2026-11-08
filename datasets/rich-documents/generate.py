#!/usr/bin/env python3
"""Generate only the small, synthetic PDF corpus from the versioned sources."""
from pathlib import Path
import hashlib
import reportlab
import yaml
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent
VERSION = '4.4.10'

def generate(source: Path, output: Path) -> None:
    data = yaml.safe_load(source.read_text(encoding='utf-8'))
    pdf = canvas.Canvas(str(output), pagesize=A4, invariant=1, pageCompression=0)
    pdf.setTitle(data['title'])
    pdf.setAuthor('AegisOps AI — corpus sintético')
    for number, page in enumerate(data['pages'], 1):
        y = 790
        pdf.setFont('Helvetica-Bold', 14)
        pdf.drawString(45, y, data['title'])
        y -= 35
        for item in page:
            kind, value = item['kind'], item['content']
            if kind in ('heading', 'subheading', 'text'):
                pdf.setFont('Helvetica-Bold' if kind != 'text' else 'Helvetica', 12 if kind == 'heading' else 10)
                pdf.drawString(45, y, value)
                y -= 24 if kind != 'text' else 19
            elif kind == 'table':
                x = [45, 180, 355, 540]
                for index, row in enumerate([value['headers'], *value['rows']]):
                    pdf.setFont('Helvetica-Bold' if index == 0 else 'Helvetica', 10)
                    for col, cell in enumerate(row):
                        pdf.drawString(x[col] + 5, y - 15, cell)
                    y -= 25
                for xpos in x:
                    pdf.line(xpos, y, xpos, y + 75)
                for ypos in (y, y + 25, y + 50, y + 75):
                    pdf.line(x[0], ypos, x[-1], ypos)
                y -= 20
            elif kind == 'columns':
                for xpos, column in ((45, value['left']), (315, value['right'])):
                    for index, line in enumerate(column):
                        pdf.setFont('Helvetica-Bold' if index == 0 else 'Helvetica', 10)
                        pdf.drawString(xpos, y - index * 18, line)
                y -= 95
            else:
                raise ValueError(f'Item desconhecido: {kind}')
        pdf.setFont('Helvetica', 9)
        pdf.drawString(45, 35, f'{data["id"]} | página {number} | versão 1.0.0 | sintético')
        pdf.showPage()
    pdf.save()

def main() -> None:
    if reportlab.Version != VERSION:
        raise SystemExit(f'Requer ReportLab {VERSION}; encontrado {reportlab.Version}.')
    for source in sorted((ROOT / 'source').glob('RD-*.yaml')):
        output = ROOT / 'documents' / (source.stem + '.pdf')
        generate(source, output)
        print(f'{output.name} {hashlib.sha256(output.read_bytes()).hexdigest()}')

if __name__ == '__main__':
    main()
