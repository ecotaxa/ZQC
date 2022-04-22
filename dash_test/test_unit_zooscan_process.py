# 1. imports of dash app
from dash.testing.application_runners import import_app
import libQC_zooscan_implementation as impl
from enums import Mode
import localData


#check_raw_files, check_frame_type, check_scan_weight, check_process_post_scan, check_bw_ratio, check_pixel_size, check_sep_mask, check_process_post_sep

def test_subBlock_process_check_raw_files(dash_duo) :
    project="zooscan_test/test_subBlock_process_check_raw_files/" 
    data = localData.getdata(Mode.TSV, project)
    res = impl.check_raw_files("check_raw_files", Mode.TSV, data) 

    # "#MISSING FILE" : one of the above listed files is missing
    ## missing file scanID_log.txt
    ## wp220191103_stn_01_d1_1
    assert res.loc[res["List scan ID"]=="wp220191103_stn_01_d1_1"]["RAW files"].values[0] == "#MISSING FILE"
    # missing file scanID_meta.txt
    ## wp220191103_stn_01_d2_1
    assert res.loc[res["List scan ID"]=="wp220191103_stn_01_d2_1"]["RAW files"].values[0] == "#MISSING FILE"
    # missing image sampleID_fracID_raw_1.tif and missing file sampleID_fracID_raw_1.zip
    # wp220191105_stn_02_d1
    assert res.loc[res["List scan ID"]=="wp220191105_stn_02_d1_1"]["RAW files"].values[0] == "#MISSING FILE"
    ## missing two files (scanID_log.txt et scanID_meta.txt)
    ## wp220191105_stn_02_d2_raw_1
    assert res.loc[res["List scan ID"]=="wp220191105_stn_02_d2_1"]["RAW files"].values[0] == "#MISSING FILE"
    ## missing three files
    ## wp220191107_stn_03_d1_1_meta
    assert res.loc[res["List scan ID"]=="wp220191107_stn_03_d1_1"]["RAW files"].values[0] == "#MISSING FILE"

    
    # "#DUPLICATE FILE" : one of the above listed files is duplicated
    ## 2 file scanID_log.txt
    ## wp220191107_stn_03_d2_1
    assert res.loc[res["List scan ID"]=="wp220191107_stn_03_d2_1"]["RAW files"].values[0] == "#DUPLICATE FILE"

    ## 2 file scanID_meta.txt
    ## wp220191108_stn_04_d1_1
    assert res.loc[res["List scan ID"]=="wp220191108_stn_04_d1_1"]["RAW files"].values[0] == "#DUPLICATE FILE"

    ## 2 image sampleID_fracID_raw_1.tif and 0 file sampleID_fracID_raw_1.zip
    ## wp220191108_stn_04_d2_1_log
    assert res.loc[res["List scan ID"]=="wp220191108_stn_04_d2_1"]["RAW files"].values[0] == "#DUPLICATE FILE"

    ## 0 image sampleID_fracID_raw_1.tif and 2 file sampleID_fracID_raw_1.zip
    ## wp220191111_stn_05_t1_d1_1
    assert res.loc[res["List scan ID"]=="wp220191111_stn_05_t1_d1_1"]["RAW files"].values[0] == "#DUPLICATE FILE"
    
    ## 2 image sampleID_fracID_raw_1.tif and 2 file sampleID_fracID_raw_1.zip
    ## wp220191111_stn_05_t1_d2_1
    assert res.loc[res["List scan ID"]=="wp220191111_stn_05_t1_d2_1"]["RAW files"].values[0] == "#DUPLICATE FILE"


    # "#bug RENAME ZIP FILE" : if a zip is present, but the inside name isn't the same as the zip name
    ## wp220191113_stn_05_t2_d1_1
    assert res.loc[res["List scan ID"]=="wp220191113_stn_05_t2_d1_1"]["RAW files"].values[0] == "#BUG rename zip file"

    # "Files OK" :  Everything is OK, the number of files is as expected 
    ## wp220191113_stn_05_t2_d2_1
    assert res.loc[res["List scan ID"]=="wp220191113_stn_05_t2_d2_1"]["RAW files"].values[0] == "Files OK"

    #1 test combinant tous les cas d'erreur
    ## wp220191114_stn_05_t4_d1_1
    assert res.loc[res["List scan ID"]=="wp220191114_stn_05_t4_d1_1"]["RAW files"].values[0] == "#BUG rename zip file#MISSING FILE#DUPLICATE FILE"
    

# def test_subBlock_process_check_frame_type(dash_duo) : 
    # project="zooscan_test/test_subBlock_process_check_raw_files/" 
    # data = localData.getdata(Mode.TSV, project)
    # res = impl.check_frame_type("check_frame_type", Mode.TSV, data) 


# def test_subBlock_process_check_scan_weight(dash_duo) : 
#     app = import_app("dash_test.app")
#     dash_duo.start_server(app)

# def test_subBlock_process_check_process_post_scan(dash_duo) : 
#     app = import_app("dash_test.app")
#     dash_duo.start_server(app)

def test_subBlock_process_check_bw_ratio(dash_duo) :
    project="zooscan_test/test_subBlock_process_check_bw_ratio/" 
    data = localData.getdata(Mode.TSV, project)
    res = impl.check_bw_ratio("check_bw_ratio", Mode.TSV, data)

    # res :
    #       List scan ID               B/W ratio
    # 1  wp220210728_d2_1                Ratio OK
    # 1  wp220210621_d2_1         #MISSING column
    # 1  wp220210728_d1_1              #Ratio NOK
    # 0  wp220210621_d1_1  #MISSING ecotaxa table
    # 1  wp220210728_d1_2              #Ratio NOK

    # "#MISSING ecotaxa table" : if no ecotaxa_scanID.tsv table. 
    ## wp220210621_d1_1
    assert res.loc[res["List scan ID"]=="wp220210621_d1_1"]["B/W ratio"].values[0] == "#MISSING ecotaxa table"
    
    # "#MISSING column" : if process_particle_bw_ratio column is missing from the ecotaxa.tsv table.
    ## wp220210621_d2_1
    assert res.loc[res["List scan ID"]=="wp220210621_d2_1"]["B/W ratio"].values[0] == "#MISSING column"

    # "#Ratio NOK" :  if the value of the process_particle_bw_ratio in the ecotaxatable.tsv 
    ##  is out of range 
    ## wp220210728_d1_1
    assert res.loc[res["List scan ID"]=="wp220210728_d1_1"]["B/W ratio"].values[0] == "#Ratio NOK"
    ## or not even a number.
    ## wp220210728_d1_2
    assert res.loc[res["List scan ID"]=="wp220210728_d1_2"]["B/W ratio"].values[0] == "#Ratio NOK"

    # "Ratio OK" : if the value of the process_particle_bw_ratio in the ecotaxatable.tsv is between 0 and 0,25.
    ## wp220210728_d2_1
    assert res.loc[res["List scan ID"]=="wp220210728_d2_1"]["B/W ratio"].values[0] == "Ratio OK"


# def test_subBlock_process_check_pixel_size(dash_duo) : 
#     app = import_app("dash_test.app")
#     dash_duo.start_server(app)

# def test_subBlock_process_check_sep_mask(dash_duo) : 
#     app = import_app("dash_test.app")
#     dash_duo.start_server(app)

# def test_subBlock_process_check_process_post_sep(dash_duo) : 
#     app = import_app("dash_test.app")
#     dash_duo.start_server(app)

