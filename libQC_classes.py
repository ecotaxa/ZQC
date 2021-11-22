
import componants
import localData
from enum import Enum
import pandas as pd
class Mode(Enum):
   TSV = "TSV"
   HEADER = "HEADER"
class EXECUTION_STATUS(Enum):
   SUCESS="Sucess"
   ERROR="Error"
   KNOWN_ERROR="Known error"

class ChecksLib():
   def __init__(self):
      self.blocks=[]

   def addBlocks(self, *_blocks) :
      [self.blocks.append(b) for b in _blocks]

   def getBlock(self, _id):
      return next((x for x in self.blocks if x.id == _id), None)

   def runCallback(self, projects, drive, block_id) :
      block = self.getBlock(block_id)
      QC_execution =block.runCallback(projects, drive)
      return QC_execution
   
   ######--- Return an object containing all availables quallity checks ---######
   def listChecks(self):
      return [b.listChecks() for b in self.blocks]

class Block :
   def __init__ (self, _title, _id, _mode): 
      self.subBlocks=[]
      self.title=_title
      self.id=_id
      self.mode=_mode    

   def addSubBlocks(self, *_subBlocks) :
      [self.subBlocks.append(sb) for sb in _subBlocks]
   
   def getSubBlock(self, _id):
      return next((x for x in self.subBlocks if x.id == _id), None)

   def runCallback(self, projects, drive) :
      QC_execution = []
      for project in projects :
         #TODO JCE get data?
         dataframe = localData.getdata(self.mode, drive+"/"+project)
         #Run blocks
         qcExecutionData = [subBlock.runCallback(self.mode, dataframe) for subBlock in self.subBlocks]

         #TODO JCE return result
         QC_execution.append(componants.qc_execution_result(project, qcExecutionData))
      return QC_execution

   def listChecks(self):
      return {
         "title" : self.title,
         "id" : self.id,
         "blocks" : [sb.listChecks() for sb in self.subBlocks]
      }

class SubBlock :
   def __init__(self, _title, _description, _id):
      self.title=_title
      self.description=_description
      self.id=_id
      self.checks=[]

   def addChecks(self, *_checks) :
      [self.checks.append(c) for c in _checks]
   
   def getCheck(self, _id):
      return next((x for x in self.checks if x.id == _id), None)

   def runCallback(self, mode, dataframe):
      
      frames = [ check.callback(check.id, mode, dataframe) for check in self.checks ]

      result = pd.concat(frames)
      result = result.groupby(["List samples ID"]).first().reset_index() #TODO JCE first_valid_index

      resultLayout = componants.sub_block_execution_result(self.title, result)
      return resultLayout

   def listChecks(self):
      return {
         "title": self.title,
         "description" : self.description,
         "id" : self.id,
         "checks" :[c.listChecks() for c in self.checks]
      }

class Check : 
   def __init__(self, _title, _description, _id, _callback):
      self.title=_title
      self.description=_description
      self.id=_id
      self.callback=_callback

   def listChecks(self):
      return {
         "title": self.title,
         "description" : self.description,
         "id" : self.id
      }

class result :
   def __init__(self, _status, _dataframe):
      self.status=_status
      self.dataframe=_dataframe
