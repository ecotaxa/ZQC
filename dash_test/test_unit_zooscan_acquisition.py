# 1. imports of dash app
from dash.testing.application_runners import import_app
import libQC_zooscan_implementation as impl
from enums import Mode
import localData



#TODO JCE
def test_subBlock_acquisition_check_sieve_bug(dash_duo) : 
    # In the columns 'sieve MIN size' and 'sieve MAX size' of the report table, are reported respectively :
    #     - the minimum sieve size, column CS acq_min_mesh of the ecotaxa_scanID.tsv tables of the subdirectories of the _work directories
    #     - the maximum size, column CT acq_max_mesh of the tables ecotaxa_scanID.tsv of the sub-directories of the directories _work

    # In the 'sieve BUG' column :
    project_1="Zooscan_test/test_subBlock_acquisition_check_sieve_bug_1" 
    data_1 = localData.getdata(Mode.TSV, project_1)
    res_1 = impl.check_sieve_bug("check_sieve_bug", Mode.TSV, data_1)
    # "#MISSING ecotaxa table" : If no ecotaxa_scanID.tsv table
    ## wp_d1_1
    assert res_1.loc[res_1["List scan ID"]=="wp_d1_1"]["acq min mesh"].values[0] == "#MISSING ecotaxa table"
    assert res_1.loc[res_1["List scan ID"]=="wp_d1_1"]["acq max mesh"].values[0] == "#MISSING ecotaxa table"
    assert res_1.loc[res_1["List scan ID"]=="wp_d1_1"]["Sieve Bug"].values[0] == "#MISSING ecotaxa table"
    
    project_2="Zooscan_test/test_subBlock_acquisition_check_sieve_bug_2" 
    data_2 = localData.getdata(Mode.TSV, project_2)
    res_2 = impl.check_sieve_bug("check_sieve_bug", Mode.TSV, data_2)
    # "#NOT NUMERIC" : If the acq_min and acq_max values are not numerical
    ## wp_d1_1
    assert res_2.loc[res_2["List scan ID"]=="wp_d1_1"]["acq min mesh"].values[0] == "test"
    assert res_2.loc[res_2["List scan ID"]=="wp_d1_1"]["acq max mesh"].values[0] == 1000
    assert res_2.loc[res_2["List scan ID"]=="wp_d1_1"]["Sieve Bug"].values[0] == "#NOT NUMERIC"
    
    project_3="Zooscan_test/test_subBlock_acquisition_check_sieve_bug_3" 
    data_3 = localData.getdata(Mode.TSV, project_3)
    res_3 = impl.check_sieve_bug("check_sieve_bug", Mode.TSV, data_3)
    # "#SIEVE different from others" : If the acq_min of 1 or more scans differs from the other scans with the same frac ID or the acq_max of 1 or more scans diverges from the other scans with the same frac ID
    ## wp_1_d1_1 & wp_2_d1_1
    assert res_3.loc[res_3["List scan ID"]=="wp_1_d1_1"]["acq min mesh"].values[0] == 100
    assert res_3.loc[res_3["List scan ID"]=="wp_1_d1_1"]["acq max mesh"].values[0] == 1000
    assert res_3.loc[res_3["List scan ID"]=="wp_1_d1_1"]["Sieve Bug"].values[0] == "#SIEVE different from others (d1)"
    assert res_3.loc[res_3["List scan ID"]=="wp_2_d1_1"]["acq min mesh"].values[0] == 10
    assert res_3.loc[res_3["List scan ID"]=="wp_2_d1_1"]["acq max mesh"].values[0] == 1000
    assert res_3.loc[res_3["List scan ID"]=="wp_2_d1_1"]["Sieve Bug"].values[0] == "#SIEVE different from others (d1)"
    # "#ACQ MIN (dN) ≠ ACQ MAX (dN+1)" : if for the same sampleID whose FracID = d1 or d2 or d3 (comparison between several scanIDs of the same sampleID) the acq_min (dN) ≠ acq_max (d+1)
    ## wp_2_d2_1
    assert res_3.loc[res_3["List scan ID"]=="wp_1_d2_1"]["acq min mesh"].values[0] == 1000
    assert res_3.loc[res_3["List scan ID"]=="wp_1_d2_1"]["acq max mesh"].values[0] == 999999
    assert res_3.loc[res_3["List scan ID"]=="wp_1_d2_1"]["Sieve Bug"].values[0] == "#ACQ MIN (d1) ≠ ACQ MAX (d2)"


    project_4="Zooscan_test/test_subBlock_acquisition_check_sieve_bug_4" 
    data_4 = localData.getdata(Mode.TSV, project_4)
    res_4 = impl.check_sieve_bug("check_sieve_bug", Mode.TSV, data_4)
    # "#ACQ MIN > ACQ MAX" : If the acq_min is greater than the acq_max for the same FracID (within the same scanID)
    ## wp_1_d1_1
    assert res_4.loc[res_4["List scan ID"]=="wp_d1_1"]["acq min mesh"].values[0] == 1000
    assert res_4.loc[res_4["List scan ID"]=="wp_d1_1"]["acq max mesh"].values[0] == 100
    assert res_4.loc[res_4["List scan ID"]=="wp_d1_1"]["Sieve Bug"].values[0] == "#ACQ MIN > ACQ MAX"
    
    project_5="Zooscan_test/test_subBlock_acquisition_check_sieve_bug_5" 
    data_5 = localData.getdata(Mode.TSV, project_5)
    res_5 = impl.check_sieve_bug("check_sieve_bug", Mode.TSV, data_5)
    # "#ACQ MIN = ACQ MAX" : If the acq_min is equal to the acq_max for the same FracID (within the same scanID)
    ## wp_d1_1
    assert res_5.loc[res_5["List scan ID"]=="wp_d1_1"]["acq min mesh"].values[0] == 100
    assert res_5.loc[res_5["List scan ID"]=="wp_d1_1"]["acq max mesh"].values[0] == 100
    assert res_5.loc[res_5["List scan ID"]=="wp_d1_1"]["Sieve Bug"].values[0] == "#ACQ MIN = ACQ MAX"

    project_6="Zooscan_test/test_subBlock_acquisition_check_sieve_bug_6" 
    data_6 = localData.getdata(Mode.TSV, project_6)
    res_6 = impl.check_sieve_bug("check_sieve_bug", Mode.TSV, data_6)
    # "sieve OK" : If everything is OK
    ## wp_1_d1_1
    assert res_6.loc[res_6["List scan ID"]=="wp_1_d1_1"]["acq min mesh"].values[0] == 1000
    assert res_6.loc[res_6["List scan ID"]=="wp_1_d1_1"]["acq max mesh"].values[0] == 999999
    assert res_6.loc[res_6["List scan ID"]=="wp_1_d1_1"]["Sieve Bug"].values[0] == "sieve OK"
    ## wp_1_d2_1
    assert res_6.loc[res_6["List scan ID"]=="wp_1_d2_1"]["acq min mesh"].values[0] == 100
    assert res_6.loc[res_6["List scan ID"]=="wp_1_d2_1"]["acq max mesh"].values[0] == 1000
    assert res_6.loc[res_6["List scan ID"]=="wp_1_d2_1"]["Sieve Bug"].values[0] == "sieve OK"
    ## wp_2_d1_1
    assert res_6.loc[res_6["List scan ID"]=="wp_2_d1_1"]["acq min mesh"].values[0] == 1000
    assert res_6.loc[res_6["List scan ID"]=="wp_2_d1_1"]["acq max mesh"].values[0] == 999999
    assert res_6.loc[res_6["List scan ID"]=="wp_2_d1_1"]["Sieve Bug"].values[0] == "sieve OK"
    ## wp_2_d2_1
    assert res_6.loc[res_6["List scan ID"]=="wp_2_d2_1"]["acq min mesh"].values[0] == 100
    assert res_6.loc[res_6["List scan ID"]=="wp_2_d2_1"]["acq max mesh"].values[0] == 1000
    assert res_6.loc[res_6["List scan ID"]=="wp_2_d2_1"]["Sieve Bug"].values[0] == "sieve OK"
    

