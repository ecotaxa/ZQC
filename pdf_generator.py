# coding: utf-8
from datetime import datetime
from fpdf import FPDF
import pandas as pd
from PIL import Image
from datetime import datetime

  

from enums import SUPPORTED_DATA_COMPONANT
import localData

SPACING = 1

def centred_h1(pdf,title):
    set_font_size(pdf,'', 24)
    #pdf.set_text_color(16, 105, 141)
    # Calculate width of title and position
    string_width = pdf.get_string_width(title) + 6
    pdf.set_x((pdf.w - string_width) / 2)
    #write centred title
    pdf.cell(string_width, 9, title, 0, 1, 'C')

def centred_h2(pdf,title):
    set_font_size(pdf,'', 17)
    # Calculate width of title and position
    string_width = pdf.get_string_width(title) + 6
    pdf.set_x((pdf.w - string_width) / 2)
    #write centred title
    pdf.cell(string_width, 9, title, 0, 1, 'C')

def h4_with_email(pdf, operator):
    # Split the title into parts
    part1 = "Saved by " + operator["name"] + " " + operator["last_name"] + " ("
    email = operator["email"]
    part2 = ") on " + datetime.utcnow().strftime("%d/%m/%Y at %I:%M:%S %p")

    # Set initial font and color for part1
    set_font_size(pdf, '', 10)
    pdf.set_text_color(51, 51, 51)

    # Write part1
    pdf.write(5,part1)
    # Set font and color for email
    pdf.set_text_color(0, 0, 255)  # Blue color
    pdf.set_font('', 'U')  # Underline

    # Write email
    pdf.write(5,email)

    # Reset font and color for part2
    pdf.set_font('', '')  # Remove underline
    pdf.set_text_color(51, 51, 51)

    # Write part2
    pdf.write(5,part2)

def generate_checks_block(checks):
    checks_layout = ""
    for check in checks:
            checks_layout+= check["title"] + "\n"
            checks_layout+= check["description"] + "\n"
    return checks_layout

def generate_sub_block(sub_block):
    sub_block_layout = ""
    sub_block_layout += sub_block["title"] + " \n"
    sub_block_layout += sub_block["description"] + " \n"+ "\n"
    sub_block_layout += generate_checks_block(sub_block["checks"])
    return sub_block_layout 


def generate_details(checkBlock):
    block_layout = ""
    for sub_block in checkBlock["blocks"]:
        block_layout += generate_sub_block(sub_block) 
    return block_layout

def write_multiline_report_info(pdf, block, ratio=1.5):
    print(block)
    text = generate_details(block)
    print(text)
    set_font_size(pdf,'', 10)
    pdf.set_text_color(51, 51, 51)
    pdf.multi_cell(0, 10, text, align="L", border=1  , max_line_height=pdf.font_size *ratio*SPACING)

def set_font_size(pdf, weight, size):
    pdf.set_font('ArialUnicode', weight, size)

def write_spacing(pdf, ratio=1.5):
    pdf.ln(pdf.font_size * ratio*SPACING)

def write_h3(pdf, text, mode=''):
    #b for bold, u for underline, i for italic, '' for regular
    set_font_size(pdf, mode, 14)
    pdf.set_text_color(51, 51, 51)
    pdf.write(4, text) 
   
def write_h4(pdf, text, mode=''):
    #b for bold, u for underline, i for italic, '' for regular
    set_font_size(pdf, mode, 16)
    pdf.set_text_color(92, 192, 205)
    pdf.write(5,text)

def write_text(pdf, text, mode=''):
    #b for bold, u for underline, i for italic, '' for regular
    set_font_size(pdf, mode, 12)
    pdf.set_text_color(51, 51, 51)
    pdf.write(4, text) 

def write_images(pdf, images):
    default_images_line_height = 24
    current_x = pdf.get_x()
    current_y = pdf.get_y()
    page_width = pdf.w - 2 * pdf.l_margin
    SPACING_IMG = 10
    BIG_LOGO_RATIO = 9

    # Function to calculate total width of images at a given line height
    def total_images_width():
        total_width = 0
        for image in images:
            img = Image.open(image)
            images_line_height = default_images_line_height + BIG_LOGO_RATIO if image == "assets/PIQV.png" else default_images_line_height
            scale_factor = images_line_height / img.height
            total_width += (img.width * scale_factor)
        total_width += SPACING_IMG * (len(images) - 1)  # Add spacing between images
        return total_width

    # Adjust line height if images don't fit
    while total_images_width() > page_width:
        default_images_line_height -= 1  # Decrease line height
        if default_images_line_height <= 0:
            raise ValueError("Images cannot fit within the page width.")

    # Render images at adjusted line height
    for image in images:
        img = Image.open(image)
        images_line_height = default_images_line_height + BIG_LOGO_RATIO if image == "assets/PIQV.png" else default_images_line_height
        scale_factor = images_line_height / img.height
        scaled_width = img.width * scale_factor
        # Rendering image
        pdf.image(image, x=current_x, y=current_y, h=images_line_height)
        current_x += scaled_width + SPACING_IMG

    pdf.set_y(current_y + default_images_line_height)
    pdf.ln(default_images_line_height * 2)
