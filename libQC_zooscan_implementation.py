import math
import labels
import time
import numpy as np
import re
import logging
from datetime import datetime

now= datetime.now()
logging.basicConfig(filename="logs/"+str(now.year)+"-"+str(now.month)+".log", level = logging.INFO, format="%(asctime)s | %(levelname)s | %(threadName)s |%(message)s")

#### TOOLS

def is_float(value):
    """Return true if value is a float else return false"""
    try:
        float(value)
        return True
    except BaseException:
        return False

def is_int(value):
    """Return true if value is an int else return false"""
    try:
        int(value)
        return True
    except BaseException:
        return False
def is_not_int(value):
    return not(is_int(value))

def get_frac_id(str) : 
    '''Return the frac id from the given str if this one is in the non exaustive list of frac type [d1, d2, d3, dN, tot, plankton] '''
    frac_types = ["(d){1}([1-9])", "(tot)", "(plankton)"]
    str=str.split('_')[0]
    
    for element in frac_types:
        m = re.search(element, str)
        if m:
            return m.group(0)
    return "frac_type_not_handled"

def is_power_of_two(n):
    return (n & (n-1) == 0) and n != 0

def independent_concat(df1, col1, df2, col2): 
    """
    Extend df2_min[col2] to match the length of df1_max[col1] by appending empty strings, 
    and add it as a new column to df1_max.
    """
    # Determine the maximum length between the two DataFrames
    max_length = max(len(df1), len(df2))
    
    # Reset indices to avoid reindexing issues
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)
    
    # Resize both DataFrames to the maximum length, filling missing values with empty strings
    df1 = df1.reindex(range(max_length), fill_value="")
    df2 = df2.reindex(range(max_length), fill_value="")
    
    # Add the column from df2_min to df1_max
    df1[col2] = df2[col2].fillna("")
    return df1

#### CALLBACKS

#Returns information by samples about the absence of implementation of this QC
def noCb(_id, _mode, local_data):
    """This feature will be available in a future release of the QC application."""
    logging.info("{} : {} : WIP callback not implemented yet".format(_id, _mode))
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result[_id] = "Not impl"#labels.errors["global.qc_not_implemented"]
    result.rename(columns={'scan_id': 'List scan ID'}, inplace=True)
    return result

### PROCESS
def check_frame_type(_id, _mode, local_data):
    """ 
        Displays information about the frame size used for scanning: either 'large' or 'narrow'.
        In the 'Frame type' column of the report table:
            - "large": When the 'process_img_background_img' in the 'ecotaxa.tsv' tables contains 'large' and the corresponding .ini file name in the 'Zooscan_config' folder also contains 'large'.
            - "narrow": When the 'process_img_background_img' in the 'ecotaxa.tsv' tables contains 'narrow' and the corresponding .ini file name in the 'Zooscan_config' folder also contains 'narrow'.
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#MISSING column": When the 'process_img_background_img' column is missing from the 'ecotaxa.tsv' table.
            - "#Frame NOT OK" : When everything isn't consistent.
    """
    start_time = time.time()

    # Get only usefull columns
    result = local_data.get("dataframe")[['scan_id', 'process_img_background_img']].drop_duplicates()

    # Get only usefull file name : .ini in Zooscan_config folder
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/Zooscan_config/" in i else False for i in fs['path'].values])
                        & (fs['extension'].values == "ini"), ["name", "extension"]].name.values
    ini_file_name = dataToTest[0] if len(dataToTest)==1 else ""

    # Replace by large or narrow or associated error code
    result.process_img_background_img = result.process_img_background_img.map(lambda x: "large" if ("large" in x) and ("large" in ini_file_name)
                                                                              else "narrow" if ("narrow" in x) and ("narrow" in ini_file_name)
                                                                              else x if labels.errors["global.missing_ecotaxa_table"] == x
                                                                              else x if x==labels.errors["global.missing_column"]
                                                                              else labels.errors["process.frame_type.not_ok"])                  

    # Keep only one line by couples : id / frame type
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_img_background_img': 'Frame type'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_frame_type".format((time.time() - start_time), _id, _mode))
    return result

def check_raw_files(_id, _mode, local_data):
    """
        This check verifies the file system structure generated by Zooprocess for the process and scan steps.
        Within the '_raw' directory of 'Zooscan_scan', the following should be present:
            - 1 file: 'scanID_log.txt'
            - 1 file: 'scanID_meta.txt'
            - 1 image: 'sampleID_fracID_raw_1.tif' and/or 1 file: 'sampleID_fracID_raw_1.zip'
        In the 'RAW files' column of the report table:
            - "#MISSING FILE": When any of the listed files are missing.
            - "#DUPLICATE FILE": When any of the listed files are duplicated.
            - "#bug RENAME ZIP FILE": When a zip file is present but its internal name doesn't match the zip file name.
            - "Files OK": Indicates consistency when the expected number of files is present.
    """
    start_time = time.time()

    # Get only usefull column size : where path contains /_raw/
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_raw/" in i else False for i in fs['path'].values]), ["name", "extension", "inside_name"]]
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result["raw_files"] = ""

    # Extract scan ids
    ids= [id[:-2] if id.endswith('_1') else id for id in result.scan_id.unique()]

    # foreatch scan id
    for id in ids:
        datascanId = dataToTest.loc[([True if id in i else False for i in dataToTest['name'].values]), ["name", "extension", "inside_name"]]

        # count of scanID_log.txt should be 1
        count_log = datascanId.loc[datascanId.extension == "txt", 'name'].str.count("_log").sum()

        # count of scanID_meta.txt should be 1
        count_meta = datascanId.loc[datascanId.extension == "txt", 'name'].str.count("_meta").sum()

        # count of sampleID_fracID_raw_1.tif and sampleID_fracID_raw_1.zip should be 1 and/or 1
        count_raw_tif = datascanId.loc[datascanId.extension == "tif", 'name'].str.count("_raw").sum()
        raw_zip = datascanId.loc[datascanId.extension == "zip", ['name', 'inside_name']]
        count_raw_zip = raw_zip['name'].str.count("_raw").sum()

        # if a zip is present, check that the inside name is the same as the zip name
        if count_raw_zip == 1 and raw_zip['name'].values != raw_zip['inside_name'].values:
            result.loc[result["scan_id"] == id + "_1", 'raw_files'] += labels.errors["process.raw_files.rename_zip"]

        # if the count of files is as expected
        elif count_log == 1 and count_meta == 1 and (count_raw_tif == 1 or count_raw_zip == 1):
            result.loc[result["scan_id"] == id + "_1", 'raw_files'] = labels.sucess["process.raw_files.ok"]

        # if less than expected
        if count_log < 1 or count_meta < 1 or (count_raw_tif < 1 and count_raw_zip < 1):
            result.loc[result["scan_id"] == id + "_1", 'raw_files'] += labels.errors["process.raw_files.missing"]

        # if more than excepted
        if count_log > 1 or count_meta > 1 or count_raw_tif > 1 or count_raw_zip > 1:
            result.loc[result["scan_id"] == id + "_1", 'raw_files'] += labels.errors["process.raw_files.duplicate"]
    
    result.loc[result["raw_files"]=="", "raw_files"]=labels.errors["process.raw_files.inconsistent_scan_id"]
    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'raw_files': 'RAW files'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_raw_files".format((time.time() - start_time), _id, _mode))
    return result