def test_subBlock_acquisition_check_motoda_check(dash_duo) : 
    # In the column 'MOTODA Fraction' of the report table, is reported :
    # the fraction acq_sub_part of the tables ecotaxa_scanID.tsv of the subdirectories of the _work directories.
    
    project_1="Zooscan_test/test_subBlock_acquisition_check_motoda_check_1" 
    data_1 = localData.getdata(Mode.TSV, project_1)
    res_1 = impl.check_motoda_check("check_motoda_check", Mode.TSV, data_1) 
    # In the column 'MOTODA check' of the report table :
    # "#MISSING ecotaxa table" : if no ecotaxa_scanID.tsv table
    ## wp_d1_1
    assert res_1.loc[res_1["List scan ID"]=="wp_d1_1"]["MOTODA Fraction"].values[0] == "#MISSING ecotaxa table"
    assert res_1.loc[res_1["List scan ID"]=="wp_d1_1"]["MOTODA check"].values[0] == "#MISSING ecotaxa table"

    project_2="Zooscan_test/test_subBlock_acquisition_check_motoda_check_2" 
    data_2 = localData.getdata(Mode.TSV, project_2)
    res_2 = impl.check_motoda_check("check_motoda_check", Mode.TSV, data_2) 
    # "#NOT NUMERIC": if the acq_sub_part value is not numeric
    ## wp_d1_1
    assert res_2.loc[res_2["List scan ID"]=="wp_d1_1"]["MOTODA Fraction"].values[0] == "test"
    assert res_2.loc[res_2["List scan ID"]=="wp_d1_1"]["MOTODA check"].values[0] == "#NOT NUMERIC"

    project_3="Zooscan_test/test_subBlock_acquisition_check_motoda_check_3" 
    data_3 = localData.getdata(Mode.TSV, project_3)
    res_3 = impl.check_motoda_check("check_motoda_check", Mode.TSV, data_3) 
    # "#Motoda identical": if acq_sub_part is identical throughout the project
    ## wp_d1_1
    assert res_3.loc[res_3["List scan ID"]=="wp_d1_1"]["MOTODA Fraction"].values[0] == "4"
    assert res_3.loc[res_3["List scan ID"]=="wp_d1_1"]["MOTODA check"].values[0] == "#Identical Motoda"
    ## wp_d2_1
    assert res_3.loc[res_3["List scan ID"]=="wp_d2_1"]["MOTODA Fraction"].values[0] == "4"
    assert res_3.loc[res_3["List scan ID"]=="wp_d2_1"]["MOTODA check"].values[0] == "#Identical Motoda"

    project_4="Zooscan_test/test_subBlock_acquisition_check_motoda_check_4" 
    data_4 = localData.getdata(Mode.TSV, project_4)
    res_4 = impl.check_motoda_check("check_motoda_check", Mode.TSV, data_4) 
    # "#Motoda Fraction ≠ 1 or ≠ ^2": if does not respect → acq_sub_part = 1 or a power of 2
    ## when FracID = d1 regardless of sample_net_type 
    ## wp_d1_1 (here test with d1/wp2/3)
    assert res_4.loc[res_4["List scan ID"]=="wp_d1_1"]["MOTODA Fraction"].values[0] == 3
    assert res_4.loc[res_4["List scan ID"]=="wp_d1_1"]["MOTODA check"].values[0] == "#Motoda Fraction ≠ 1 or ≠ ^2"
    ## OR when FracID = tot and sample_net_type = rg,
    ## rg_tot_1 (here test with tot/rg/21)
    assert res_4.loc[res_4["List scan ID"]=="rg_tot_1"]["MOTODA Fraction"].values[0] == 21
    assert res_4.loc[res_4["List scan ID"]=="rg_tot_1"]["MOTODA check"].values[0] == "#Motoda Fraction ≠ 1 or ≠ ^2"

    # "#Motoda Fraction ≠ ^2": does not respect → acq_sub_part = a power of 2 except 1
    ## when FracID = dN+1 and all net types except rg 
    ## wp2_d3_1 (here test with d3/wp2/1)
    assert res_4.loc[res_4["List scan ID"]=="wp2_d3_1"]["MOTODA Fraction"].values[0] == 1
    assert res_4.loc[res_4["List scan ID"]=="wp2_d3_1"]["MOTODA check"].values[0] == "#Motoda Fraction ≠ ^2"
    ## OR =tot and all net types except rg
    ## manta_tot_1 (here test with d3/manta/111)
    assert res_4.loc[res_4["List scan ID"]=="manta_tot_1"]["MOTODA Fraction"].values[0] == 111
    assert res_4.loc[res_4["List scan ID"]=="manta_tot_1"]["MOTODA check"].values[0] == "#Motoda Fraction ≠ ^2"
    ## OR = plankton  all net types except rg
    ## bongo_plankton_1 (here test with plankton/bongo/1)
    assert res_4.loc[res_4["List scan ID"]=="bongo_plankton_1"]["MOTODA Fraction"].values[0] == 1
    assert res_4.loc[res_4["List scan ID"]=="bongo_plankton_1"]["MOTODA check"].values[0] == "#Motoda Fraction ≠ ^2"

    project_5="Zooscan_test/test_subBlock_acquisition_check_motoda_check_5" 
    data_5 = localData.getdata(Mode.TSV, project_5)
    res_5 = impl.check_motoda_check("check_motoda_check", Mode.TSV, data_5) 
    # "Motoda OK" : if everything is OK
    # if does respect → acq_sub_part = 1 or a power of 2
    ## when FracID = d1 regardless of sample_net_type 
    ## wp_d1_1 (here test with d1/wp2/1)
    assert res_5.loc[res_5["List scan ID"]=="wp_d1_1"]["MOTODA Fraction"].values[0] == 1
    assert res_5.loc[res_5["List scan ID"]=="wp_d1_1"]["MOTODA check"].values[0] == "Motoda OK"
    assert res_5.loc[res_5["List scan ID"]=="wp_2_d1_1"]["MOTODA Fraction"].values[0] == 2
    assert res_5.loc[res_5["List scan ID"]=="wp_2_d1_1"]["MOTODA check"].values[0] == "Motoda OK"
    ## OR when FracID = tot and sample_net_type = rg, 
    ## rg_tot_1 (here test with tot/rg/1)
    assert res_5.loc[res_5["List scan ID"]=="rg_tot_1"]["MOTODA Fraction"].values[0] == 1
    assert res_5.loc[res_5["List scan ID"]=="rg_tot_1"]["MOTODA check"].values[0] == "Motoda OK"
    ## rg_2_tot_1 (here test with tot/rg/8)
    assert res_5.loc[res_5["List scan ID"]=="rg_2_tot_1"]["MOTODA Fraction"].values[0] == 8
    assert res_5.loc[res_5["List scan ID"]=="rg_2_tot_1"]["MOTODA check"].values[0] == "Motoda OK"

    # if does not respect → acq_sub_part = a power of 2 except 1
    ## when FracID = dN+1 and all net types except rg 
    ## wp2_d3_1 (here test with d3/wp2/2)
    assert res_5.loc[res_5["List scan ID"]=="wp2_d3_1"]["MOTODA Fraction"].values[0] == 2
    assert res_5.loc[res_5["List scan ID"]=="wp2_d3_1"]["MOTODA check"].values[0] == "Motoda OK"
    ## OR =tot and all net types except rg
    ## manta_tot_1 (here test with d3/manta/4)
    assert res_5.loc[res_5["List scan ID"]=="manta_tot_1"]["MOTODA Fraction"].values[0] == 4
    assert res_5.loc[res_5["List scan ID"]=="manta_tot_1"]["MOTODA check"].values[0] == "Motoda OK"
    ## OR = plankton  all net types except rg
    ## bongo_plankton_1 (here test with d3/plankton/16)
    assert res_5.loc[res_5["List scan ID"]=="bongo_plankton_1"]["MOTODA Fraction"].values[0] == 16
    assert res_5.loc[res_5["List scan ID"]=="bongo_plankton_1"]["MOTODA check"].values[0] == "Motoda OK"

