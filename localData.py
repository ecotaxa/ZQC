import libQC_classes 
import pandas as pd
import os
import errors_labels

def getdata(mode, subpath) :
    """Read, format, and return usefull data for the selected project"""
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
    """Read all ecotaxa tables (tsv files) for the given project. Return them as list of pandas dataframes"""
    tsv_files = []
    for folder_name in listFolder("../local_plankton/zooscan/"+subpath+"/Zooscan_scan/_work/") :
            try: 
                df = pd.read_csv("../local_plankton/zooscan/"+subpath+"/Zooscan_scan/_work/"+folder_name+"/ecotaxa_"+folder_name+".tsv", encoding = "ISO-8859-1", usecols=['sample_id','process_img_background_img'],sep="\t")
                df['STATUS']="Ecotaxa table OK"
                df['scan_id'] = folder_name
                tsv_files.append(df.drop(0))  
            except IOError as e:
                #si on a pas le .tsv on a pas les samples id : que faire? #TODO JCE
                df = pd.DataFrame(data={'scan_id': [folder_name], 'STATUS': errors_labels.errors["global.missing_ecotaxa_table"]})            
                tsv_files.append(df)
                print(e)
    return tsv_files

def  getHeader(subpath):
    """Read the two header tables for the given project. Return them as list of pandas dataframes"""
    header_files = []
    # Read sample header table
    try: 
        df = pd.read_csv("../local_plankton/zooscan/"+subpath+"/Zooscan_meta/zooscan_sample_header_table.csv", encoding = "ISO-8859-1", usecols=['sampleid', 'ship'], sep=";")
        header_files.append(df)  
    except IOError as e:
        print(e)
    # Read scan header table
    try: 
        df = pd.read_csv("../local_plankton/zooscan/"+subpath+"/Zooscan_meta/zooscan_scan_header_table.csv", encoding = "ISO-8859-1", sep=";")
        header_files.append(df)  
    except IOError as e:
        print(e)
    return header_files

def listFolder(path) :
    """List folder for the given path"""
    return os.listdir(path)

def tsvToGlobalData(tsv_files) : 
    """Generate from tsv a common structure of dataframe"""
    dataframe = pd.concat(tsv_files)
    for col in dataframe.columns :
        dataframe[col].fillna(dataframe.STATUS, inplace=True)
        print(col, " : ", dataframe[col].unique())

    #Do not work
    #dataframe.fillna(dataframe["STATUS"], inplace=True)
    return dataframe

def headerToGlobalData(header_files) : 
    """Generate from header a common structure of dataframe"""
    dataframe = pd.concat(header_files)
    dataframe.rename(columns={'sampleid' : 'sample_id'}, inplace=True)
    return dataframe

#TODO JCE : impl
def saveQcExecution(title, result):
    """Save an execution as html (or pdf)"""
    return