def check_scan_weight(_id, _mode, local_data):
    """
        All '_raw_1.tif' image files within the '_raw' directory must be of the same size.
        
        In the 'SCAN weight' column of the report table:
            - "#BUG weight": When the '.tif' files do not have the same size.
            - "Weight OK": When all '.tif' files have the same size.
    """
    start_time = time.time()

    # Get only usefull column size :  where path contains /_raw/ and extension == .tif
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_raw/" in i else False for i in fs['path'].values]) & (fs['extension'].values == "tif"), "size"]
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()

    # check that all these tif have the same weight
    if len(dataToTest.unique()) == 1:
        result["scan_weight"] = labels.sucess["process.scan_weight.ok"]
    else:
        result["scan_weight"] = labels.errors["process.scan_weight.bug"]

    # Keep only one line by couples : id / scan weight
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'scan_weight': 'SCAN weight'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_scan_weight".format((time.time() - start_time), _id, _mode))
    return result

def check_process_post_scan(_id, _mode, local_data):
    """ 
        Verifies the file system structure post-scan generation.

        Within the '_work' directory of 'Zooscan_scan', the following must be present:
            - N images named 'scanID_X.jpg' (images range from 1 to infinity).
            - 1 table named 'ecotaxa_scanID.tsv'.
            - 1 file of the following types: 'dat1.pid', 'msk1.gif', 'out1.gif'.
            - 1 zipped image named 'vis1.zip'.

        In the 'POST SCAN' column of the report table:
            - "#UNPROCESSED": When fewer 'tsv' files than expected.
            - "#DUPLICATE TSV": When more 'tsv' files than expected.
            - "#MISSING ZIP": When fewer 'zip' files than expected.
            - "#DUPLICATE ZIP": When more 'zip' files than expected.
            - "#bug RENAME ZIP FILE": When a zip is present, but its internal name doesn't match the zip file name.
            - "#BAD ZIP FILE": When a zip is present but is corrupted and cannot be read.
            - "Process OK": When the count of files aligns as expected, indicating consistency.
    """
    #JCE TODO "N images named" not tested
    start_time = time.time()

    # Get only usefull column size : where path contains /_raw/
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_work/" in i else False for i in fs['path'].values]), ["path", "name", "extension", "inside_name"]]
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result["process_post_scan"] = ""

    # Extract scan ids
    ids = result["scan_id"].values

    # foreatch scan id
    for id in ids:
        #get lines related to curent id
        datascanId = dataToTest.loc[([True if id in i else False for i in dataToTest['name'].values]), ["name", "extension", "inside_name"]]

        # count of scanID.tsv should be 1
        count_tsv = len(datascanId.loc[datascanId.extension == "tsv", 'name'])

        # count of scanID_vis1.zip should be 1
        work_zip = datascanId.loc[datascanId.extension== "zip", ['name', 'inside_name']]
        count_work_zip = len(work_zip['name'])

        # if a zip is present, check that this zip is not corrupted
        if count_work_zip == 1 and labels.errors["global.bad_zip_file"] == work_zip['inside_name'].values:
            result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["global.bad_zip_file"]

        # if a zip is present, check that the inside name is the same as the zip name
        elif count_work_zip == 1 and work_zip['name'].values+".tif" != work_zip['inside_name'].values:
            result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.rename_zip"]

        # if the count of files is as expected
        elif count_work_zip == 1 and count_tsv == 1 :
            result.loc[result["scan_id"] == id, 'process_post_scan'] = labels.sucess["process.post_scan.ok"]

        else :
            # if less tsv than expected
            if count_tsv < 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.unprocessed"]
                
            # if more tsv than excepted
            if count_tsv > 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.duplicate.tsv"]

            # if less zip than expected
            if count_work_zip < 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.missing.zip"]

            # if more zip than excepted
            if count_work_zip > 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.duplicate.zip"]

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_post_scan': 'POST SCAN'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_process_post_scan".format((time.time() - start_time), _id, _mode))
    return result

def check_nb_lines_tsv(_id, _mode, local_data):
    """ 
        Verifies the consistency between the number of lines in the TSV file and the number of images in the related folder.

        In the 'Nb tsv lines' column of the report table:
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#Images nb ≠ TSV lines nb" : When the number of lines in a TSV file differs from the number of images in the related folder.
            - "Nb lines TSV OK" : When the count of lines and images align as expected.
    """
    start_time = time.time()

    # Get only usefull data : where path contains /_raw/
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if ("/Zooscan_scan/_work/" in i and "multiples_to_separate" not in i)else False for i in fs['path'].values])
                        & (fs['extension'].values == "jpg"), ["name", "extension"]]

    result = local_data.get("dataframe")[['scan_id', 'object_id']].groupby("scan_id").size().reset_index(name='nb_objects')
    result["nb_lines_tsv"] = ""
    
    temp =  local_data.get("dataframe")[['scan_id', 'object_id']].groupby('scan_id').first().reset_index()

    # Extract scan ids
    ids = result["scan_id"].values

    # foreatch scan id
    for id in ids:
        #get lines related to curent id
        data_img_list = dataToTest.loc[([True if id in i else False for i in dataToTest['name'].values]), ["name", "extension"]]

        # count number of img in work
        count_img = len(data_img_list)

        # get number of object for id
        count_tsv_lines = result[result["scan_id"]==id]["nb_objects"].values[0]
        # if missing TSV
        if temp[temp["scan_id"] == id]["object_id"].values[0]==labels.errors["global.missing_ecotaxa_table"] : 
            result.loc[result["scan_id"] == id, 'nb_lines_tsv'] += labels.errors["global.missing_ecotaxa_table"]
        # if nb of img == nb of object in tsv
        elif count_img == count_tsv_lines :
            result.loc[result["scan_id"] == id, 'nb_lines_tsv'] += labels.sucess["process.nb_lines_tsv.ok"]
        # if nb of img != nb of object in tsv
        else :
            result.loc[result["scan_id"] == id, 'nb_lines_tsv'] += labels.errors["process.nb_lines_tsv.diff"]
            
                
    #drop usless collumns
    result.drop(columns=["nb_objects"], inplace=True)

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'nb_lines_tsv': 'Nb tsv lines'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_nb_lines_tsv".format((time.time() - start_time), _id, _mode))
    return result

def check_zooprocess_check(_id, _mode, local_data):
    """
        To ensure process quality, Zooprocess users can perform a visual quality check on scans. Once completed, the scan ID should appear in the 'checked_files.txt' within 'Zooscan_check/'.

        In the 'Check Zooprocess' column of the report table:
            - "#NOT checked": When the scan ID does not appear in the list of checked files located in 'checked_files.txt' within 'Zooscan_check/'.
            - "Check OK": When the scan ID does appear in the list of checked files located in 'checked_files.txt' within 'Zooscan_check/'.
    """
    start_time = time.time()

    # Get only usefull columns
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result["check_zooprocess"] = ""
    
    checked_files = local_data.get("checked_files")

    # Replace by process_checked OK or associated error code
    result["check_zooprocess"] = result["scan_id"].apply(lambda x:  labels.sucess["process.process_checked.ok"] if any(x in checked_file for checked_file in checked_files) else labels.errors["process.process_checked.not_checked"])

    # Keep only one line by couples : id / check zooprocess
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'check_zooprocess': 'Check Zooprocess'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_bw_ratio".format((time.time() - start_time), _id, _mode))
    return result

