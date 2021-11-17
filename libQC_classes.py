
import componants
from enum import Enum

class Mode(Enum):
   TSV = "TSV"
   HEADER = "HEADER"

class ChecksLib():
   def __init__(self):
      self.blocks=[]

   def addBlocks(self, *_blocks) :
      [self.blocks.append(b) for b in _blocks]

   def getBlock(self, _id):
      return next((x for x in self.blocks if x.id == _id), None)

   def runCallback(self, projects, block_ids) :
      for block_id in block_ids :
         print(block_id)
         self.getBlock(block_id).runCallback(projects)

   def deleteResult(self, block_id) :
       self.getBlock(block_id).deleteResult()

   def getResult(self, block_id, projects) : 
        return self.getBlock(block_id).getResult(projects)
   
   ######--- Return an object containing all availables quallity checks ---######
   def listChecks(self):
      return [b.listChecks() for b in self.blocks]

class Block :
   def __init__ (self, _title, _id, _mode): 
      self.subBlocks=[]
      self.title=_title
      self.id=_id
      self.mode=_mode    
      self.result = "EMPTY"

   def addSubBlocks(self, *_subBlocks) :
      [self.subBlocks.append(sb) for sb in _subBlocks]
   
   def getSubBlock(self, _id):
      return next((x for x in self.subBlocks if x.id == _id), None)

   def runCallback(self, projects) :
      QC_execution = []
      for project in projects :
         #TODO JCE get data?
         dataframe = []
         #Run blocks
         qcExecutionData = [subBlock.runCallback(self.mode, dataframe) for subBlock in self.subBlocks]

         #TODO JCE Update result
         QC_execution.append(componants.qcExecutionResult(project, qcExecutionData))
      self.result = QC_execution
   
   def getResult(self, projects) : 
      if self.result == "EMPTY" :
         return componants.emptyResult(self.id, projects)
      else :
         return self.result #because sub-blocks could be run by different block, the final result is here in block.

   def deleteResult(self):
      self.result = "EMPTY"

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

   def runCallback(self, mode, dataframe) :
      [check.callback(check.id, mode, dataframe) for check in self.checks]

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

