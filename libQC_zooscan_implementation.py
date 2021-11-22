#TODO DOC

def noCb(_id, _mode, dataframe) :
    print(_id, " : ", _mode," : WIP callback not implemented yet")
    result = dataframe[['sample_id']].drop_duplicates()
    result.rename(columns={'sample_id' : 'List samples ID'}, inplace=True)
    return result

def check_frame_type(_id, _mode, dataframe) : 
    print(_id, " : ", _mode," : WIP callback check_frame_type")

    #Get only usefull columns
    result = dataframe[['sample_id','process_img_background_img']]

    #Replace by large or narrow #TODO JCE : VERIFIER LARGE ET NARROW ET AJOUTER UN CODE D'ERREUR SI AUCUN DES DEUX
    result.process_img_background_img=result.process_img_background_img.map(lambda x: "large" if x.find("large") else "narrrow")

    #Keep only one line by couples id/frame type
    result = result.drop_duplicates()

    #check that all scan in samples have the same frame type #TODO JCE demander confirmation a Amanda

    #Rename collums to match the desiered output
    result.rename(columns={'sample_id' : 'List samples ID', 'process_img_background_img' : 'Frame type'}, inplace=True)

    return result

    