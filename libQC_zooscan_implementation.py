import labels
import time

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

def underscore_split(a):
    """Split before the second underscore"""
    if a.count("_") == 1:
        return a
    return "_".join(a.split("_", 2)[:2])


def noCb(_id, _mode, local_data):
    """Returns information by samples about the absence of implementation of this QC"""
    print(_id, " : ", _mode, " : WIP callback not implemented yet")
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result[_id] = "Not impl"#labels.errors["global.qc_not_implemented"]
    result.rename(columns={'scan_id': 'List scan ID'}, inplace=True)
    return result


def check_frame_type(_id, _mode, local_data):
    """Returns information by scan about the size of the frame used for scanning: "large" or "narrow".
    Potential cases :
        "large"
        "narrow"
        "global.missing_ecotaxa_table": "#MISSING ecotaxa table"
        "process.frame_type.not_ok" : "#Frame NOT OK"
    """
    start_time = time.time()

    # Get only usefull columns
    result = local_data.get("dataframe")[['scan_id', 'process_img_background_img']]

    # Get only usefull file name : .ini in Zooscan_config folder
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/Zooscan_config/" in i else False for i in fs['path'].values])
                        & (fs['extension'].values == "ini"), ["name", "extension"]].name.values
    ini_file_name = dataToTest[0] if len(dataToTest)==1 else ""

    # Replace by large or narrow or associated error code
    result.process_img_background_img = result.process_img_background_img.map(lambda x: "large" if ("large" in x) and ("large" in ini_file_name)
                                                                              else "narrow" if ("narrow" in x) and ("large" in ini_file_name)
                                                                              else x if labels.errors["global.missing_ecotaxa_table"] == x
                                                                              else labels.errors["process.frame_type.not_ok"])                  

    # Keep only one line by couples : id / frame type
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_img_background_img': 'Frame type'}, inplace=True)

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback check_frame_type")
    return result


def check_bw_ratio(_id, _mode, local_data):
    """In order to ensure the quality of the process, the value of the B/W ratio must be strictly less than 0.25.
        Potential cases :
        "global.missing_ecotaxa_table": "#MISSING ecotaxa table"
        "process.bw_ratio.not_ok": "#Ratio NOK"
        "process.bw_ratio.ok": "Ratio OK"
    """
    start_time = time.time()

    # Get only usefull columns
    result = local_data.get("dataframe")[['scan_id', 'process_particle_bw_ratio']]

    # Replace by ratio OK or associated error code
    result.process_particle_bw_ratio = result.process_particle_bw_ratio.map(lambda x: x if labels.errors["global.missing_ecotaxa_table"] == x
                                                                            else labels.sucess["process.bw_ratio.ok"] if is_float(x) and float(x) < 0.25 and float(x) > 0
                                                                            else labels.errors["process.bw_ratio.not_ok"])

    # Keep only one line by couples : id / ratio
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_particle_bw_ratio': 'B/W ratio'}, inplace=True)

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback process_particle_bw_ratio")
    return result


def check_pixel_size(_id, _mode, local_data):
    """The idea here is to reveal an old zooprocess bug that was mistaken about the pixel size to apply for morphometric calculations.
        The purpose is to check that the pixel_size is consistent with the process_img_resolution.
    Potential cases :
        "pixel_size.not_ok":"#Size NOK",
        if ok show : pixel size value
    """
    start_time = time.time()

    # Get only usefull columns
    dataToTest = local_data.get("dataframe")[['scan_id', 'process_particle_pixel_size_mm', 'process_img_resolution']]
    print(dataToTest.drop_duplicates())
    result = local_data.get("dataframe")[['scan_id']]
    print(result.drop_duplicates())
    data = []
    for i in range(0, len(dataToTest.scan_id)):
        size = dataToTest.process_particle_pixel_size_mm.values[i]
        resolution = dataToTest.process_img_resolution.values[i]
        if((size == "0.0847" and resolution == "300") 
        or (size == "0.0408" and resolution == "600") 
        or (size == "0.0204" and resolution == "1200")
        or (size == "0.0106" and resolution == "2400")
        or (size == "0.0053" and resolution == "4800")) : 
            data.append(size)
        else :
            data.append(labels.errors["global.missing_ecotaxa_table"] if size ==
                        labels.errors["global.missing_ecotaxa_table"] else labels.errors["process.pixel_size.not_ok"])

    result["pixel_size"] = data

    # Keep only one line by couples : id / is resolution coerent
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'pixel_size': 'PIXEL size'}, inplace=True)

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback check_pixel_size")
    return result


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
    start_time = time.time()

    # Get only usefull column size : where path contains /_raw/
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_raw/" in i else False for i in fs['path'].values]), ["name", "extension", "inside_name"]]
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result["raw_files"] = ""
    # Extract scan ids from _raw files name
    dataToTest['scan_id'] = [underscore_split(i) for i in dataToTest["name"].values]
    ids = dataToTest.scan_id.unique()

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

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'raw_files': 'RAW files'}, inplace=True)

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback check_raw_files ")
    return result


