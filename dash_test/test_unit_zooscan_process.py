# 1. imports of dash app
from dash.testing.application_runners import import_app
import libQC_zooscan_implementation as impl
from enums import Mode
import localData


#check_raw_files, check_frame_type, check_scan_weight, check_process_post_scan, check_bw_ratio, check_pixel_size, check_sep_mask, check_process_post_sep

def test_subBlock_process_check_raw_files(dash_duo) :
    project="zooscan_test/Zooscan_test_subBlock_process_data_2/" 
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


    # "#BUG RENAME ZIP FILE" : if a zip is present, but the inside name isn't the same as the zip name
    ## wp220191113_stn_05_t2_d1_1
    assert res.loc[res["List scan ID"]=="wp220191113_stn_05_t2_d1_1"]["RAW files"].values[0] == "#BUG rename zip file"

    # "Files OK" :  Everything is OK, the number of files is as expected 
    ## wp220191113_stn_05_t2_d2_1
    assert res.loc[res["List scan ID"]=="wp220191113_stn_05_t2_d2_1"]["RAW files"].values[0] == "Files OK"

    #1 test case that combbine all errors cases
    ## wp220191114_stn_05_t4_d1_1
    assert res.loc[res["List scan ID"]=="wp220191114_stn_05_t4_d1_1"]["RAW files"].values[0] == "#BUG rename zip file#MISSING FILE#DUPLICATE FILE"
    

def test_subBlock_process_check_frame_type(dash_duo) : 
    project="zooscan_test/Zooscan_test_subBlock_process_data_2/" 
    data = localData.getdata(Mode.TSV, project)
    res = impl.check_frame_type("check_frame_type", Mode.TSV, data) 

    # "large" : if the process_img_background_img of ecotaxa.tsv tables contains "large" and the .ini file name in Zooscan_config folder contains "large"
    ## wp220191111_stn_05_t1_d1_1
    assert res.loc[res["List scan ID"]=="wp220191111_stn_05_t1_d1_1"]["Frame type"].values[0] == "large"

    #TODO JCE
    # "narrow" : if the process_img_background_img of ecotaxa.tsv tables contains "narrow" and the .ini file name in Zooscan_config folder contains "narrow"
    ##
    #assert res.loc[res["List scan ID"]==""]["B/W ratio"].values[0] == "narrow"

    # "#MISSING ecotaxa table" : if no ecotaxa_scanID.tsv table
    ##wp220191103_stn_01_d1_1
    assert res.loc[res["List scan ID"]=="wp220191103_stn_01_d1_1"]["Frame type"].values[0] == "#MISSING ecotaxa table"

    # "#MISSING column" : if process_img_background_img column is missing from the ecotaxa.tsv table
    ## wp220191103_stn_01_d2_1
    assert res.loc[res["List scan ID"]=="wp220191103_stn_01_d2_1"]["Frame type"].values[0] == "#MISSING column"

    # "#Frame NOT OK" : if any other issue
    ## large.ini and narrow in tsv
    ## wp220191127_stn_10_t1_d2_1
    assert res.loc[res["List scan ID"]=="wp220191127_stn_10_t1_d2_1"]["Frame type"].values[0] == "#Frame NOT OK"

    #TODO JCE
    ## narrow.ini and large in tsv
    ##
    #assert res.loc[res["List scan ID"]==""]["Frame type"].values[0] == "#Frame NOT OK"

def test_subBlock_process_check_scan_weight(dash_duo) : 
    project_ok="zooscan_test/Zooscan_test_subBlock_process_data_1/" 
    project_ko="zooscan_test/Zooscan_test_subBlock_process_data_2/" 
    data_ok = localData.getdata(Mode.TSV, project_ok)
    data_ko = localData.getdata(Mode.TSV, project_ko)
    res_ok = impl.check_scan_weight("check_scan_weight", Mode.TSV, data_ok)
    res_ko = impl.check_scan_weight("check_scan_weight", Mode.TSV, data_ko)
   
    # "Weight OK" : all these .tif have the same weight
    assert res_ok["SCAN weight"].values[0] == "Weight OK"

    # "#BUG weight" : all these .tif have not the same weight
    ## wp220191130_stn_12_d1_raw_1.tif has been edited 
    assert res_ko["SCAN weight"].values[0] == "#BUG weight"


