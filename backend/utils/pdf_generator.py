import uuid
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_pdf(title, lines):

    folder = os.path.join(os.getcwd(), "temp")
    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(folder, f"{uuid.uuid4().hex}.pdf")

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, title)
    y -= 30

    c.setFont("Helvetica", 10)

    for line in lines:
        if not line.strip():
            y -= 10
            continue

        c.drawString(50, y, line[:90])
        y -= 15

        if y < 40:
            c.showPage()
            y = height - 50

    c.save()

    return filename