def check_bw_ratio(_id, _mode, local_data):
    """
        To ensure process quality, the B/W ratio value must be strictly less than 0.25.

        In the 'B/W ratio' column of the report table:
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#MISSING column": When the 'process_particle_bw_ratio' column is missing from the 'ecotaxa.tsv' table.
            - "#Ratio NOK": When the value of 'process_particle_bw_ratio' in 'ecotaxa.tsv' is out of range or not a valid number.
            - "Ratio OK": When the value of 'process_particle_bw_ratio' in 'ecotaxa.tsv' is between 0 and 0.25.
    """
    start_time = time.time()

    # Get only usefull columns
    result = local_data.get("dataframe")[['scan_id', 'process_particle_bw_ratio']].drop_duplicates()

    # Replace by ratio OK or associated error code
    result.process_particle_bw_ratio = result.process_particle_bw_ratio.map(lambda x: x if labels.errors["global.missing_ecotaxa_table"] == x
                                                                            else x if x==labels.errors["global.missing_column"]
                                                                            else labels.sucess["process.bw_ratio.ok"] if is_float(x) and float(x) < 0.25 and float(x) > 0
                                                                            else labels.errors["process.bw_ratio.not_ok"])

    # Keep only one line by couples : id / ratio
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_particle_bw_ratio': 'B/W ratio'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_bw_ratio".format((time.time() - start_time), _id, _mode))
    return result

def check_pixel_size(_id, _mode, local_data):
    """
        The aim is to uncover an old Zooprocess bug related to incorrect pixel sizes used for morphometric calculations. The objective is to verify the consistency between 'pixel_size' and 'process_img_resolution'.

        It should match one of the following configurations:
            - Size: "0.0847", Resolution: "300"
            - Size: "0.0408", Resolution: "600"
            - Size: "0.0204", Resolution: "1200"
            - Size: "0.0106", Resolution: "2400"
            - Size: "0.0053", Resolution: "4800"
            
        In the 'PIXEL size' column of the report table:
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#MISSING column": When the 'pixel_size' or 'process_img_resolution' column is missing from the 'ecotaxa.tsv' table.
            - "#Size NOK": When the pixel size does not align with the resolution.
            - Pixel size value: When the pixel size aligns with the resolution.
    """
    start_time = time.time()

    # Get only usefull columns
    dataToTest = local_data.get("dataframe")[['scan_id', 'process_particle_pixel_size_mm', 'process_img_resolution']].groupby('scan_id').first().reset_index()
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result["pixel_size"] = ""

    for i in range(0, len(dataToTest.scan_id)):
        id = dataToTest.scan_id.values[i]
        size = dataToTest.process_particle_pixel_size_mm.values[i]
        resolution = dataToTest.process_img_resolution.values[i]
        
        if((size == "0.0847" and resolution == "300") 
        or (size == "0.0408" and resolution == "600") 
        or (size == "0.0204" and resolution == "1200")
        or (size == "0.0106" and resolution == "2400")
        or (size == "0.0053" and resolution == "4800")) : 
            result.loc[result["scan_id"] == id, 'pixel_size'] = size
        else :
            result.loc[result["scan_id"] == id, 'pixel_size'] = labels.errors["global.missing_ecotaxa_table"] if size == labels.errors["global.missing_ecotaxa_table"] \
                                                                else labels.errors["global.missing_column"] if size==labels.errors["global.missing_column"] \
                                                                else labels.errors["process.pixel_size.not_ok"]

    # Keep only one line by couples : id / is resolution coerent
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'pixel_size': 'PIXEL size'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_pixel_size".format((time.time() - start_time), _id, _mode))
    return result

def check_sep_mask(_id, _mode, local_data):
    """
        This check verifies the presence of a 'sep.gif' mask in the subdirectory of the '_work'.

        In the 'SEP MASK' column of the report table:
            - "#MISSING SEP MSK = (F)": When the 'sep.gif' mask is not found. It also specifies the associated motoda fraction with the scan to address situations where no separation occurred due to a poor sample, hence motoda = 1.
            - "Sep mask OK": When a 'sep.gif' mask is present.
    """
    start_time = time.time()

    # Get only usefull column :  where path contains /_work/ and extension == .gif
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_work/" in i and "_sep" in i else False for i in fs['path'].values])
                        & (fs['extension'].values == "gif"), ["name", "extension"]].name.values

    result = local_data.get("dataframe")[['scan_id', 'acq_sub_part']].groupby('scan_id').first().reset_index()
    result["sep_mask"] = ""
    for id in result.scan_id:
        if id + "_sep" in dataToTest:
            result.loc[result["scan_id"] == id, 'sep_mask'] += labels.sucess["process.sep_mask.ok"]
        else:
            # get motoda frac from data
            motoda_frac = result.loc[result["scan_id"] == id, 'acq_sub_part']
            result.loc[result["scan_id"] == id, 'sep_mask'] = labels.errors["process.sep_mask.missing"] + " = " + motoda_frac

    result.drop(columns=["acq_sub_part"], inplace=True)

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'sep_mask': 'SEP MASK'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_sep_mask".format((time.time() - start_time), _id, _mode))
    return result

def check_process_post_sep(_id, _mode, local_data):
    """ 
        This second process must include the separation mask (if any) generated in the prior step.

        In the 'POST SEP' column of the report table:
            - "#UNPROCESSED" : When no 'ecotaxa_scanID.tsv' table is available.
            - "#MISSING column": When the 'process_particle_sep_mask' column is absent from the 'ecotaxa.tsv' table.
            - "#SEP MSK NOT INCLUDED": When the 'process_particle_sep_mask' in the 'ecotaxa.tsv' table does not indicate 'include'.
            - "process OK": When the 'process_particle_sep_mask' in the 'ecotaxa.tsv' table indicates 'include'.
    """
    start_time = time.time()

    # Get only usefull column : scan_id and process_particle_sep_mask
    result = local_data.get("dataframe")[['scan_id', 'process_particle_sep_mask']].drop_duplicates()

    # Replace by large or narrow or associated error code
    result.process_particle_sep_mask = result.process_particle_sep_mask.map(lambda x: labels.sucess["process.post_sep.ok"] if "include" in x
                                                                            else labels.errors["process.post_sep.unprocessed"] if labels.errors["global.missing_ecotaxa_table"] == x
                                                                            else x if x==labels.errors["global.missing_column"]
                                                                            else labels.errors["process.post_sep.not_included"])

    # Keep only one line by couples : id / frame type
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_particle_sep_mask': 'POST SEP'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_process_post_sep".format((time.time() - start_time), _id, _mode))
    return result

### ACQUISITION

