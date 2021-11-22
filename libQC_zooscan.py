#TODO DOC
from libQC_classes import Block, Check, ChecksLib, Mode, SubBlock
import libQC_zooscan_implementation

class Lib_zooscan():

   def __init__(self):
      #Create empty QC library
      self.lib = ChecksLib()

      #Create empty Blocks 
      block_before_scan = Block("Before scan", "before_scan", Mode.HEADER)
      block_during_analysis = Block("During analysis", "during_analysis", Mode.TSV)
      block_after_ecotaxa_classif = Block("After ECOTAXA classif", "after_ecotaxa_classif", Mode.TSV)
      
      #Create empty sub blocks
      subBlock_sample = SubBlock("Sample", "This quality check gives an overview of the quality of the data related to the acquisition of the sample.", "sample")
      subBlock_acquisition = SubBlock("Acquisition", "This quality check gives an overview of the quality of the data related to the acquisition of the scan on the Zooscan.", "acquisition")
      subBlock_process = SubBlock("Process", "This quality check gives an overview and notes the quality of the steps performed by the sample during its acquisition (SCAN) at the Zooscan and its processing (PROCESS) via the Zooprocess application.", "process")
      subBlock_multiples = SubBlock("Multiples", "toto write a description", "multiples")
      

      #Create checks
      check_frame_type = Check("FRAME type", 'Displays information about the size of the frame used for scanning: "large" or "narrow".', "frame_type", libQC_zooscan_implementation.check_frame_type)
      check_raw_files = Check("RAW files", "scan de l’échantillon", "raw_files", libQC_zooscan_implementation.noCb)
      check_scan_weight = Check("SCAN weight", "qualité du scan", "scan_weight", libQC_zooscan_implementation.noCb)
      check_process_post_scan = Check("Process POST SCAN", "", "process_post_scan", libQC_zooscan_implementation.noCb)
      check_bw_ratio = Check("B/W ratio", "qualité du process", "bw_ratio", libQC_zooscan_implementation.noCb)
      check_pixel_size = Check("PIXEL size", "", "pixel_size", libQC_zooscan_implementation.noCb)
      check_sep_mask = Check("SEP MASK", "étape de séparation des multiples", "sep_mask", libQC_zooscan_implementation.noCb)
      check_process_post_sep = Check("Process POST SEP", "process incluant le masque de séparation", "process_post_sep", libQC_zooscan_implementation.noCb)
   
      check_sieve_bug = Check("Sieve Bug", "", "sieve_bug", libQC_zooscan_implementation.noCb)
      check_motoda_fraction = Check("MOTODA fraction", "", "motoda_fraction", libQC_zooscan_implementation.noCb)
      check_motoda_check = Check("MOTODA check", "Contrôle numérique", "motoda_check", libQC_zooscan_implementation.noCb)
      check_motoda_comparaison = Check("MOTODA comparison", "Comparison entre les scanID d’un même sampleID", "motoda_comparaison", libQC_zooscan_implementation.noCb)
      check_motoda_quality = Check("MOTODA quality", "Nombre de vignettes", "motoda_quality", libQC_zooscan_implementation.noCb)
      check_ortographe= Check("Orthographe", "Sur champ récurrent", "ortographe", libQC_zooscan_implementation.noCb)

      checks_gps = Check("GPS : ", "Carte interactive, sous forme d’un Tableau, sous forme de Graphs", "", libQC_zooscan_implementation.noCb)
      checks_date = Check("Check dates de prélèvements", "", "", libQC_zooscan_implementation.noCb)
      checks_other_data = Check("Check other data", "", "", libQC_zooscan_implementation.noCb)
      checks_distance_parcourue = Check("Distance parcourue par le filet", "", "", libQC_zooscan_implementation.noCb)
      checks_filtred_volume = Check("Volume filtré", "", "", libQC_zooscan_implementation.noCb)


      #Fill library with blocks
      self.lib.addBlocks(block_before_scan, block_during_analysis, block_after_ecotaxa_classif)

      #Fill blocks with subblocks
      block_before_scan.addSubBlocks(subBlock_sample)
      block_during_analysis.addSubBlocks(subBlock_sample,subBlock_acquisition,subBlock_process)
      block_after_ecotaxa_classif.addSubBlocks(subBlock_multiples)

      #Fill sub blocks with checks
      subBlock_process.addChecks(check_frame_type, check_raw_files, check_scan_weight, check_process_post_scan, check_bw_ratio, check_pixel_size, check_sep_mask, check_process_post_sep)
      subBlock_acquisition.addChecks(check_sieve_bug, check_motoda_fraction, check_motoda_check, check_motoda_comparaison, check_motoda_quality, check_ortographe)
      subBlock_sample.addChecks(checks_gps, checks_date, checks_other_data, checks_distance_parcourue, checks_filtred_volume)

   def listChecks(self) :
      return self.lib.listChecks()
   
   def runCallback(self, projects, drive, block_id):
      return self.lib.runCallback(projects, drive, block_id)