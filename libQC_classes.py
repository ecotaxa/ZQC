from datetime import datetime
import componants
from enums import SUPPORTED_DATA_COMPONANT
import localData
import pandas as pd
import time
import labels
import logging

now= datetime.now()
logging.basicConfig(filename="logs/"+str(now.year)+"-"+str(now.month)+".log", level = logging.INFO, format="%(asctime)s | %(levelname)s | %(threadName)s |%(message)s")

class ChecksLib():
    def __init__(self):
        self.blocks = []

    def addBlocks(self, *_blocks):
        [self.blocks.append(b) for b in _blocks]

    def getBlock(self, _id):
        return next((x for x in self.blocks if x.id == _id), None)

    def runCallback(self, projects, drive, block_id):
        block = self.getBlock(block_id)
        QC_execution = block.runCallback(projects, drive)
        return QC_execution

    def listChecks(self):
        """Return an object containing all availables quallity checks"""
        return [b.listChecks() for b in self.blocks]


class Block:
    def __init__(self, _title, _id, _description, _pdf_orientation, _mode):
        self.subBlocks = []
        self.title = _title
        self.id = _id
        self.description = _description
        self.pdf_orientation = _pdf_orientation
        self.mode = _mode

    def addSubBlocks(self, *_subBlocks):
        [self.subBlocks.append(sb) for sb in _subBlocks]

    def getSubBlock(self, _id):
        return next((x for x in self.subBlocks if x.id == _id), None)

    def runCallback(self, projects, drive):
        """Run block's QC, and return execution result as dash componants"""
        QC_execution = {"dash" : [], "pdf" : []}
        logging.info("--- run for {} projects : {} ---".format(len(projects), projects))
        for project in projects:
            start_time = time.time()
            pdf = {"project" : project, 
                   "block" : {"title" : self.title, "description" : self.description, "pdf_orientation" : self.pdf_orientation, "list_checks" : self.listChecks()},
                   "subBlocks" : []}
            try :
                # Get data
                local_data = localData.getdata(self.mode, drive + "/" + project)
                logging.info("--- Get local data for project '{}' in : {} seconds ---".format(project, time.time() - start_time))
                #If critical status error  : generate associated result componant
                if labels.errors["global.missing_directory.work"] in local_data["dataframe"]["STATUS"].values :
                    qcExecutionData="The QC can't execute for this project because of : "+ local_data["dataframe"]["STATUS"][0]
                else : 
                    # Run blocks
                    qcExecutionData = [subBlock.runCallback(self.mode, local_data, pdf) for subBlock in self.subBlocks]
            except Exception as e:
                qcExecutionData="The QC can't execute for this project because of : "+ str(e)
                logging.warning("***** runCallback error for project '{}' : {}".format(project, e))
            
            # Generate and agregate dash componants
            QC_execution["dash"].append(componants.qc_execution_result(project, qcExecutionData))

            # Save the created pdf 
            pdf["path"]=drive + "/" + project+ "/"
            pdf["title"] = ("QC_"+self.title+"_"+project+"_"+str(datetime.utcnow().strftime("%Y%m%d-%H%M%S"))).replace(" ", "_")
            QC_execution["pdf"].append(pdf)

        return QC_execution

    def listChecks(self):
        return {
            "title": self.title,
            "id": self.id,
            "blocks": [sb.listChecks() for sb in self.subBlocks]
        }


class SubBlock:
    def __init__(self, _title, _description, _number_of_fig, _id):
        self.title = _title
        self.description = _description
        self.id = _id
        self.number_of_fig = _number_of_fig
        self.checks = []

    def addChecks(self, *_checks):
        [self.checks.append(c) for c in _checks]

    def getCheck(self, _id):
        return next((x for x in self.checks if x.id == _id), None)

    def runCallback(self, mode, local_data, pdf):
        """Run sub block's QC, save the result in project forlder and return execution result as dash componants"""
        # For eatch checks of this sub block, run its callback and store the result in frames array.
        frames = [{"type": check.type, "fig_number" : check.fig_number, "data" : check.callback(check.id, mode, local_data) } for check in self.checks]
        result=[]
        # Concat all frame concat depending fig nb to create a unique result dataframe for this sub block. 
        for nb in range(1, self.number_of_fig+1):
            frames_for_fig_n = [d for d in frames if d['fig_number'] == nb]
            type_for_fig_n=list(set([frame["type"] for frame in frames_for_fig_n]))
            dataframe_for_fig_n=[frame["data"] for frame in frames_for_fig_n]
            if type_for_fig_n[0] == SUPPORTED_DATA_COMPONANT.DATA_TABLE_XS:
                # small unlinked tables
                result.append({"dataframe" : pd.concat(dataframe_for_fig_n), "type" : type_for_fig_n[0]})
            if type_for_fig_n[0] == SUPPORTED_DATA_COMPONANT.DATA_TABLE:
                # linked tables
                result.append({"dataframe" : pd.concat(dataframe_for_fig_n).groupby([dataframe_for_fig_n[0].columns[0]]).first().reset_index(), "type" : type_for_fig_n[0]})

        # Save the result of the execution as html in the project folder
        pdf["subBlocks"].append({"title" : self.title, "list_checks" : self.listChecks(), "data" : result})

        # Generate the dash layout, depending on execution result type
        resultLayout = componants.sub_block_execution_result(pdf["project"], self.title, result)

        return resultLayout

    def listChecks(self):
        return {
            "title": self.title,
            "description": self.description,
            "id": self.id,
            "checks": [c.listChecks() for c in self.checks]
        }


class Check:
    def __init__(self, _title, _description, _id, _type, _fig_number, _callback):
        self.title = _title
        self.description = _description
        self.id = _id
        self.fig_number=_fig_number
        self.type = _type
        self.callback = _callback

    def listChecks(self):
        return {
            "title": self.title,
            "description": self.description,
            "id": self.id
        }


class result:
    def __init__(self, _status, _dataframe):
        self.status = _status
        self.dataframe = _dataframe