def check_process_post_scan(_id, _mode, local_data):
    """ Checks the file system structure post scan generated.
    In the _raw directory of Zooscan_scan :
        N images named : scanID_X.jpg (images go from 1 to infinity)
        1 table ecotaxa_scanID.tsv
        1 file of the following types dat1.pid, msk1.gif, out1.gif
        1 zipped image vis1.zip
    Potential cases :
        "process_post_scan.unprocessed" : "#UNPROCESSED",
        "process_post_scan.duplicate.tsv" : "#DUPLICATE TSV",
        "process_post_scan.missing.zip" : "#MISSING ZIP",
        "process_post_scan.duplicate.zip" : "#DUPLICATE ZIP"
        "process_post_scan.ok" : "Process OK"
    """
    start_time = time.time()

    # Get only usefull column size : where path contains /_raw/
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_work/" in i else False for i in fs['path'].values]), ["path", "name", "extension", "inside_name"]]
    result = local_data.get("dataframe")[['scan_id']].drop_duplicates()
    result["process_post_scan"] = ""

    # Extract scan ids from _work files name
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

        # if the count of files is as expected
        if count_work_zip == 1 and count_tsv == 1 :
            result.loc[result["scan_id"] == id, 'process_post_scan'] = labels.sucess["process.post_scan.ok"]

        else :
            # if less tsv than expected
            if count_tsv < 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.unprocessed"]
                
            # if more tsv than excepted
            if count_tsv > 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.duplicate.tsv"]
                
            # if a zip is present, check that the inside name is the same as the zip name
            if count_work_zip == 1 and work_zip['name'].values+".tif" != work_zip['inside_name'].values:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.rename_zip"]

            # if less zip than expected
            if count_work_zip < 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.missing.zip"]

            # if more zip than excepted
            if count_work_zip > 1:
                result.loc[result["scan_id"] == id, 'process_post_scan'] += labels.errors["process.post_scan.duplicate.zip"]

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_post_scan': 'POST SCAN'}, inplace=True)

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback check_process_post_scan")
    return result


def check_scan_weight(_id, _mode, local_data):
    """All image files _raw_1.tif inside the _raw directory must be the same size.
    Potential cases :
        "scan_weight.bug" : "#BUG weight"
        "scan_weight.ok" : "Weight OK"
    """
    start_time = time.time()

    # Get only usefull column size :  where path contains /_raw/ and extension == .tif
    fs = local_data.get("fs")
    dataToTest = fs.loc[([True if "/_raw/" in i else False for i in fs['path'].values]) & (fs['extension'].values == "tif"), "size"]
    result = local_data.get("dataframe")[['scan_id']]

    # check that all these tif have the same weight
    if len(dataToTest.unique()) == 1:
        result["scan_weight"] = labels.sucess["process.scan_weight.ok"]
    else:
        result["scan_weight"] = labels.errors["process.scan_weight.bug"]

    # Keep only one line by couples : id / scan weight
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'scan_weight': 'SCAN weight'}, inplace=True)

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback check_scan_weight")
    return result


def check_sep_mask(_id, _mode, local_data):
    """Verification of the presence of a sep.gif mask in the subdirectory of the _work. If it is not present, indicate the motoda fraction associated with the scan to eliminate the situation where there was no multiple to separate because the sample was very poor and therefore motoda = 1
    Potential cases :
       "sep_mask.missing" : "#MISSING SEP MSK = (F)"
        "sep_mask.ok" : "Sep mask OK"
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

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback check_sep_mask")
    return result


def check_process_post_sep(_id, _mode, local_data):
    """This second process must include the separation mask (if any) created in the previous step.
    Potential cases :
        'post_sep.unprocessed' : "UNPROCESSED",
        'post_sep.not_included' : "SEP MSK NOT INCLUDED"
        'post_sep.ok' : "process OK"
    """
    start_time = time.time()

    # Get only usefull column : scan_id and process_particle_sep_mask
    result = local_data.get("dataframe")[['scan_id', 'process_particle_sep_mask']]

    # Replace by large or narrow or associated error code
    result.process_particle_sep_mask = result.process_particle_sep_mask.map(lambda x: labels.sucess["process.post_sep.ok"] if "include" in x
                                                                            else labels.errors["process.post_sep.unprocessed"] if labels.errors["global.missing_ecotaxa_table"] == x
                                                                            else labels.errors["process.post_sep.not_included"])

    # Keep only one line by couples : id / frame type
    result = result.drop_duplicates()

    # Rename collums to match the desiered output
    result.rename(columns={'scan_id': 'List scan ID', 'process_particle_sep_mask': 'POST SEP'}, inplace=True)

    print("-- TIME : %s seconds --" % (time.time() - start_time), " : ", _id, " : ", _mode, " : callback check_process_post_sep")
    return result