class PDF(FPDF):
    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        col_width = self.epw/10
        self.set_y(-15)
        self.set_font_size(8)
        self.set_text_color(51, 51, 51)
        # Printing piqv adress
        self.multi_cell(0, 10, "Quantitative Imaging Platform \nStation Zoologique - 181 chemin du Lazaret \n06230 Villefranche sur Mer - France \n\n✉ piqv@imev-mer.fr", align="C", max_line_height=self.font_size *1.1*SPACING)
        # Printing page number:
        self.cell(0, 1, f"Page {self.page_no()}|{{nb}}", align="R")

def write_multiline_datatable_XL(pdf, df):
    # distribute content depending of the nuber of dataset's cols
    col_width = pdf.epw /(len(df.columns)-1)
    write_multiline_datatable(pdf, df, col_width)
    return

    
def write_multiline_datatable_XS(pdf, df):
    # distribute content in small cols
    col_width = pdf.epw /10
    write_multiline_datatable(pdf, df, col_width)
    return

def write_multiline_datatable(pdf, df, col_width):
    write_spacing(pdf)  
    write_multiline_row_headers(df.head(), pdf, col_width)
    # for row in data
    for i in df.index :
        row=[]
        # Get row content
        for index in df.head() :
            if index!="index" :
                row.append(str(df[index][i]))
        write_multiline_row_content(row, pdf, col_width)
           
    return
    
def write_multiline_row_headers(headers, pdf, col_width):
    # set font suporting "!=" symbol
    set_font_size(pdf, 'B', 10)
    line_height = pdf.font_size * 1.5
    pdf.set_text_color(0,0,0)
    # table header :
    row=[]
    for col_name in headers :
        if col_name!="index" :
            row.append(col_name)
    write_multiline_row(row, pdf, line_height, col_width)

def write_multiline_row_content(row, pdf, col_width):
    # set font suporting "!=" symbol
    set_font_size(pdf, '', 10)
    line_height = pdf.font_size * 1.5
    pdf.set_text_color(51, 51, 51)
    write_multiline_row(row, pdf, line_height, col_width)

def write_multiline_row(row, pdf, line_height, col_width):
    row_height_lines = 1
    lines_in_row = []
    # determine height of highest cell in the row
    for datum in row: 
        output = pdf.multi_cell(col_width, line_height, datum, border=1, ln=3, split_only=True)
        lines_in_row.append(len(output))
        if len(output) > row_height_lines:
            row_height_lines = len(output)

    if pdf.will_page_break(row_height_lines * line_height):
            pdf.add_page()
    for tlines , datum in zip(lines_in_row, row):
        # Adjust text
        text =datum.rstrip('\n') + (1 + row_height_lines - tlines) * '\n'

        # Set error label color to red
        if text.startswith("#") :
            pdf.set_text_color(237, 67, 55)
            pdf.multi_cell(col_width, line_height, text, border=1, ln=3)
            pdf.set_text_color(51, 51, 51)
        else :
            pdf.multi_cell(col_width, line_height, text, border=1, ln=3)

    pdf.ln(row_height_lines * line_height)

def create_pdf_report_for_project(project, block, operator):
    pdf = PDF(block["pdf_orientation"],'mm', 'A4')
    ## https://github.com/reingart/pyfpdf/issues/86
    pdf.add_font('ArialUnicode',fname='assets/fonts/Arial-Unicode-Regular.ttf',uni=True)
    pdf.add_font('ArialUnicode', style='B', fname='assets/fonts/Arial-Unicode-Bold.ttf',uni=True)
    set_font_size(pdf, '', 12)
    pdf.set_text_color(51, 51, 51)
    ##
    pdf.add_page()
    write_images(pdf, ["assets/LOV.png", "assets/IMEV.png", "assets/PIQV.png", "assets/CNRS.png", "assets/SU.png", "assets/EMBRC.png" ])
    centred_h1(pdf, "ZQC Report : "+ block["title"])
    write_spacing(pdf,0.2)
    centred_h2(pdf, block["description"])
    write_spacing(pdf,0.7)
    h4_with_email(pdf,operator)
    write_spacing(pdf, 7)
    write_h3(pdf,"Project tested : ")
    write_spacing(pdf)
    write_h3(pdf,project,'b')
    write_spacing(pdf)
    write_spacing(pdf)
    write_multiline_report_info(pdf, block["list_checks"])
    return pdf

def add_sub_block_execution(pdf, title, data):
    """Save an execution as html (or pdf)"""
    write_h4(pdf, title)
    for result in data:
        if result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE :
            df = pd.DataFrame.from_dict(result["dataframe"]).reset_index()  # make sure indexes pair with number of rows
            write_multiline_datatable_XL(pdf, df)
        elif result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE_XS:
            df = pd.DataFrame.from_dict(result["dataframe"]).reset_index()  # make sure indexes pair with number of rows
            write_multiline_datatable_XS(pdf, df)
    write_spacing(pdf, 2)
def save_pdf(pdf, path, title):
    localData.saveQcExecution(pdf, path, title)

def generate(pdfs_data):
    execution_data=[]
    for data in pdfs_data :
        if len(data["subBlocks"]) > 0 :
            pdf = create_pdf_report_for_project(data["project"], data["block"], data["operator"])
            for subBlock in data["subBlocks"] :
                add_sub_block_execution(pdf, subBlock["title"], subBlock["data"])
            save_pdf(pdf, data["path"], data["title"])
            execution_data.append({"type" : "SUCESS", "title" : "Saved file", "message" : data["path"] +"Zooscan_reports/" + data["title"] + ".pdf"})
    return execution_data
    #return {"type" : "ERROR", "title" : "Can't save file", "message" : data["path"] + data["title"] + ".pdf"}
