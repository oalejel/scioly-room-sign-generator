#!/usr/bin/env python
"Make Science Olympiad room signs."

"""
FOR EVENT SIGNS:
list all event names in ALPHABETICAL ORDER in indexed-event-names.json if some titles are too long, place a
newline character (forward slash n) to separate the indexed-images folder should
contain images named after their events. This program matches images with event 
names by alphabetically ordering the image names. Make names lower-case letters.

Example: { "event-names": [ ... ] }

NOTE: check to make sure images match titles after running!


FOR HOMEROOM SIGNS:
It's ok if you have duplicate team names; the program will throw those out.
Make sure school-names has an array of strings with key "school-names"
Example: { "school-names": [ ... ] }

NOTE: you can also include room names like "GRADING ROOM" in the array.
"""

import os
from sys import argv

from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize
import json

# filled later in program
event_names = list()
school_names = list()

# define some dimensions
point = 1
inch = 72
PAGE_WIDTH  = 8.5 * inch
PAGE_HEIGHT = 11 * inch
MARGIN = 0.5 * inch

# inserts newlines to make text fit width of a page 
# goals: 1) minimize number of newlines 
#        2) maximize width used in text without splitting words
def fit_text_to_width(canv, max_width, text):
    words = text.split(' ')
    word_widths = [canv.stringWidth(w) for w in words]
    space_width = canv.stringWidth(' ')

    index = 0
    while index < len(word_widths):
        width = word_widths[index]
        # furthest index of words to include.
        # inclusion_index - index is number of spaces to consider
        inclusion_index = index
        
        # if we can fit more words in this line
        if width < max_width:
            while inclusion_index < len(word_widths):
                # see what the width of adding the next word (with spaces) is
                words_sum = sum(word_widths[index:inclusion_index + 2])
                space_sum = space_width * (inclusion_index - index)
                test_sum = words_sum + space_sum
                if test_sum <= max_width:
                    inclusion_index += 1
                else:
                    break
        # once we have optimize the placement of a newline, modify 
        # the words array to place a newline symbol at the end of the last word
        if inclusion_index < len(word_widths) - 1:
            words[inclusion_index] += '\n'
        
        index = inclusion_index
        index += 1
        
    # insert spaces in relevant places
    for i in range(0, len(words) - 1):
        if words[i][-1] != '\n':
            words[i] += ' '
    
    # then join our padded words
    return "".join(words)

def make_event_pdf(output_filename, event_name, img_name):
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
    
    width_limit = PAGE_WIDTH - (2*MARGIN)
    adjusted_text = fit_text_to_width(c, width_limit, event_name)
    
    vertical_offset = PAGE_HEIGHT - title_height * 3.4
    lines = adjusted_text.split('\n')
    vertical_offset += (float(len(lines)) // 2) * title_height
    
    for subtline in lines:
        c.drawCentredString(PAGE_WIDTH * 0.5, vertical_offset, subtline)
        vertical_offset -= title_height
    print(lines)

    c.showPage()
    c.save()
    
def generate_event_signs():
    try:
        with open('indexed-event-names.json') as f:
            event_names = json.load(f)["event-names"]
    except:
        print("File not found: indexed-event-names.json")
        print("This script needs this file to generate PDFs.")
    
    # make a folder for event pdfs 
    if not os.path.exists("event-pdfs-output"):
        os.mkdir("event-pdfs-output")
        
    # sort event names in case people don't read instructions ;)
    event_names.sort()
    
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
        make_event_pdf("event-pdfs-output/{}".format(filename), event, img_name)
        print("Wrote", filename)
        
def make_homeroom_pdf(output_filename, school_name):
    global PAGE_WIDTH, PAGE_HEIGHT 
    # swap to draw in landscape 
#    PAGE_WIDTH, PAGE_HEIGHT = PAGE_HEIGHT, PAGE_WIDTH
    
    c = canvas.Canvas(output_filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    c.setStrokeColorRGB(0,0,0)
    c.setFillColorRGB(0,0,0)
    registerFont(TTFont('UniversCondensed','univcond.ttf'))
    
    # add a header that says Science Olympiad with our logo on right 
    header_text_height = 25
    c.setFont("UniversCondensed", header_text_height)
    c.drawString(MARGIN, PAGE_HEIGHT - (MARGIN + header_text_height), "UMSO")
    
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
    title_width = c.stringWidth(school_name)
    title_height = 100 * point
    # set our title font to 100 pts
    c.setFont("UniversCondensed", title_height)
    
    width_limit = PAGE_WIDTH - (2*MARGIN)
    adjusted_text = fit_text_to_width(c, width_limit, school_name)
    
    vertical_offset = PAGE_HEIGHT - title_height * 4
    lines = adjusted_text.split('\n')
    vertical_offset += (len(lines) // 2) * title_height
    
    for subtline in lines:
        c.drawCentredString(PAGE_WIDTH * 0.5, vertical_offset, subtline)
        vertical_offset -= title_height
    
    # add soinc logo at bottom 
    # draw icon in top right
    c.drawImage("soinc-logo.png", 
                x=MARGIN, 
                y=25,
                width=width_limit,
                height=200,
                preserveAspectRatio=True);
    
    c.showPage()
    c.save()
    
    # undo our flip for landscape
#    PAGE_WIDTH, PAGE_HEIGHT = PAGE_HEIGHT, PAGE_WIDTH
        
def generate_homeroom_signs():
    try:
        with open('school-names.json') as f:
            school_names = json.load(f)["school-names"]
    except:
        print("File not found: school-names.json")
        print("This script needs this file to generate homeroom PDFs.")
    
    # make a folder for homeroom pdfs 
    if not os.path.exists("homeroom-pdfs-output"):
        os.mkdir("homeroom-pdfs-output")
        
    for name in school_names:
        filename = "homeroom-pdfs-output/{}.pdf".format(name)
        filename.replace('\n', '')
        filename.replace(' ', '')
        make_homeroom_pdf(filename, name)
        
if __name__ == "__main__":
    # unconditionally regenerate all
    # consider reading arguments to decide which of the two to print
    generate_homeroom_signs()
    generate_event_signs()
        
