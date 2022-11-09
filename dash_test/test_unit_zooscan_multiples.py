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
        assert str(e) == "#MISSING ecotaxa DIRECTORY"

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

    # # TODO JCE
    # # all multiples % are OK
    # project_3 = "zooscan_test/Zooscan_test_subBlock_multiples_check_multiples_3" 
    # data_3 = localData.getdata(Mode.TSV_2, project_3)
    # res_3 = impl.checks_multiples("checks_multiples", Mode.TSV_2, data_3)
    # assert res_0.loc[res_0["List scan ID"]=="wp_d2_1"]["acq max mesh"].values[0] == 10000
    
    # # TODO JCE
    # # all multiples % are too high 20/20/15/15/15/15
    # project_4 = "zooscan_test/Zooscan_test_subBlock_multiples_check_multiples_4" 
    # data_4 = localData.getdata(Mode.TSV_2, project_4)
    # res_4 = impl.checks_multiples("checks_multiples", Mode.TSV_2, data_4)