def check_sieve_bug(_id, _mode, local_data):
    """
        This check ensures the consistency of sieve values used in scan preparation, which should remain constant within the same project and NEVER differ.
        
        Within the report table's 'sieve MIN size' and 'sieve MAX size' columns, the following details are provided:
            - 'sieve MIN size': Displays the value of the minimum sieve size obtained from 'acq_min_mesh' column within the 'ecotaxa_scanID.tsv' tables located in the subdirectories of the '_work' directories.
            - 'sieve MAX size': Displays the value of the maximum sieve size obtained from 'acq_max_mesh' column within the 'ecotaxa_scanID.tsv' tables located in the subdirectories of the '_work' directories.
            
        In the 'sieve BUG' column:
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#NOT NUMERIC": When the 'acq_min' and 'acq_max' values are non-numerical.
            - "#SIEVE different from others": When 'acq_min' or 'acq_max' values differ among scans sharing the same Frac ID.
            - "#ACQ MIN > ACQ MAX" : When 'acq_min' is greater than 'acq_max' for the same FracID (within the same scanID).
            - "#ACQ MIN = ACQ MAX" : When 'acq_min' equals 'acq_max' for the same FracID (within the same scanID).
            - "#ACQ MIN (dN) ≠ ACQ MAX (dN+1)" : When, for the same sampleID where FracID = d1 or d2 or d3 (comparison between multiple scanIDs of the same sampleID), 'acq_min' (dN) ≠ 'acq_max' (d+1).
            - "sieve OK": Indicates sieve size consistency.
    """
    start_time = time.time()

    # Get only usefull columns
    result = local_data.get("dataframe")[['scan_id', 'acq_min_mesh', 'sample_id', 'acq_max_mesh', 'acq_id']].drop_duplicates()
    result["fracID"] = [get_frac_id(e) for e in result["acq_id"]]
    result['sieve_bug']=""
    # Replace by sieve OK or associated error code
    result.sieve_bug = result.acq_min_mesh.map(lambda x: x if labels.errors["global.missing_ecotaxa_table"] == x
                                                           else labels.errors["global.not_numeric"] if not is_int(x)
                                                           else labels.sucess["acquisition.sieve.bug.ok"]) 
    result.loc[result["acq_max_mesh"].apply(is_not_int) & result["sieve_bug"]==labels.sucess["acquisition.sieve.bug.ok"], 'sieve_bug']=labels.errors["global.not_numeric"]

    # cast the type
    result=result.astype({"acq_min_mesh" : "int", "acq_max_mesh" : "int"}, errors='ignore')

    # The acq_min is superior or equal to the acq_max **for the same FracID (within the same scanID)**, 
    # put a warning "ACQ MIN > ACQ MAX" or "ACQ MIN = ACQ MAX" according to the situation:
    for id in result.scan_id : 
        sieve_bug_label=result.loc[result["scan_id"] == id, 'sieve_bug'].values[0]
        if sieve_bug_label == labels.sucess["acquisition.sieve.bug.ok"] :
            acq_min_mesh = int(result.loc[result["scan_id"] == id, 'acq_min_mesh'].values[0]) if is_int(result.loc[result["scan_id"] == id, 'acq_min_mesh'].values[0]) else result.loc[result["scan_id"] == id, 'acq_min_mesh'].values[0]
            acq_max_mesh = int(result.loc[result["scan_id"] == id, 'acq_max_mesh'].values[0]) if is_int(result.loc[result["scan_id"] == id, 'acq_max_mesh'].values[0]) else result.loc[result["scan_id"] == id, 'acq_max_mesh'].values[0]
            
            # If acq_min_mesh == acq_max_mesh 
            if acq_min_mesh == acq_max_mesh :
                result.loc[result["scan_id"] == id, 'sieve_bug'] = labels.errors["acquisition.sieve.bug.min_equ_max"]
            # If acq_min_mesh > acq_max_mesh 
            elif acq_min_mesh > acq_max_mesh :
                result.loc[result["scan_id"] == id, 'sieve_bug'] = labels.errors["acquisition.sieve.bug.min_sup_max"]

    ## TODO JCE  
    #For the same sampleID whose FracID = d1 or d2 ... dN (comparison between several scanIDs of the same sampleID), check the following conditions:
    # - the acq_min (dN) ≠ acq_max (dN+1), put a warning "ACQ MIN (dN) ≠ ACQ MAX (dN+1)"
    data_by_sample_id = result.groupby("sample_id")
    for key, item in data_by_sample_id:
        group=data_by_sample_id.get_group(key)
        if len(group)>1 :
            for i in range(1,len(group)) :
                #Get d_i and d_i+1
                d_i=group[group["fracID"]=="d"+str(i)]
                d_i_plus_1=group[group["fracID"]=="d"+str(i+1)]

                #if not d_i and d_i+1 skip test
                if d_i.empty or d_i_plus_1.empty : 
                    break

                #Compare d_i and d_i+1
                #Should respect "acq_min_mesh (N) == acq_max_mesh (N+1)"
                di_acq_min_mesh = int(d_i.acq_min_mesh.values[0]) if is_int(d_i.acq_min_mesh.values[0]) else d_i.acq_min_mesh.values[0]
                di_plus_un_acq_max_mesh = int(d_i_plus_1.acq_max_mesh.values[0]) if is_int(d_i_plus_1.acq_max_mesh.values[0]) else d_i_plus_1.acq_max_mesh.values[0]
                if di_acq_min_mesh != di_plus_un_acq_max_mesh :
                    result.loc[result["scan_id"] == d_i.scan_id.values[0], 'sieve_bug'] = labels.errors["acquisition.sieve.bug.min_dn_dif_max_dn+1_1"]+str(i)+labels.errors["acquisition.sieve.bug.min_dn_dif_max_dn+1_2"]+str(i+1)+labels.sucess["acquisition.sieve.bug.min_dn_dif_max_dn+1_3"]
                    result.loc[result["scan_id"] == d_i_plus_1.scan_id.values[0], 'sieve_bug'] = labels.errors["acquisition.sieve.bug.min_dn_dif_max_dn+1_1"]+str(i)+labels.errors["acquisition.sieve.bug.min_dn_dif_max_dn+1_2"]+str(i+1)+labels.sucess["acquisition.sieve.bug.min_dn_dif_max_dn+1_3"]
    
    #For the same handled Frac ID 
    data_by_frac_id = result.groupby("fracID")
    for key, item in data_by_frac_id:
        if key!= "frac_type_not_handled" :
            group=data_by_frac_id.get_group(key)
            # If the acq of one or more scans differs from the other scans
            if len(group['acq_min_mesh'].unique())>1 or len(group['acq_max_mesh'].unique())>1 :
                result.loc[result['fracID'] == key,  'sieve_bug'] = labels.errors["acquisition.sieve.bug.different"]+" ("+key.replace('_', '')+")"
    
    # Keep only one usfull lines
    result = result.drop_duplicates()
    result.drop(columns=["sample_id", "fracID", "acq_id"], inplace=True)

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'acq_min_mesh': 'acq min mesh', 'acq_max_mesh': 'acq max mesh', 'sieve_bug' : 'Sieve Bug'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_sieve_bug".format((time.time() - start_time), _id, _mode))
    return result