def test_subBlock_process_check_process_post_scan(dash_duo) : 
    #   In the _work directory of Zooscan_scan must be present :
    #         - N images named : scanID_X.jpg (images go from 1 to infinity)
    #         - 1 table ecotaxa_scanID.tsv
    #         - 1 file of the following types dat1.pid, msk1.gif, out1.gif
    #         - 1 zipped image vis1.zip

    project="zooscan_test/Zooscan_test_subBlock_process_data_2/" 
    data = localData.getdata(Mode.TSV, project)
    res = impl.check_process_post_scan("check_process_post_scan", Mode.TSV, data) 


    # In the column "POST SCAN" of the report table:
    # "#UNPROCESSED" : if less tsv than expected
    ## wp220191103_stn_01_d1_1
    assert res.loc[res["List scan ID"]=="wp220191103_stn_01_d1_1"]["POST SCAN"].values[0] == "#UNPROCESSED"

    # "#DUPLICATE TSV" : if more tsv than excepted
    ## wp220191103_stn_01_d2_1
    assert res.loc[res["List scan ID"]=="wp220191103_stn_01_d2_1"]["POST SCAN"].values[0] == "#DUPLICATE TSV"

    # "#MISSING ZIP" : if less zip than expected
    ## wp220191105_stn_02_d1_1
    assert res.loc[res["List scan ID"]=="wp220191105_stn_02_d1_1"]["POST SCAN"].values[0] == "#MISSING ZIP"

    # "#DUPLICATE ZIP" : if more zip than excepted
    ## wp220191105_stn_02_d2_1
    assert res.loc[res["List scan ID"]=="wp220191105_stn_02_d2_1"]["POST SCAN"].values[0] == "#DUPLICATE ZIP"

    # "#bug RENAME ZIP FILE" : if a zip is present, but the inside name isn't the same as the zip name
    ## wp220191107_stn_03_d1_1
    assert res.loc[res["List scan ID"]=="wp220191107_stn_03_d1_1"]["POST SCAN"].values[0] == "#BUG rename zip file"

    # "#BAD ZIP FILE" : if a zip is present, but this zip is corrupted and can't be read
    ## wp220191108_stn_04_d1_1
    assert res.loc[res["List scan ID"]=="wp220191108_stn_04_d1_1"]["POST SCAN"].values[0] == "#BAD ZIP FILE"

    # "Process OK" : if the count of files is as expected
    ## wp220191107_stn_03_d2_1
    assert res.loc[res["List scan ID"]=="wp220191107_stn_03_d2_1"]["POST SCAN"].values[0] == "Process OK"


def test_subBlock_process_check_bw_ratio(dash_duo) :
    project="zooscan_test/Zooscan_test_subBlock_process_data_1/" 
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
    ## wp220210728_d1_2_1 
    assert res.loc[res["List scan ID"]=="wp220210728_d1_2_1"]["B/W ratio"].values[0] == "#Ratio NOK"

    # "Ratio OK" : if the value of the process_particle_bw_ratio in the ecotaxatable.tsv is between 0 and 0,25.
    ## wp220210728_d2_1
    assert res.loc[res["List scan ID"]=="wp220210728_d2_1"]["B/W ratio"].values[0] == "Ratio OK"


