import libQC_classes 
import pandas as pd
import os

def getdata(mode, subpath) :
    if mode==libQC_classes.Mode.TSV :
        #get all tsv files 
        tsv_files = getTsv(subpath)
        dataframe = tsvToGlobalData(tsv_files)
        return dataframe

    elif mode==libQC_classes.Mode.HEADER :
        #TODO JCE read and return usefull data for the selected project in header mode ie: in Zooscan_meta folder
        #get all header files 
        header_files = getHeader(subpath)
        dataframe = headerToGlobalData(header_files)
        return dataframe

def  getTsv(subpath):
    tsv_files = []
    for folder_name in listFolder("../local_plankton/zooscan/"+subpath+"/Zooscan_scan/_work/") :
            tsv_files.append(pd.read_csv("../local_plankton/zooscan/"+subpath+"/Zooscan_scan/_work/"+folder_name+"/ecotaxa_"+folder_name+".tsv", usecols=['sample_id','process_img_background_img'],sep="\t").drop(0))     
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