def check_motoda_check(_id, _mode, local_data):
    """
        This control conducts a numerical validation of the motoda fraction utilized.
        It identifies data generated using an earlier Zooprocess version that didn't consider the motoda fraction. All ecotaxa.tsv tables had the same motoda fraction number.

        In the 'MOTODA Fraction' column of the report table, the following is reported:
            - The 'fraction acq_sub_part' from the 'ecotaxa_scanID.tsv' tables found within the subdirectories of the '_work' directories.

        In the 'MOTODA check' column of the report table:
            - "#NOT NUMERIC": When the 'acq_sub_part' value is not numeric.
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#Motoda Fraction ≠ 1 or ≠ ^2": When 'FracID' = d1 regardless of 'sample_net_mesh' OR, when 'FracID' = tot and 'sample_net_mesh' ≥ 500.
            does not respect → 'acq_sub_part' = 1 or a power of 2.
            - "#Motoda Fraction ≠ ^2": When 'FracID' = dN+1 OR 'FracID'=tot OR 'FracID'=plankton (all net types except rg), 
            does not respect → acq_sub_part = a power of 2 except 1.
            - "#Motoda identical": When 'acq_sub_part' remains identical across the entire project.
            - "Motoda OK" : When everything is consistent.
    """
    start_time = time.time()
    # Get only usefull columns
    dataToTest = local_data.get("dataframe")[['scan_id', 'acq_sub_part', "acq_id", "sample_net_mesh"]].groupby('scan_id').first().reset_index()
    dataToTest["fracID"] = [get_frac_id(e) for e in dataToTest["acq_id"]]
    result = local_data.get("dataframe")[['scan_id','acq_sub_part']].drop_duplicates()
    result["motoda_check"] = ""
    
    # fill with motoda OK or associated generic error code
    result.motoda_check = result.acq_sub_part.map(lambda x: x if labels.errors["global.missing_ecotaxa_table"] == x
                                                           else labels.errors["global.not_numeric"] if not is_int(x)
                                                           else labels.sucess["acquisition.motoda.check.ok"]) 

    # If Motoda identique
    if len(dataToTest.acq_sub_part.unique()) == 1 :
        result['motoda_check'] =  np.where(result['motoda_check'] == labels.sucess["acquisition.motoda.check.ok"],labels.errors["acquisition.motoda.check.identique"], result['motoda_check'])
    nb_scans = len(dataToTest.scan_id)
    if (nb_scans>2) :
        for i in range(0, nb_scans):
            id = dataToTest.scan_id.values[i]
            motoda_check = result.loc[result["scan_id"] == id, 'motoda_check'].values[0]
            fracID = dataToTest.fracID.values[i]
            acq_sub_part = dataToTest.acq_sub_part.values[i]
            net_mesh = int(dataToTest.sample_net_mesh.values[i]) if is_int(dataToTest.sample_net_mesh.values[i]) else dataToTest.sample_net_mesh.values[i]

            if motoda_check == labels.sucess["acquisition.motoda.check.ok"] and is_int(net_mesh) :
                result.loc[result["scan_id"] == id, 'acq_sub_part'] = int(acq_sub_part) if is_int(acq_sub_part) else acq_sub_part
                if(fracID=="d1" or ( fracID=="tot" and net_mesh>=500)) :
                    #should be (1 or )puissance de 2
                    if not is_power_of_two(int(acq_sub_part)) :
                        result.loc[result["scan_id"] == id, 'motoda_check'] = labels.errors["acquisition.motoda.check.cas1"]
                elif (fracID.startswith("d") or fracID=="tot" or fracID=="plankton") and net_mesh < 500  :
                    if int(acq_sub_part)==1 or not is_power_of_two(int(acq_sub_part)) :
                        #should be ^2 but not 1
                        result.loc[result["scan_id"] == id, 'motoda_check'] = labels.errors["acquisition.motoda.check.cas2"]

    # Keep only one line by couples : id / motoda fraction
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'acq_sub_part' : 'MOTODA Fraction','motoda_check': 'MOTODA check'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_motoda_check".format((time.time() - start_time), _id, _mode))
    return result

def check_motoda_comparaison(_id, _mode, local_data):
    """ 
        Comparison of the motoda fraction is conducted among scanIDs belonging to the same sampleID.
        This control is specifically performed for scans where FracID = d1 or d2 or dn..., ensuring the same sampleID.

        In the 'MOTODA comparison' column of the report table:
            - "#NOT NUMERIC": When the 'acq_sub_part' value is not numeric.
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#Motoda frac (dN-1) > Motoda frac (dN)":  When the comparison violates acq_sub_part (N) <= acq_sub_part (N+1). 
            Example: acq_sub_part (d1) > acq_sub_part (d2).
            - "#Motoda comparison OK" : When everything is consistent.
            
        In the 'Sample Comment' column of the report table:
            -  The 'sample_comment' from column EK of the 'ecotaxa_scanID.tsv' tables in the subdirectories of the '_work' directories. 
            When the 'ecotaxa.tsv' table is missing, it's retrieved from the 'meta.txt'.

        In the 'Observation' column of the report table:
            - The observation extracted from the 'meta.txt' file within the '_work' directories. 
            - "#Unexpected character in meta.txt": When the 'meta.txt' file contains a special character preventing it from being read. 
            - "#BAD TXT FILE": When the 'meta.txt' file can't be read due to another reason.
    """
    start_time = time.time()
    # Get only usefull columns
    dataToTest = local_data.get("dataframe")[['scan_id', 'acq_sub_part', 'sample_id', 'acq_id']].groupby('scan_id').first().reset_index()
    dataToTest["fracID"] = [get_frac_id(e) for e in dataToTest["acq_id"]]
    result = local_data.get("dataframe")[['scan_id','acq_sub_part', 'sample_comment', 'sample_id']].drop_duplicates()
    result.insert(loc=2, column='motoda_comp', value="")
    result['Observation']=""
    
    #get meta.txt related information
    meta = local_data.get("meta")

    # fill with motoda OK or associated generic error code
    result.motoda_comp = result.acq_sub_part.map(lambda x: x if labels.errors["global.missing_ecotaxa_table"] == x
                                                           else labels.errors["global.not_numeric"] if not is_int(x)
                                                           else labels.sucess["acquisition.motoda.comparaison.ok"]) 

    data_by_sample_id = dataToTest.groupby("sample_id")
    
    for key, item in data_by_sample_id:
        group=data_by_sample_id.get_group(key)

        if len(group)>1 :
            for i in range(1,len(group)) :
                #Get d_i and d_i+1
                d_i=group[group["fracID"]=="d"+str(i)]
                d_i_plus_1=group[group["fracID"]=="d"+str(i+1)]

                #if not d_i and d_i+1 skip test
                if d_i.empty or d_i_plus_1.empty : 
                    break

                #Compare d_i and d_i+1
                #Should respect "acq_sub_part (N) <= acq_sub_part (N+1)"
                di_acq_sub_part = int(d_i.acq_sub_part.values[0]) if is_int(d_i.acq_sub_part.values[0]) else d_i.acq_sub_part.values[0]
                di_plus_un_acq_sub_part = int(d_i_plus_1.acq_sub_part.values[0]) if is_int(d_i_plus_1.acq_sub_part.values[0]) else d_i_plus_1.acq_sub_part.values[0]
                if di_acq_sub_part > di_plus_un_acq_sub_part :
                    result.loc[result["scan_id"] == d_i.scan_id.values[0], 'motoda_comp'] = labels.errors["acquisition.motoda.comparaison.ko"]+" (d"+str(i)+") > Motoda frac (d"+str(i+1)+")"
                    result.loc[result["scan_id"] == d_i_plus_1.scan_id.values[0], 'motoda_comp'] = labels.errors["acquisition.motoda.comparaison.ko"]+" (d"+str(i)+") > Motoda frac (d"+str(i+1)+")"
    
    # Extract scan ids
    ids = result["scan_id"].drop_duplicates().values
    if len(meta) == 0 :
        result['sample_comment'] = labels.errors["global.missing_meta_txt_file"]
        result['Observation'] = labels.errors["global.missing_meta_txt_file"]
    else :
        # foreatch scan id
        for id in ids:
            #get meta related to curent scan_id (opti)
            for k,v in meta.items() :
                if id in k :
                    meta_for_scan_id = v
                    break

            if result.loc[result["scan_id"] == id ].motoda_comp.values[0] == labels.errors["global.missing_ecotaxa_table"] :
                #get sample_comment
                meta_sample_comment =  meta_for_scan_id if meta_for_scan_id[0] == labels.errors["global.bad_meta_txt_file"] or meta_for_scan_id[0] == labels.errors["global.unicode_decode_error"] else [a.replace("Sample_comment= ", "") for a in meta_for_scan_id if a.startswith("Sample_comment= ")]
                #set sample_comment
                result.loc[result["scan_id"] == id, "sample_comment"] = meta_sample_comment[0] if len(meta_sample_comment)>0 else labels.errors["global.missing_column"]+" in meta.txt"
            
            #get and set Observation
            # if meta is empty
            if(len(meta_for_scan_id)==0) :
                meta_observation = []
            else :
                meta_observation =  meta_for_scan_id if meta_for_scan_id[0] == labels.errors["global.bad_meta_txt_file"] or meta_for_scan_id[0] == labels.errors["global.unicode_decode_error"] else [a.replace("Observation= ", "") for a in meta_for_scan_id if a.startswith("Observation= ")]
            result.loc[result["scan_id"] == id, "Observation"] = meta_observation[0] if len(meta_observation)>0 else labels.errors["global.missing_column"]+"  in meta.txt"

    # Keep only one line by couples : id / motoda fraction
    result = result.drop_duplicates()
    result.drop(columns=["acq_sub_part", "sample_id"], inplace=True)

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'motoda_comp': 'MOTODA comparison', 'sample_comment':'Sample comment'}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_motoda_comparaison".format((time.time() - start_time), _id, _mode))
    return result