def test_subBlock_process_check_pixel_size(dash_duo) : 
    project="zooscan_test/Zooscan_test_subBlock_process_data_2/" 
    data = localData.getdata(Mode.TSV, project)
    res = impl.check_pixel_size("check_pixel_size", Mode.TSV, data)
    # It should match one of the following proposals :
    # size :"0.0847" and resolution : "300"
    # size :"0.0408" and resolution : "600" 
    # size :"0.0204" and resolution : "1200"
    # size :"0.0106" and resolution : "2400"
    # size :"0.0053" and resolution : "4800"
            
    #In the column "PIXEL size" of the report table:
    # "#MISSING ecotaxa table" : if no ecotaxa_scanID.tsv table.
    ## wp220191103_stn_01_d1_1
    assert res.loc[res["List scan ID"]=="wp220191103_stn_01_d1_1"]["PIXEL size"].values[0] == "#MISSING ecotaxa table"

    # "#MISSING column" : if pixel_size column or process_img_resolution column is missing from the ecotaxa.tsv table.
    ## wp220191108_stn_04_d1_1
    assert res.loc[res["List scan ID"]=="wp220191108_stn_04_d1_1"]["PIXEL size"].values[0] == "#MISSING column"

    # "#Size NOK" : if the pixel size is not consistent with the resolution.
    ## wp220191108_stn_04_d2_1
    assert res.loc[res["List scan ID"]=="wp220191108_stn_04_d2_1"]["PIXEL size"].values[0] == "#Size NOK"
    #TODO JCE test with others wrong values resolution/size

    # ""pixel size value : if the pixel size is consistent with the resolution.
    ## size :"0.0847" and resolution : "300"
    ## wp220191111_stn_05_t1_d2_1
    assert res.loc[res["List scan ID"]=="wp220191111_stn_05_t1_d2_1"]["PIXEL size"].values[0] == "0.0847"

    ## size :"0.0408" and resolution : "600" 
    ## wp220191113_stn_05_t2_d1_1
    assert res.loc[res["List scan ID"]=="wp220191113_stn_05_t2_d1_1"]["PIXEL size"].values[0] == "0.0408"

    ## size :"0.0204" and resolution : "1200"
    ## wp220191113_stn_05_t2_d2_1
    assert res.loc[res["List scan ID"]=="wp220191113_stn_05_t2_d2_1"]["PIXEL size"].values[0] == "0.0204"

    ## size :"0.0106" and resolution : "2400"
    ## wp220191111_stn_05_t1_d1_1
    assert res.loc[res["List scan ID"]=="wp220191111_stn_05_t1_d1_1"]["PIXEL size"].values[0] == "0.0106"

    ## size :"0.0053" and resolution : "4800"
    ## wp220191114_stn_05_t4_d1_1
    assert res.loc[res["List scan ID"]=="wp220191114_stn_05_t4_d1_1"]["PIXEL size"].values[0] == "0.0053"


def test_subBlock_process_check_sep_mask(dash_duo) : 
    project="zooscan_test/Zooscan_test_subBlock_process_data_1/" 
    data = localData.getdata(Mode.TSV, project)
    res = impl.check_sep_mask("check_sep_mask", Mode.TSV, data)

    # "#MISSING SEP MSK = (F)" : If the sep.gif mask is not present, indicate also the motoda fraction associated with the scan to eliminate the situation where there was no multiple to separate because the sample was very poor and therefore motoda = 1
    ## wp220210728_d1_2_1
    assert res.loc[res["List scan ID"]=="wp220210728_d1_2_1"]["SEP MASK"].values[0] == "#MISSING SEP MSK = 2"
    
    # "Sep mask OK" : If a sep.gif mask is present
    ## wp220210621_d1_1
    assert res.loc[res["List scan ID"]=="wp220210621_d1_1"]["SEP MASK"].values[0] == "Sep mask OK"


