import libQC_classes 
import pandas as pd
import os
#TODO JCE : handle exceptions
def getdata(mode, subpath) :
    # Read, format, and return usefull data for the selected project
    if mode==libQC_classes.Mode.TSV :
        # Get all tsv files 
        tsv_files = getTsv(subpath)
        # Format given data 
        dataframe = tsvToGlobalData(tsv_files)
        return dataframe

    elif mode==libQC_classes.Mode.HEADER :
        # Get all header files 
        header_files = getHeader(subpath)
        # Format given data 
        dataframe = headerToGlobalData(header_files)
        return dataframe

def  getTsv(subpath):
    tsv_files = []
    for folder_name in listFolder("../local_plankton/zooscan/"+subpath+"/Zooscan_scan/_work/") :
            print(folder_name)
            tsv_files.append(pd.read_csv("../local_plankton/zooscan/"+subpath+"/Zooscan_scan/_work/"+folder_name+"/ecotaxa_"+folder_name+".tsv", encoding = "ISO-8859-1", usecols=['sample_id','process_img_background_img'],sep="\t").drop(0))     
            print("can read file")
    return tsv_files

def  getHeader(subpath):
    header_files = []
    header_files.append(pd.read_csv("../local_plankton/zooscan/"+subpath+"/Zooscan_meta/zooscan_sample_header_table.csv", usecols=['sampleid', 'ship'], sep=";"))
    header_files.append(pd.read_csv("../local_plankton/zooscan/"+subpath+"/Zooscan_meta/zooscan_scan_header_table.csv", sep=";"))
    return header_files

def listFolder(path) :
    return os.listdir(path)

def tsvToGlobalData(tsv_files) : 
    #TODO JCE : generate from tsv a common structure of dataframe
    dataframe = pd.concat(tsv_files)
    return dataframe

def headerToGlobalData(header_files) : 
    #TODO JCE : generate from header a common structure of dataframe
    return header_files

def save_qc_execution(title, result):
    #TODO JCE : save as html (or pdf)
    return
