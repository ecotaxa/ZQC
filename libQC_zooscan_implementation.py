import errors_labels

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

def noCb(_id, _mode, dataframe) :
    """Returns information by samples about the absence of implementation of this QC"""
    print(_id, " : ", _mode," : WIP callback not implemented yet")
    result = dataframe[['scan_id']].drop_duplicates()
    result[_id]=errors_labels.errors["global.qc_not_implemented"]
    result.rename(columns={'scan_id' : 'List scan ID'}, inplace=True)
    return result

def check_frame_type(_id, _mode, dataframe) : 
    """Returns information by samples about the size of the frame used for scanning: "large" or "narrow"."""
    print(_id, " : ", _mode," : WIP callback check_frame_type")
    #Get only usefull columns
    result = dataframe[['scan_id','process_img_background_img']]
    
    #Replace by large or narrow or associated error code
    result.process_img_background_img=result.process_img_background_img.map(lambda x: "large" if x.find("large")>=0 
                                                                                 else "narrow" if x.find("narrow")>=0 
                                                                                 else x if errors_labels.errors["global.missing_ecotaxa_table"]==x
                                                                                 else errors_labels.errors["frame_type.not_large_or_narrow"])

    #Keep only one line by couples : id / frame type
    result = result.drop_duplicates()

    #check that all scan in samples have the same frame type #TODO JCE demander confirmation a Amanda
    #print(result.process_img_background_img.unique())

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'process_img_background_img' : 'Frame type'}, inplace=True)

    return result

def check_bw_ratio(_id, _mode, dataframe) : 
    """In order to ensure the quality of the process, the value of the B/W ratio must be strictly less than 0.25."""
    print(_id, " : ", _mode," : WIP callback process_particle_bw_ratio")
    #Get only usefull columns
    result = dataframe[['scan_id','process_particle_bw_ratio']]
    
    #Replace by ratio OK or associated error code
    result.process_particle_bw_ratio=result.process_particle_bw_ratio.map(lambda x: x if errors_labels.errors["global.missing_ecotaxa_table"]==x
                                                                                    else errors_labels.sucess["bw_ratio.ok"] if is_float(x) and float(x)<0.25 and float(x)>0
                                                                                    else errors_labels.errors["bw_ratio.not_ok"])

    #Keep only one line by couples : id / ratio
    result = result.drop_duplicates()

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'process_particle_bw_ratio' : 'B/W ratio'}, inplace=True)

    return result

#IN WORK
def check_pixel_size(_id, _mode, dataframe) : 
    """The idea here is to reveal an old zooprocess bug that was mistaken about the pixel size to apply for morphometric calculations. The purpose is to check that the pixel_size is consistent with the process_img_resolution."""
    print(_id, " : ", _mode," : WIP callback check_pixel_size")
    #Get only usefull columns
    dataToTest = dataframe[['scan_id','process_particle_pixel_size_mm', 'process_img_resolution']]
    result = dataframe[['scan_id']]

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
                data.append(errors_labels.errors["global.missing_ecotaxa_table"] if size==errors_labels.errors["global.missing_ecotaxa_table"] else errors_labels.errors["pixel_size.not_ok"])

    result["pixel_size"]=data

    #Keep only one line by couples : id / is resolution coerent
    result = result.drop_duplicates()

    #Rename collums to match the desiered output
    result.rename(columns={'scan_id' : 'List scan ID', 'pixel_size' : 'PIXEL size'}, inplace=True)

    return result
    