def check_motoda_quality(_id, _mode, local_data):
    """ 
        .jpg images, commonly referred to as vignettes, are generated within the subdirectories of the '_work' directory following the initial processing step. 
        The count of these vignettes serves as an indicator of the quality of the fraction selected with motoda for creating the scan : it indicates samples with insufficient or excessive splits.

        In the 'Motoda quality' column of the report table:
            - "#NOT NUMERIC": When the 'acq_sub_part' value is non-numeric.
            - "#MISSING ecotaxa table": When no 'ecotaxa_scanID.tsv' table is available.
            - "#MISSING images" : When there are no .jpg images found in the subdirectories of the '_work' directory.
            - "#Images nb LOW : N" or "#Images nb HIGH : N" : 
                    When 'sample_net_mesh' >= 500 and 'motoda_frac' strictly equals 1:
                        → The number of .jpg images in the '_work' subdirectory must not exceed 1500.
                    When 'sample_net_mesh' >= 500 and 'motoda_frac' is strictly above 1:
                        → The number of .jpg images in the '_work' subdirectory must be between 500 and 1500.
                    When 'sample_net_mesh' < 500 and 'FracID' = d1 and 'motoda_frac' strictly equals 1:
                        → The number of .jpg images in the '_work' subdirectory must not exceed 1500.
                    When 'sample_net_mesh' < 500 and 'FracID' = d1 and 'motoda_frac' is strictly above 1:
                        → The number of .jpg images in the '_work' subdirectory must be between 500 and 1500.
                    When 'sample_net_mesh' < 500 and 'FracID' = d1+N or 'FracID' = tot or 'FracID' = plankton and motoda_frac strictly equals 1:
                        → The number of .jpg images in the '_work' subdirectory must not exceed 2500.
                    When 'sample_net_mesh' < 500 and 'FracID' = d1+N or 'FracID' = tot or 'FracID' = plankton and motoda_frac is strictly above 1:
                        → The number of .jpg images in the '_work' subdirectory must be between 1000 and 2500.
            - "Motoda OK": When all conditions are met, indicating consistency.
    """
    start_time = time.time()
    # Get only usefull columns
    result = local_data.get("dataframe")[['scan_id', 'acq_sub_part', "acq_id", "sample_net_mesh"]].drop_duplicates()
    result["fracID"] = [get_frac_id(e) for e in result["acq_id"]]
    result['motoda_quality']=""
    # Get only usefull file name : .jpg in /Zooscan_scan/_work/ folder
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if ("/Zooscan_scan/_work/" in i and "multiples_to_separate" not in i)else False for i in fs['path'].values])
                        & (fs['extension'].values == "jpg"), ["name", "extension"]]

    # fill with motoda OK or associated generic error code
    result.motoda_quality = result.acq_sub_part.map(lambda x: x if labels.errors["global.missing_ecotaxa_table"] == x
                                                           else labels.errors["global.not_numeric"] if not is_int(x)
                                                           else "") 
    # Extract scan ids
    ids = result["scan_id"].values

    # foreatch scan id
    for id in ids:
        #get lines related to curent id
        data_img_list = dataToTest.loc[([True if id in i else False for i in dataToTest['name'].values]), ["name", "extension"]]

        # count of scanID.tsv should be 1
        count_img = len(data_img_list)

        #get needed infos for that scan id
        scan_id_data = result.loc[result["scan_id"]==id, ["fracID", "acq_sub_part", "motoda_quality", "sample_net_mesh"]]
        net_mesh = int(scan_id_data["sample_net_mesh"].values[0]) if is_int(scan_id_data["sample_net_mesh"].values[0]) else scan_id_data["sample_net_mesh"].values[0]

        # if sample_net_mesh is not a number, fill result with the associated error msg
        if is_int(net_mesh) :
            # if no img in work, fill result with the associated error msg
            if count_img==0 :
                result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.errors["acquisition.motoda.quality.missing"]
            elif scan_id_data["motoda_quality"].values[0]=="" :
                #get needed infos for that scan id
                frac_id = scan_id_data["fracID"].values[0]
                motoda_frac = int(scan_id_data["acq_sub_part"].values[0]) if is_int(scan_id_data["acq_sub_part"].values[0]) else scan_id_data["acq_sub_part"].values[0]

                #start testing
                if net_mesh>=500 :
                    # When Nettype = rg and motoda_frac strictly =1
                    if motoda_frac==1 :
                        # the number of .jpg images in the _work subdirectory must not be > 1500
                        result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.sucess["acquisition.motoda.quality.ok"] if count_img <= 1500 else labels.errors["acquisition.motoda.quality.high"]+str(count_img)
                    # When Nettype = rg and motoda_frac strictly >1
                    elif motoda_frac>1 :
                        # the number of .jpg images in the _work subdirectory must be between 500 and 1500
                        result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.errors["acquisition.motoda.quality.low"]+str(count_img) if count_img < 500 else labels.errors["acquisition.motoda.quality.high"]+str(count_img) if count_img > 1500 else labels.sucess["acquisition.motoda.quality.ok"] 
                    else : 
                        result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.sucess["acquisition.motoda.quality.ok"]
                #For net_mesh < 500
                else :
                    if frac_id=="d1" : 
                        # When Nettype ≠ rg and FracID = d1 and motoda_frac strictly =1
                        if motoda_frac == 1 :
                            # the number of .jpg images in the _work subdirectory must not be > 1500
                            result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.sucess["acquisition.motoda.quality.ok"] if count_img <= 1500 else labels.errors["acquisition.motoda.quality.high"]+str(count_img)
                        # When Nettype ≠ rg and FracID = d1 and the motoda_frac strictly >1 
                        elif motoda_frac > 1 :
                            # the number of .jpg images in the _work subdirectory must be between 500 and 1500
                            result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.errors["acquisition.motoda.quality.low"]+str(count_img) if count_img < 500 else labels.errors["acquisition.motoda.quality.high"]+str(count_img) if count_img > 1500 else labels.sucess["acquisition.motoda.quality.ok"] 
                    
                    elif (frac_id.startswith("d") or frac_id=="tot" or frac_id=="plankton") : 
                        # When Nettype ≠ rg and FracID = d1+N or = tot or =plankton and motoda_frac strictly =1
                        if motoda_frac == 1 :
                            # the number of .jpg images in the _work subdirectory must not be > 2500
                            result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.sucess["acquisition.motoda.quality.ok"] if count_img <= 2500 else labels.errors["acquisition.motoda.quality.high"]+str(count_img)
                        # When Nettype ≠ rg and FracID = d1+N or = tot or =plankton and motoda_frac strictly >1
                        elif motoda_frac > 1 :
                            # the number of .jpg images in the _work subdirectory must be between 1000 and 2500
                            result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.errors["acquisition.motoda.quality.low"]+str(count_img) if count_img < 1000 else labels.errors["acquisition.motoda.quality.high"]+str(count_img) if count_img > 2500 else labels.sucess["acquisition.motoda.quality.ok"] 
                    else : 
                        result.loc[result["scan_id"] == id, 'motoda_quality'] = labels.sucess["acquisition.motoda.quality.ok"]

    #Remove result useless columns
    result.drop(columns=["fracID", "sample_net_mesh", "acq_sub_part", "acq_id"], inplace=True)

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', "motoda_quality" : "Motoda quality"}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_motoda_quality".format((time.time() - start_time), _id, _mode))
    return result

