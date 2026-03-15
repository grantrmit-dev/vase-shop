#!/usr/bin/env python3
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

BASE=Path('/home/han/.openclaw/workspace/FBG Brochure')
IMGDIR=BASE/'product images'
OUT=Path('/tmp/FBG_Brochure_v2.pdf')

def draw_cover(c):
    w,h=A4
    c.setFont('Helvetica-Bold',26)
    c.drawString(48,h-90,'Ultrafast FBG Product Brochure')
    c.setFont('Helvetica',12)
    c.drawString(48,h-115,'Version 2 — images integrated in extracted order')

def draw_image_page(c, img_path, idx):
    w,h=A4
    c.setFont('Helvetica-Bold',14)
    c.drawString(48,h-50,f'Product Image {idx}')
    img=ImageReader(str(img_path))
    iw,ih=img.getSize()
    maxw=w-96; maxh=h-140
    scale=min(maxw/iw,maxh/ih)
    nw,nh=iw*scale,ih*scale
    x=(w-nw)/2
    y=(h-nh)/2-20
    c.drawImage(img,x,y,nw,nh,preserveAspectRatio=True,anchor='c')
    c.setFont('Helvetica',9)
    c.drawString(48,28,img_path.name)


def main():
    images=sorted(IMGDIR.glob('*.jpg'))
    c=canvas.Canvas(str(OUT), pagesize=A4)
    draw_cover(c)
    c.showPage()
    for i,p in enumerate(images,1):
        draw_image_page(c,p,i)
        c.showPage()
    c.save()
    print(OUT)
    print('images_used',len(images))

if __name__=='__main__':
    main()
