#!/usr/bin/env python
"Make Science Olympiad room signs."

"""
list all event names in alphabetical order if some titles are too long, place a
newline character (forward slash n) to separate the indexed-images folder should
contain images named after their events. This program matches images with event 
names by alphabetically ordering the image names. Make names lower-case letters.

NOTE: check to make sure images match titles after running!
"""

import os
from sys import argv

from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize
import json

event_names = list()
try:
    with open('indexed-event-names.json') as f:
        event_names = json.load(f)["event-names"]
except:
    print("File not found: indexed-event-names.json")
    print("This script needs this file to generate PDFs.")


# define some dimensions
point = 1
inch = 72
PAGE_WIDTH  = 8.5 * inch
PAGE_HEIGHT = 11 * inch
MARGIN = 0.5 * inch

def make_pdf_file(output_filename, event_name, img_name):
    c = canvas.Canvas(output_filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    c.setStrokeColorRGB(0,0,0)
    c.setFillColorRGB(0,0,0)
    registerFont(TTFont('UniversCondensed','univcond.ttf'))
    
    # draw event image in bottom center 
    c.drawImage(img_name, 
                x=MARGIN, 
                y=50, 
                width=PAGE_WIDTH - (2 * MARGIN),
                height=300,
                preserveAspectRatio=True)
    
    # add a header that says Science Olympiad with our logo on right 
    header_text_height = 25
    c.setFont("UniversCondensed", header_text_height)
    c.drawString(MARGIN, PAGE_HEIGHT - (MARGIN + header_text_height), "Science Olympiad")
    
    # draw icon in top right
    img_aspect_ratio = 1.10376 # height / 1.10376
    img_width = 60.0
    c.drawImage("icon.png", 
                x=PAGE_WIDTH-(MARGIN + img_width), 
                y=PAGE_HEIGHT-(img_width * img_aspect_ratio + MARGIN), 
                width=img_width, 
                height=img_width*img_aspect_ratio)
    
    # we want vertical center of grouped title, that may be multiline
    # to be at height (PAGE_HEIGHT - title_height * 3.5)
    # must compute an offset from this centering if we have multiple lines to write for the title
    # get estimated width and height of title 
    title_width = c.stringWidth(event_name)
    title_height = 100 * point
    # set our title font to 100 pts
    c.setFont("UniversCondensed", title_height)
    
    vertical_offset = PAGE_HEIGHT - title_height * 3.4
    lines = event_name.split('\n')
    vertical_offset += (len(lines) // 2) * title_height
    
    for subtline in lines:
        c.drawCentredString(PAGE_WIDTH * 0.5, vertical_offset, subtline)
        vertical_offset -= title_height
        
    c.showPage()
    c.save()

if __name__ == "__main__":
    # make a folder for output pdfs 
    if not os.path.exists("output-pdfs"):
        os.mkdir("output-pdfs")
        
    # if no images folder, the complain
    image_names = list()
    try:
        image_names = os.listdir("images")
        image_names.sort() # sort alphabetically
        # then remove any hidden files
        image_names = [i for i in image_names if i[0] != '.']
    except:
        print("Missing images folder!")
    
    for index, event in enumerate(event_names):
        filename = "{}-room.pdf".format(event.replace('\n', ''))
        img_name = "images/{}".format(image_names[index])
        make_pdf_file("output-pdfs/{}".format(filename), event, img_name)
        print("Wrote", filename)