# coding: utf-8
from datetime import datetime
from fpdf import FPDF
import pandas as pd

from enums import SUPPORTED_DATA_COMPONANT
import localData

SPACING = 1


def set_font_size(pdf, weight, size):
    pdf.set_font('ArialUnicode', weight, size)

def write_title(pdf, text):
    set_font_size(pdf,'', 24)
    pdf.set_text_color(16, 105, 141)
    pdf.write(5,text)
    pdf.ln(pdf.font_size * 1.5*SPACING)

def write_sub_title(pdf, text):
    set_font_size(pdf, '', 16)
    pdf.ln(pdf.font_size * 1.5*SPACING)    
    pdf.set_text_color(92, 192, 205)
    pdf.write(5,text)

def write_text(pdf, text):
    set_font_size(pdf, '', 12)
    pdf.ln(pdf.font_size * 1.5*SPACING)
    pdf.set_text_color(51, 51, 51)
    pdf.write(4, text) 

def write_multiline_datatable(pdf, df):
    # distribute content depending of the nuber of dataset's cols
    col_width = pdf.epw /10#(len(df.head())+4)
    pdf.ln(pdf.font_size * 1.5*SPACING)
    
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

def create_pdf_report_for_project(project):
    pdf = FPDF('L','mm', 'A4')
    ## https://github.com/reingart/pyfpdf/issues/86
    pdf.add_font('ArialUnicode',fname='assets/fonts/Arial-Unicode-Regular.ttf',uni=True)
    pdf.add_font('ArialUnicode', style='B', fname='assets/fonts/Arial-Unicode-Bold.ttf',uni=True)
    set_font_size(pdf, '', 12)
    pdf.set_text_color(51, 51, 51)
    ##
    pdf.add_page()
    write_title(pdf, project)
    return pdf

def add_sub_block_execution(pdf, title, data):
    """Save an execution as html (or pdf)"""
    write_sub_title(pdf, title)

    for result in data:
        if result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE or result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE_XS:
            df = pd.DataFrame.from_dict(result["dataframe"]).reset_index()  # make sure indexes pair with number of rows
            write_multiline_datatable(pdf, df)

def save_pdf(pdf, path, title):
    localData.saveQcExecution(pdf, path, title)

def generate(pdfs_data):
    for data in pdfs_data :
        print(data)
        pdf = create_pdf_report_for_project(data["project"])
        for subBlock in data["subBlocks"] :
            add_sub_block_execution(pdf, subBlock["title"], subBlock["data"])
        save_pdf(pdf, data["path"], data["title"])
