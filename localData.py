import libQC_classes 
import pandas as pd
import numpy as np
import os
import labels
from zipfile import ZipFile
from zipfile import BadZipFile 

#base_path= "../local_plankton/zooscan/"
base_path= "/piqv/local_plankton/zooscan/"

def missingCol(cols, path):
    read_cols = pd.read_csv(path, nrows=0, encoding="ISO-8859-1", sep="\t").columns
    cols_ok = read_cols[read_cols.isin(cols)].tolist()
    cols_ko = list(set(cols) - set(cols_ok))
    return cols_ok, cols_ko

def getDrives():
    print("************Get drives in************")
    drives = getDir("")
    #Sort in alphabetical order
    drives.sort()
    return drives

def getProjects(drive):
    print("************Get projects in************")
    projects = getDir(drive)
    #Keep only the one that begin with Zooscan_
    projects= [x for x in projects if x.startswith('Zooscan_')]
    #Sort in alphabetical order
    projects.sort()
    return projects

def getDir(subpath) :
    print("************Get dir in************")
    dirs = next(os.walk(base_path+subpath))[1]
    return dirs

def getFiles(subpath):
    print("************Get files in************")
    files = next(os.walk(base_path+subpath))[2]
    return files

def getdata(mode, subpath) :
    """Read, format, and return usefull data for the selected project"""
    if mode==libQC_classes.Mode.TSV :
        # Get all tsv files 
        tsv_files = getTsv(subpath)
        # Format given data 
        dataframe = tsvToGlobalData(tsv_files)
        
        fsData = getFileSystem(subpath)
        return {"dataframe" : dataframe, "fs" : fsData}

    elif mode==libQC_classes.Mode.HEADER :
        # Get all header files 
        header_files = getHeader(subpath)
        # Format given data 
        dataframe = headerToGlobalData(header_files)
        return dataframe

def  getTsv(subpath):
    """Read all ecotaxa tables (tsv files) for the given project. Return them as list of pandas dataframes"""
    tsv_files = []
    try : 
        for folder_name in listFolder(base_path+subpath+"/Zooscan_scan/_work/") :
                try: 
                    path = base_path+subpath+"/Zooscan_scan/_work/"+folder_name+"/ecotaxa_"+folder_name+".tsv"
                    #needed tsv cols for data testing
                    cols = [
                            'sample_id',
                            'process_img_background_img', 
                            'process_particle_bw_ratio', 
                            "process_particle_pixel_size_mm",
                            "process_img_resolution", 
                            "acq_sub_part", 
                            "process_particle_sep_mask", 
                            'acq_min_mesh', 
                            'acq_max_mesh'
                        ]
                    cols_ok, cols_ko = missingCol(cols, path)

                    df = pd.read_csv(path, encoding = "ISO-8859-1", usecols=cols_ok, sep="\t")
                    df['STATUS']="Ecotaxa table OK"
                    df['scan_id'] = folder_name
                    if cols_ko :
                        df[cols_ko]=labels.errors["global.missing_column"]
                    tsv_files.append(df.drop(0))  
                except IOError as e:
                    df = pd.DataFrame(data={'scan_id': [folder_name], 'STATUS': labels.errors["global.missing_ecotaxa_table"]})            
                    tsv_files.append(df)
                    print(e)
    except IOError as e:
        print(e)
    return tsv_files

def  getHeader(subpath):
    """Read the two header tables for the given project. Return them as list of pandas dataframes"""
    header_files = []
    # Read sample header table
    try: 
        df = pd.read_csv(base_path+subpath+"/Zooscan_meta/zooscan_sample_header_table.csv", encoding = "ISO-8859-1", usecols=['sampleid', 'ship'], sep=";")
        header_files.append(df)  
    except IOError as e:
        print(e)
    # Read scan header table
    try: 
        df = pd.read_csv(base_path+subpath+"/Zooscan_meta/zooscan_scan_header_table.csv", encoding = "ISO-8859-1", sep=";")
        header_files.append(df)  
    except IOError as e:
        print(e)
    return header_files

def _recursive_folderstats(folderpath, items=None,
                            depth=0, idx=1):
    """Helper function that recursively collects folder statistics and returns current id, foldersize and number of files traversed."""
    items = items if items is not None else []
    foldersize, num_files = 0, 0
    current_idx = idx

    if os.access(folderpath, os.R_OK):
        for f in os.listdir(folderpath):

            filepath = os.path.join(folderpath, f)
            stats = os.stat(filepath)
            foldersize += stats.st_size
            idx += 1

            if os.path.isdir(filepath):
                idx, items, _foldersize, _num_files = _recursive_folderstats(filepath, items, depth + 1, idx)
                foldersize += _foldersize
                num_files += _num_files
            else:
                filename, extension = os.path.splitext(f)
                extension = extension[1:] if extension else None
                inside_name="None"

                try :
                    inside_name = ZipFile(filepath, 'r').namelist() if extension == "zip" else "None"
                    inside_name = inside_name[0] if inside_name else "None"
                except BadZipFile : 
                    inside_name=labels.errors["global.bad_zip_file"]

                item = [idx, filepath, filename, extension, stats.st_size,
                        False, None, depth, inside_name]
                items.append(item)
                num_files += 1

    stats = os.stat(folderpath)
    foldername = os.path.basename(folderpath)
    item = [current_idx, folderpath, foldername, None, foldersize,
            True, num_files, depth, "None"]

    return idx, items, foldersize, num_files

def getFileSystem(subpath):
    """Function that returns a Pandas dataframe from the folders and files from a selected folder."""
    columns = ['id', 'path', 'name', 'extension', 'size',
               'folder', 'num_files', 'depth', "inside_name"]
    path = base_path+subpath
    idx, items, foldersize, num_files = _recursive_folderstats(path)
    df = pd.DataFrame(items, columns=columns)
    return df

def listFolder(path) :
    """List folder for the given path"""
    return os.listdir(path)

def tsvToGlobalData(tsv_files) : 
    """Generate from tsv a common structure of dataframe"""
    dataframe = pd.concat(tsv_files)
    for col in dataframe.columns :
        dataframe[col].fillna(dataframe.STATUS, inplace=True)
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