#TODO JCE
# def test_subBlock_acquisition_check_motoda_comparaison(dash_duo) : 
#     project="Zooscan_test/test_subBlock_process_data_2" 
#     data = localData.getdata(Mode.TSV, project)
#     res = impl.check_motoda_comparaison("check_motoda_comparaison", Mode.TSV, data) 

    # In the column 'MOTODA comparison' of the report table :
    # "#NOT NUMERIC": if the acq_sub_part value is not numeric
    # "#MISSING ecotaxa table": if no ecotaxa_scanID.tsv table
    
    # "#Motoda frac (dN-1) ≥ Motoda frac (dN)": if does not respect acq_sub_part (N) < acq_sub_part (N+1).  Example : acq_sub_part (d1) > acq_sub_part (d2)
    # "#Motoda comparison OK" : if everything is OK
                
    # In the columns 'Sample Comment' and 'Observation' of the report table, are reported respectively :
    # the sample_comment, column EK of the ecotaxa_scanID.tsv tables of the subdirectories of the _work directories. If the ecotaxa.tsv table is missing it is retrieved from the meta.txt.
    # the Observation, from the meta.txt file of the _work directories.

#TODO JCE
# def test_subBlock_acquisition_check_motoda_quality(dash_duo) : 
#     project="Zooscan_test/test_subBlock_process_data_2" 
#     data = localData.getdata(Mode.TSV, project)
#     res = impl.check_motoda_quality("check_motoda_quality", Mode.TSV, data) 

    # In the column 'Motoda quality' of the report table:

    # "#NOT NUMERIC": if the acq_sub_part value is not numeric
    ## 

    # "#MISSING ecotaxa table": if no ecotaxa_scanID.tsv table
    ## 

    # "#MISSING images" : if No .jpg images in the sub-directories of the _work directory
    ##

    # "#Images nb LOW : N" or "#Images nb HIGH : N" : if the following conditions are not met :
    #         When Nettype is rg and motoda_frac strictly equal to 1
    #             → the number of .jpg images in the _work subdirectory must not be > 1500
    #         When Nettype is rg and motoda_frac strictly > 1
    #             → the number of .jpg images in the _work subdirectory must be between 800 and 1500
    #         When Nettype ≠ rg and FracID = d1 and motoda_frac strictly equal to 1
    #             → the number of .jpg images in the _work subdirectory must not be > 1500
    #         When Nettype ≠ rg and FracID = d1 and the motoda_frac strictly > 1 
    #             → the number of .jpg images in the _work subdirectory must be between 800 and 1500
    #         When Nettype ≠ rg and FracID = d1+N or = tot or =plankton and motoda_frac strictly equal to 1
    #             → the number of .jpg images in the _work subdirectory must not be > 2500
    #         When Nettype ≠ rg and FracID = d1+N or = tot or =plankton and motoda_frac strictly >1
    #             → the number of .jpg images in the _work subdirectory must be between 1000 and 2500
    ##

    # "Motoda OK" : if everything is OK
    ##

#TODO JCE
# def test_subBlock_acquisition_check_spelling(dash_duo) : 
#     project="Zooscan_test/test_subBlock_process_data_1" 
#     data = localData.getdata(Mode.TSV, project)
#     res = impl.check_spelling("check_spelling", Mode.TSV, data) 

    # analysis operators in "Scan op." column
    # splitting methods in "Submethod" column
    