"""Build 6" x 6" ShowMojo booking QR stickers from units.csv.

Usage:  python3 build.py
Needs:  pip install qrcode reportlab pillow

Outputs (all regenerated every run):
  stickers/<address>.pdf   one sticker per unit, vector, 6.00 x 6.00 in
  stickers/<address>.png   same sticker, 1800 x 1800 px (300 dpi)
  print/<batch>.pdf        every sticker added in that month's batch
  print/all-active.pdf     every unit marked active=yes
"""
import csv
import os
import re

import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 6.0 * inch          # sticker is exactly 6.00" x 6.00"
BORDER = 3                 # white quiet zone around the code, in QR modules
DPI = 300
LABEL_PT = 7               # tiny property label along the bottom edge
LABEL_FROM_BOTTOM = 0.07 * inch
LABEL_GRAY = "#555555"


def url_for(lid):
    return f"https://showmojo.com/l/{lid}"


def label_for(u):
    place = u["address"] + (f", {u['unit']}" if u["unit"] else "")
    return f"{place}  •  ShowMojo {u['showmojo_id']}"


def slug(u):
    return re.sub(r"[^A-Za-z0-9]+", "-", f"{u['address']} {u['unit']}".strip()).strip("-")


def matrix(lid):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=BORDER)
    q.add_data(url_for(lid))
    q.make(fit=True)
    return q.get_matrix()


def draw_pdf_page(c, u):
    m = matrix(u["showmojo_id"])
    n = len(m)
    mod = SIZE / n
    c.setFillColor(white)
    c.rect(0, 0, SIZE, SIZE, stroke=0, fill=1)
    c.setFillColor(black)
    for r, row in enumerate(m):
        i = 0
        while i < n:
            if row[i]:
                s = i
                while i < n and row[i]:
                    i += 1
                c.rect(s * mod, (n - 1 - r) * mod, (i - s) * mod + 0.15, mod + 0.15, stroke=0, fill=1)
            else:
                i += 1
    c.setFillColor(HexColor(LABEL_GRAY))
    c.setFont("Helvetica", LABEL_PT)
    c.drawCentredString(SIZE / 2, LABEL_FROM_BOTTOM, label_for(u))
    c.showPage()


def write_png(u, path):
    m = matrix(u["showmojo_id"])
    n = len(m)
    px = int(6 * DPI)
    img = Image.new("RGB", (px, px), "white")
    d = ImageDraw.Draw(img)
    for r, row in enumerate(m):
        for col, v in enumerate(row):
            if v:
                d.rectangle([round(col * px / n), round(r * px / n),
                             round((col + 1) * px / n) - 1, round((r + 1) * px / n) - 1], fill="black")
    size = round(LABEL_PT / 72 * DPI)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    text = label_for(u)
    w = d.textlength(text, font=font)
    y = px - round(LABEL_FROM_BOTTOM / inch * DPI) - size
    d.text(((px - w) / 2, y), text, fill=LABEL_GRAY, font=font)
    img.save(path, dpi=(DPI, DPI))


def build_pdf(path, units, title):
    c = canvas.Canvas(path, pagesize=(SIZE, SIZE))
    c.setTitle(title)
    for u in units:
        draw_pdf_page(c, u)
    c.save()


def main():
    with open(os.path.join(HERE, "units.csv"), newline="") as f:
        units = [u for u in csv.DictReader(f) if u["showmojo_id"].strip()]
    for u in units:
        for k in u:
            u[k] = (u[k] or "").strip()

    sdir = os.path.join(HERE, "stickers")
    pdir = os.path.join(HERE, "print")
    os.makedirs(sdir, exist_ok=True)
    os.makedirs(pdir, exist_ok=True)

    for u in units:
        build_pdf(os.path.join(sdir, slug(u) + ".pdf"), [u], label_for(u))
        write_png(u, os.path.join(sdir, slug(u) + ".png"))

    for batch in sorted({u["batch"] for u in units}):
        group = [u for u in units if u["batch"] == batch]
        build_pdf(os.path.join(pdir, f"{batch}.pdf"), group, f"ShowMojo QR stickers - {batch}")
    active = [u for u in units if u["active"].lower() == "yes"]
    build_pdf(os.path.join(pdir, "all-active.pdf"), active, "ShowMojo QR stickers - all active")
    print(f"{len(units)} stickers, {len(active)} active")


if __name__ == "__main__":
    main()
