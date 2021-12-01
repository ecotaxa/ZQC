import labels

#TODO DOC
def is_float(value):
  try:
    float(value)
    return True
  except:
    return False
    
def is_int(value):
  try:
    int(value)
    return True
  except:
    return False

def noCb(_id, _mode, local_data) :
    """Returns information by samples about the absence of implementation of this QC"""
    print(_id, " : ", _mode," : WIP callback not implemented yet")
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result[_id]=labels.errors["global.qc_not_implemented"]
    result.rename(columns={'scan_id' : 'List scan ID'}, inplace=True)
    return result

def check_frame_type(_id, _mode, local_data) : 
    """Returns information by samples about the size of the frame used for scanning: "large" or "narrow"."""
    print(_id, " : ", _mode," : callback check_frame_type")
    #Get only usefull columns
    result = local_data.get("dataframe")[['scan_id','process_img_background_img']]
    
    #Replace by large or narrow or associated error code
    result.process_img_background_img=result.process_img_background_img.map(lambda x: "large" if "large" in x
                                                                                 else "narrow" if "narrow" in x
                                                                                 else x if labels.errors["global.missing_ecotaxa_table"]==x
                                                                                 else labels.errors["frame_type.not_large_or_narrow"])

    #Keep only one line by couples : id / frame type
    result = result.drop_duplicates()

    #check that all scan in samples have the same frame type #TODO JCE demander confirmation a Amanda
    #print(result.process_img_background_img.unique())

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'process_img_background_img' : 'Frame type'}, inplace=True)

    return result

def check_bw_ratio(_id, _mode, local_data) : 
    """In order to ensure the quality of the process, the value of the B/W ratio must be strictly less than 0.25."""
    print(_id, " : ", _mode," : callback process_particle_bw_ratio")
    #Get only usefull columns
    result = local_data.get("dataframe")[['scan_id','process_particle_bw_ratio']]
    
    #Replace by ratio OK or associated error code
    result.process_particle_bw_ratio=result.process_particle_bw_ratio.map(lambda x: x if labels.errors["global.missing_ecotaxa_table"]==x
                                                                                    else labels.sucess["bw_ratio.ok"] if is_float(x) and float(x)<0.25 and float(x)>0
                                                                                    else labels.errors["bw_ratio.not_ok"])

    #Keep only one line by couples : id / ratio
    result = result.drop_duplicates()

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'process_particle_bw_ratio' : 'B/W ratio'}, inplace=True)

    return result

def check_pixel_size(_id, _mode, local_data) : 
    """The idea here is to reveal an old zooprocess bug that was mistaken about the pixel size to apply for morphometric calculations. The purpose is to check that the pixel_size is consistent with the process_img_resolution."""
    print(_id, " : ", _mode," : callback check_pixel_size")
    #Get only usefull columns
    dataToTest = local_data.get("dataframe")[['scan_id','process_particle_pixel_size_mm', 'process_img_resolution']]
    result = local_data.get("dataframe")[['scan_id']]

    data=[]
    for i in range(0,len(dataToTest.scan_id)) :
        size = dataToTest.process_particle_pixel_size_mm.values[i]
        resolution = dataToTest.process_img_resolution.values[i]
        match size, resolution :
            case "0.0847", "300" : 
                data.append(size)
            case "0.0408", "600" : 
                data.append(size)
            case "0.0204", "1200" : 
                data.append(size)
            case "0.0106", "2400": 
                data.append(size)
            case "0.0053", "4800": 
                data.append(size)
            case _: 
                data.append(labels.errors["global.missing_ecotaxa_table"] if size==labels.errors["global.missing_ecotaxa_table"] else labels.errors["pixel_size.not_ok"])

    result["pixel_size"]=data

    #Keep only one line by couples : id / is resolution coerent
    result = result.drop_duplicates()

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'pixel_size' : 'PIXEL size'}, inplace=True)

    return result

#INWORK
def check_raw_files(_id, _mode, local_data):
    """Checks the file system structure generated by zooprocess for the process and scan steps.
    In the _raw directory of Zooscan_scan :
        1 file scanID_log.txt
        1 file scanID_meta.txt
        1 image sampleID_fracID_raw_1.tif and/or 1 file sampleID_fracID_raw_1.zip 
    Potential cases : 
        "raw_files.missing" : "#MISSING FILE",
        "raw_files.duplicate" : "#DUPLICATE FILE",
        "raw_files.rename_zip" : "#bug RENAME ZIP FILE"
        "raw_files.ok" : "Files OK",
        """

    print(_id, " : ", _mode," : WIP callback check_raw_files")
    #Get only usefull columns
    dataToTest = local_data.get("dataframe")[['scan_id']]
    result = local_data.get("dataframe")[['scan_id']]

    data=[]
    for i in range(0,len(dataToTest.scan_id)) :
        data.append("WIP")

    result["raw_files"]=data

    #Keep only one line by couples : id / ratio
    result = result.drop_duplicates()

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'raw_files' : 'RAW files'}, inplace=True)

    return result

def check_scan_weight(_id, _mode, local_data):
    """All image files _raw_1.tif inside the _raw directory must be the same size.
    Potential cases : 
        scan_weight.bug
        scan_weight.ok
    """

    print(_id, " : ", _mode," : WIP callback check_scan_weight")

    #Get only usefull column size :  where path contains /_raw/ and extension == .tif
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_raw/" in i else False for i in fs['path'].values ]) & (fs['extension'].values=="tif"), "size"]
    result = local_data.get("dataframe")[['scan_id']]

    # check that all these tif have the same weight
    if len(dataToTest.unique()) == 1 :
        result["scan_weight"]=labels.sucess["scan_weight.ok"]
    else :
        result["scan_weight"]=labels.errors["scan_weight.bug"]

    #Keep only one line by couples : id / scan weight
    result = result.drop_duplicates()

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'scan_weight' : 'SCAN weight'}, inplace=True)

    return result