def check_spelling(_id, _mode, local_data):
    """
        Highlighting spelling errors in a secondary table for fields expected to remain consistent across the project:
            - 'Analysis operator' in the 'Scan op.' column
            - 'Splitting method' in the 'Submethod' column
    """
    start_time = time.time()
    # Get only usefull columns and drp duplicate to keep uniques values
    result_sample_scan_operator = local_data.get("dataframe")[['sample_scan_operator']].drop_duplicates()
    result_acq_sub_method = local_data.get("dataframe")[['acq_sub_method']].drop_duplicates()

    #set same len to both col
    result = independent_concat(result_sample_scan_operator, "sample_scan_operator",result_acq_sub_method, "acq_sub_method") 
    # Rename collums to match the desiered output
    result.rename(columns={'sample_scan_operator': 'Scan op.', "acq_sub_method" : "Submethod"}, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_spelling".format((time.time() - start_time), _id, _mode))
    return result

    """Checks that: all multiples < 20% of living, other multiples < 15% of (living - Copepoda), and Copepoda multiples < 15% of total Copepoda, all in both Abundance (Ab) and biovolume (Bv);
This QC is based on the newest ecotaxa default export zip file located in the "ecotaxa/" folder of your project.
NB: 
    - Total living eliminate morphological sub-categories such as "head", "part", "dead", "Insecta", "wing", "seaweed"
    - Ab for Abundance
    - Bv for Biovolume

- Ratio (total multiple/total living)
(multiple (other) + multiple (copepoda)) > 20% of (total living) 

- Ratio multiple (not copepoda)/living (not copepoda)  
% multiple (other) > 15% of (living - (Copepoda and children))

- Ratio multiple (copepoda)/total copepoda 
% multiple (copepoda) > 15% of total Copepoda (with child)

In followings coluns of the report table, are respectively reported :
    - List scan ID : the scan id.
    - % Ab (tot mult/tot liv.) : %Ab multiples (other+cop) / living, should be < 20% of (total living) abundance
    - % Bv (tot mult/tot liv.) : %Bv multiples (other+cop) / living, should be < 20% of (total living) biovolume
    - % Ab (tot mult/tot liv.) - cop : %Ab multiples other / (living - cop), should be < 15% of (living - Copepoda and children) abundance
    - % Bv (tot mult/tot liv.) - cop : %Bv multiples other / (living - cop), should be < 15% of (living - Copepoda et children) biovolume
    - % Ab (cop mult/tot cop) : %Ab multiples cop / (living - other), should be < 15% of total abundance
    - % Bv (cop mult/tot cop) : %Bv multiples cop / (living - other), should be < 15% of total biovolume

In the above listed columns of the report table can appear an error code:
    - "#HIGH multiples level" : the sample's % of multiples is to high.

    """
def checks_multiples(_id, _mode, local_data) : 
    """
    "Total living" excludes morphological sub-categories such as "head," "part," "dead," "Insecta," "wing," and "seaweed",
    "Ab" represents Abundance,
    "Bv" stands for Biovolume.

    - Ratio (total multiple/total living)
        The percentage of all multiple categories must be below 20% of all living categories.
        Formula: `(multiple (other) + multiple (copepoda)) < 20% of (total living) `

    - Ratio multiple (not copepoda)/living (not copepoda)  
        The percentage of multiple (other) must be below 15% of all living categories except the Copepoda categories.
        Formula: `% multiple (other) < 15% of (living - (Copepoda (with child))`

    - Ratio multiple (copepoda)/total copepoda 
        The percentage of multiple (copepoda) must be below 15% of all Copepoda categories.
        Formula: `% multiple (copepoda) < 15% of total Copepoda (with child)`

    This quality control procedure relies on the latest EcoTaxa default export zip file found in the "ecotaxa/" directory of your project.
"""
    start_time = time.time()
    # Get only usefull columns
    dataToTest = local_data.get("dataframe")[["object_id",'object_annotation_hierarchy', 'object_annotation_category', 'object_area']]

    # Remove not relevant categories
    dataToTest = dataToTest[dataToTest['object_annotation_hierarchy'].str.startswith("not-living")== False]
    # morpho stuff
    dataToTest = dataToTest[dataToTest['object_annotation_category'].str.contains("head")== False]
    dataToTest = dataToTest[dataToTest['object_annotation_category'].str.contains("part")== False]
    dataToTest = dataToTest[dataToTest['object_annotation_category'].str.contains("trunk")== False]
    dataToTest = dataToTest[dataToTest['object_annotation_category'].str.contains("dead")== False]
    # not plankton
    dataToTest = dataToTest[dataToTest['object_annotation_category'].str.contains("Insecta")== False]
    dataToTest = dataToTest[dataToTest['object_annotation_category'].str.contains("wing")== False]
    dataToTest = dataToTest[dataToTest['object_annotation_category'].str.contains("seaweed")== False]
    # Compute scan id and biovolume
    # The math.pi constant returns the value of PI: 3.141592653589793. The python pi const returns the value of PI : 3.141593 
    dataToTest["vol"]= [4/3 * 3.141593 * math.sqrt(float(area) / 3.141593) for area in dataToTest.object_area]#maybe here
    dataToTest["scan_id"]=dataToTest.object_id.str.replace("_1_[0-9]+$", "", regex=True)
    # Compute statistics by scan id  # missing means not counted = 0
    result = dataToTest.drop_duplicates().groupby("scan_id").agg( vol_tot=('vol', 'sum'), n_tot=('object_id', np.size)
        ).join(dataToTest[dataToTest["object_annotation_category"].str.contains("multiple")].groupby("scan_id").agg( vol_mult=('vol', 'sum'), n_mult=('object_id', np.size))
        ).join(dataToTest[dataToTest["object_annotation_hierarchy"].str.contains("Copepoda")].groupby("scan_id").agg( vol_cop=('vol', 'sum'), n_cop=('object_id', np.size))
        ).join(dataToTest[dataToTest["object_annotation_hierarchy"].str.contains("Copepoda>multiple")].groupby("scan_id").agg( vol_mult_cop=('vol', 'sum'), n_mult_cop=('object_id', np.size))
        ).join( dataToTest[dataToTest["object_annotation_hierarchy"].str.contains("other>multiple")].groupby("scan_id").agg( vol_mult_other=('vol', 'sum'), n_mult_other=('object_id', np.size))
        ).fillna(0)
    # Compute percent multiples with division by zero checks
    result['p_mult'] = result.apply(lambda row: 
                                            labels.errors["multiples.level.high"]+str(round(row.n_mult / row.n_tot * 100, 1)) 
                                            if row.n_tot != 0 and (row.n_mult / row.n_tot) > 0.2 
                                            else round(row.n_mult / row.n_tot * 100, 1) if row.n_tot != 0 else 0, axis=1)

    result['p_vol_mult'] = result.apply(lambda row: 
                                            labels.errors["multiples.level.high"]+str( round(row.vol_mult / row.vol_tot * 100, 1)) 
                                            if row.vol_tot != 0 and (row.vol_mult / row.vol_tot) > 0.2 
                                            else round(row.vol_mult / row.vol_tot * 100, 1) if row.vol_tot != 0 else 0, axis=1)

    result['p_mult_non_cop'] = result.apply(lambda row: 
                                            labels.errors["multiples.level.high"]+str(round(row.n_mult_other /(row.n_tot - row.n_cop) * 100, 1)) 
                                            if (row.n_tot - row.n_cop) != 0 and (row.n_mult_other /(row.n_tot - row.n_cop)) > 0.15 
                                            else round(row.n_mult_other /(row.n_tot - row.n_cop) * 100, 1) if (row.n_tot - row.n_cop) != 0 else 0, axis=1)

    result['p_vol_mult_non_cop'] = result.apply(lambda row: 
                                            labels.errors["multiples.level.high"]+str(round(row.vol_mult_other / (row.vol_tot - row.vol_cop) * 100, 1)) 
                                            if (row.vol_tot - row.vol_cop) != 0 and (row.vol_mult_other / (row.vol_tot - row.vol_cop)) > 0.15 
                                            else round(row.vol_mult_other / (row.vol_tot - row.vol_cop) * 100, 1) if (row.vol_tot - row.vol_cop) != 0 else 0, axis=1)

    result['p_mult_cop'] = result.apply(lambda row: 
                                            labels.errors["multiples.level.high"]+str(round(row.n_mult_cop / row.n_cop * 100, 1)) 
                                            if row.n_cop != 0 and (row.n_mult_cop / row.n_cop) > 0.15 
                                            else round(row.n_mult_cop / row.n_cop * 100, 1) if row.n_cop != 0 else 0, axis=1)

    result['p_vol_mult_cop'] = result.apply(lambda row: 
                                            labels.errors["multiples.level.high"]+str(round(row.vol_mult_cop / row.vol_cop * 100, 1)) 
                                            if row.vol_cop != 0 and (row.vol_mult_cop / row.vol_cop) > 0.15 
                                            else round(row.vol_mult_cop / row.vol_cop * 100, 1) if row.vol_cop != 0 else 0, axis=1)

    # Clean cols
    result = result.reset_index()
    result.drop(columns=["vol_tot", "n_tot", "vol_mult", "n_mult", "vol_cop", "n_cop", "vol_mult_cop", "n_mult_cop", "vol_mult_other", "n_mult_other"], inplace=True)

    # Rename collums to match the desiered output
    result.rename(columns={ 'scan_id': 'List scan ID', 
                            'p_mult' : "% Ab (tot mult/tot liv.)",#"%Ab multiples : (other+cop) / living",
                            'p_vol_mult' : "% Bv (tot mult/tot liv.)",#"%Bv multiples (other+cop) / living",
                            'p_mult_non_cop' : "% Ab (tot mult/tot liv.) - cop",#"%Ab multiples other / (living - cop)",
                            'p_vol_mult_non_cop' : "% Bv (tot mult/tot liv.) - cop",#"%Bv multiples other / (living - cop)",
                            'p_mult_cop' : "% Ab (cop mult/tot cop)", #"%Ab multiples cop / (living - other)",
                            'p_vol_mult_cop' : "% Bv (cop mult/tot cop)",#"%Bv multiples cop / (living - other)"
                        }, inplace=True)

    logging.info("-- TIME : {} seconds -- : {} : {} : callback check_motoda_check".format((time.time() - start_time), _id, _mode))
    return result

"""
    
    # remove not relevant categories
  d <- filter(d,
    # not living
    ! stringr::str_detect(lineage, "^not-living"),
    # morpho stuff
    ! name %in% c("head", "part", "dead"),
    # not plankton
    ! name %in% c("Insecta", "wing", "seaweed")
  )
  
  # compute scan id and biovolume
  d$vol <- 4/3 * pi * sqrt(d$area / pi)
  d$scan_id <- str_replace(d$id, "_1_[0-9]+$", "")
  d <- group_by(d, scan_id)
  
  # compute statistics
  s <- summarise(d, n_tot=n(), vol_tot=sum(vol)) %>% 
    full_join(summarise(filter(d, stringr::str_detect(name, "multiple")), n_mult=n(), vol_mult=sum(vol)), by="scan_id") %>% 
    full_join(summarise(filter(d, stringr::str_detect(lineage, "Copepoda")), n_cop=n(), vol_cop=sum(vol)), by="scan_id") %>%
    full_join(summarise(filter(d, stringr::str_detect(lineage, "Copepoda>multiple")), n_mult_cop=n(), vol_mult_cop=sum(vol)), by="scan_id") %>% 
    full_join(summarise(filter(d, stringr::str_detect(lineage, "other>multiple")), n_mult_other=n(), vol_mult_other=sum(vol)), by="scan_id")
  # missing means not counted = 0
  s[is.na(s)] <- 0
  
  # compute percent multiples
  stats <- transmute(s,
    scan_id = scan_id,
    `% mult` = n_mult / n_tot * 100,
    `%vol mult` = vol_mult / vol_tot * 100,
    `% mult (non cop)` = n_mult_other / (n_tot - n_cop) * 100,
    `%vol mult (non cop)` = vol_mult_other / (vol_tot - vol_cop) * 100,
    `% mult (cop)` = n_mult_cop / n_cop * 100,
    `%vol mult (cop)` = vol_mult_cop / vol_cop * 100
  )
  # implement checks
  ok <- apply(stats[,-1], 1, function(x) {
    all(na.omit(x <= c(20, 20, 15, 15, 15, 15)))
  })
  # TODO make this into a boolean matrix and use it in the formating of the HTML table below
  
  return(
    list(
      test=all(ok),
      message=html_table(stats[!ok,], class="table table-condensed", digits=1, classes=rlang::quos(
        `% mult`=format_condition(`% mult`>20, "danger"),
        `%vol mult`=format_condition(`%vol mult`>20, "danger"),
        `% mult (non cop)`=format_condition(`% mult (non cop)`>15, "danger"),
        `%vol mult (non cop)`=format_condition(`%vol mult (non cop)`>15, "danger"),
        `% mult (cop)`=format_condition(`% mult (cop)`>15, "danger"),
        `%vol mult (cop)`=format_condition(`%vol mult (cop)`>15, "danger")
      ))
    )
  )
  
    """