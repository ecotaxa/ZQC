# 1. imports of dash app
from dash.testing.application_runners import import_app
import libQC_zooscan_implementation as impl
from enums import Mode
import localData

#TODO JCE
def test_subBlock_multiples_check_multiples(dash_duo) : 
    app = import_app("dash_test.app")
    dash_duo.start_server(app)
    
    # NO /ecotaxa folder
    project_0 = "zooscan_test/Zooscan_test_subBlock_multiples_check_multiples_0" 
    try :
        data_0 = localData.getdata(Mode.TSV_2, project_0)
    except ValueError as e:
        assert str(e) == "Please create manually a folder at the root of your project directory and name it “ecotaxa”. Then run this QC again."

    # NO ZIP
    project_1 = "zooscan_test/Zooscan_test_subBlock_multiples_check_multiples_1" 
    try :
        data_1 = localData.getdata(Mode.TSV_2, project_1)
    except ValueError as e:
        assert str(e) == "No zip file available in the ecotaxa/ forder of the selected project, please generate it on ecotaxa."

    # MULTIPLES ZIP => should take the newest
    project_2 = "zooscan_test/Zooscan_test_subBlock_multiples_check_multiples_2"
    data_2 = localData.getdata(Mode.TSV_2, project_2)
    assert data_2.get("dataframe")["scan_id"][1] == './dash_test/data/zooscan_test/Zooscan_test_subBlock_multiples_check_multiples_2/ecotaxa/export_436_20221107_1723.zip'

    # Test values
    project_3 = "zooscan_test/Zooscan_test_subBlock_multiples_check_multiples_3" 
    data_3 = localData.getdata(Mode.TSV_2, project_3)
    res_3 = impl.checks_multiples("checks_multiples", Mode.TSV_2, data_3)

    # all multiples % are OK
    # all multiples % are too high 20/20/15/15/15/15
    assert res_3.loc[res_3["List scan ID"]=="wp2_20101025_b3_h_d2"]['% Ab (tot mult/tot liv.)'].values[0] == 9.1
    assert res_3.loc[res_3["List scan ID"]=="wp2_20101025_b3_h_d2"]["% Bv (tot mult/tot liv.)"].values[0] == 13.1
    assert res_3.loc[res_3["List scan ID"]=="wp2_20101025_b3_h_d2"]["% Ab (tot mult/tot liv.) - cop"].values[0] == "#HIGH multiples level : 33.3"
    assert res_3.loc[res_3["List scan ID"]=="wp2_20101025_b3_h_d2"]["% Bv (tot mult/tot liv.) - cop"].values[0] == "#HIGH multiples level : 36.8"
    assert res_3.loc[res_3["List scan ID"]=="wp2_20101025_b3_h_d2"]["% Ab (cop mult/tot cop)"].values[0] == 5.5
    assert res_3.loc[res_3["List scan ID"]=="wp2_20101025_b3_h_d2"]["% Bv (cop mult/tot cop)"].values[0] == 8.1
    