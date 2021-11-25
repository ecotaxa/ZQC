import errors_labels

#TODO DOC

def noCb(_id, _mode, dataframe) :
    """Returns information by samples about the absence of implementation of this QC"""
    print(_id, " : ", _mode," : WIP callback not implemented yet")
    result = dataframe[['sample_id']].drop_duplicates()
    result[_id]=errors_labels.errors["global.qc_not_implemented"]
    result.rename(columns={'sample_id' : 'List samples ID'}, inplace=True)
    return result

def check_frame_type(_id, _mode, dataframe) : 
    """Returns information by samples about the size of the frame used for scanning: "large" or "narrow"."""
    print(_id, " : ", _mode," : WIP callback check_frame_type")
    #Get only usefull columns
    result = dataframe[['sample_id','process_img_background_img']]

    #Replace by large or narrow or associated error code
    result.process_img_background_img=result.process_img_background_img.map(lambda x: "large" if x.find("large")>=0 else "narrow" if x.find("narrow")>=0 else errors_labels.errors["frame_type.not_large_or_narrow"])

    #Keep only one line by couples : id / frame type
    result = result.drop_duplicates()

    #check that all scan in samples have the same frame type #TODO JCE demander confirmation a Amanda
    #print(result.process_img_background_img.unique())

    #Rename collums to match the desiered output
    result.rename(columns={'sample_id' : 'List samples ID', 'process_img_background_img' : 'Frame type'}, inplace=True)

    return result

    