def test_subBlock_process_check_process_post_sep(dash_duo) : 
    project="zooscan_test/Zooscan_test_subBlock_process_data_1/" 
    data = localData.getdata(Mode.TSV, project)
    res = impl.check_process_post_sep("check_process_post_sep", Mode.TSV, data)

    # "#UNPROCESSED" : if missing ecotaxa_scanID.tsv table.
    ##wp220210621_d1_1
    assert res.loc[res["List scan ID"]=="wp220210621_d1_1"]["POST SEP"].values[0] == "#UNPROCESSED"

    # "#MISSING column" : if process_particle_sep_mask column is missing from the ecotaxa.tsv table.
    ##wp220210728_d1_2_1
    assert res.loc[res["List scan ID"]=="wp220210728_d1_2_1"]["POST SEP"].values[0] == "#MISSING column"

    # "#SEP MSK NOT INCLUDED" : if process_particle_sep_mask from ecotaxa.tsv table does not contains "include"##
    ## wp220210728_d2_1
    assert res.loc[res["List scan ID"]=="wp220210728_d2_1"]["POST SEP"].values[0] == "#SEP MSK NOT INCLUDED"

    # "process OK" : if process_particle_sep_mask from ecotaxa.tsv table contains "include"
    ##wp220210621_d2_1
    assert res.loc[res["List scan ID"]=="wp220210621_d2_1"]["POST SEP"].values[0] == "process OK"


def test_subBlock_process_check_nb_lines_tsv(dash_duo) : 
    project="zooscan_test/Zooscan_test_subBlock_process_check_nb_lines_tsv_1/" 

    data = localData.getdata(Mode.TSV, project)
    res = impl.check_nb_lines_tsv("check_nb_lines_tsv", Mode.TSV, data)
   
    # MISSING ecotaxa table : if no ecotaxa_scanID.tsv table.
    # wp_d3_1
    assert res.loc[res["List scan ID"]=="wp_d3_1"]["Nb tsv lines"].values[0] == "#MISSING ecotaxa table"

    # Images nb ≠ TSV lignes nb : if the number of lines in a tsv file is différents than the number of images in the related folder
    ## wp_d2_1
    ## wp_d4_1
    assert res.loc[res["List scan ID"]=="wp_d2_1"]["Nb tsv lines"].values[0] == "#Images nb ≠ TSV lignes nb"
    assert res.loc[res["List scan ID"]=="wp_d4_1"]["Nb tsv lines"].values[0] == "#Images nb ≠ TSV lignes nb"
    
    # Nb lines TSV OK : if the count of lines and images are as expected
    # wp_d1_1
    assert res.loc[res["List scan ID"]=="wp_d1_1"]["Nb tsv lines"].values[0] == "Nb lines TSV OK"

def test_subBlock_process_check_nb_process_CHECK(dash_duo) : 
    project_ok="zooscan_test/Zooscan_test_subBlock_process_check_process_check_1/" 
    project_ko="zooscan_test/Zooscan_test_subBlock_process_check_process_check_2/" 

    data_ok = localData.getdata(Mode.TSV, project_ok)
    data_ko = localData.getdata(Mode.TSV, project_ko)

    res_ok = impl.check_zooprocess_check("check_zooprocess_check", Mode.TSV, data_ok)
    res_ko = impl.check_zooprocess_check("check_zooprocess_check", Mode.TSV, data_ko)
   
    # MISSING checked_files : if no checked_files.txt file.
    assert res_ko.loc[res_ko["List scan ID"]=="wp_d1_1"]["Process checked"].values[0] == "#NOT checked"
    assert res_ko.loc[res_ko["List scan ID"]=="wp_d2_1"]["Process checked"].values[0] == "#NOT checked"

    # No missintg lines checked_files OK : if all of the work scans id are listed in checked_files
    assert res_ok.loc[res_ok["List scan ID"]=="wp_d1_1"]["Process checked"].values[0] == "#NOT checked"

    # No missintg lines checked_files OK : if all of the work scans id are listed in checked_files
    assert res_ok.loc[res_ok["List scan ID"]=="wp_d2_1"]["Process checked"].values[0] == "check process OK"