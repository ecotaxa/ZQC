from libQC_classes import Block, Check, ChecksLib, SubBlock
from enums import Mode, SUPPORTED_DATA_COMPONANT
import libQC_zooscan_implementation

class Lib_zooscan():

   def __init__(self):
      """Define and construct a zooscan library"""
      #Create empty QC library
      self.lib = ChecksLib()

      #Create empty Blocks 
      block_before_scan = Block("Before scan", "before_scan", "Control quality on ”sampling” data", 'L', Mode.HEADER)
      block_during_analysis = Block("During analysis", "during_analysis", "Control quality on ”process and acquisition” data",'L', Mode.TSV)
      block_after_ecotaxa_classif = Block("After EcoTaxa classification", "after_ecotaxa_classif", "Control Quality on “multiples” categories", "P", Mode.TSV_2)
      
      #Create empty sub blocks
      subBlock_sample = SubBlock("Sample", " This feature will be available in a future release of the QC application. This quality check will gives an overview of the quality of the data related to the acquisition of the sample.", 1, "sample")
      subBlock_acquisition = SubBlock("Acquisition", "This quality check gives an overview of the quality of the data related to the acquisition of the scan on the Zooscan.", 2, "acquisition")
      subBlock_process = SubBlock("Process", "This quality check gives an overview and notes the quality of the steps performed by the sample during its acquisition (SCAN) at the Zooscan and its processing (PROCESS) via the Zooprocess application.", 1, "process")
      subBlock_multiples = SubBlock("Multiples", 'This quality control identifies the effort made to separate multiple objects by measuring the abundance and biovolume of the "multiple other" and "multiple copepoda" categories in relation to the other categories.', 1, "multiples")
      

      #Create checks
      check_frame_type = Check("FRAME type", libQC_zooscan_implementation.check_frame_type.__doc__ , "frame_type", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_frame_type)
      check_raw_files = Check("RAW files", libQC_zooscan_implementation.check_raw_files.__doc__ , "raw_files", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_raw_files)
      check_scan_weight = Check("SCAN weight",  libQC_zooscan_implementation.check_scan_weight.__doc__ , "scan_weight", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_scan_weight)
      check_process_post_scan = Check("Process POST SCAN", libQC_zooscan_implementation.check_process_post_scan.__doc__ , "process_post_scan", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_process_post_scan)
      check_nb_lines_tsv = Check("Nb tsv lines", libQC_zooscan_implementation.check_nb_lines_tsv.__doc__ , "check_nb_lines_tsv", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_nb_lines_tsv)
      check_zooprocess_check = Check("Zooprocess check", libQC_zooscan_implementation.check_zooprocess_check.__doc__ , "zooprocess_check", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_zooprocess_check)
      check_bw_ratio = Check("B/W ratio", libQC_zooscan_implementation.check_bw_ratio.__doc__ , "bw_ratio", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_bw_ratio)
      check_pixel_size = Check("PIXEL size",  libQC_zooscan_implementation.check_pixel_size.__doc__ , "pixel_size", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_pixel_size)
      check_sep_mask = Check("SEP MASK", libQC_zooscan_implementation.check_sep_mask.__doc__ , "sep_mask", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1,  libQC_zooscan_implementation.check_sep_mask)
      check_process_post_sep = Check("Process POST SEP",  libQC_zooscan_implementation.check_process_post_sep.__doc__ , "process_post_sep", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_process_post_sep)
   
      check_sieve_bug = Check("Sieve Bug", libQC_zooscan_implementation.check_sieve_bug.__doc__, "sieve_bug", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_sieve_bug)
      check_motoda_check = Check("MOTODA check", libQC_zooscan_implementation.check_motoda_check.__doc__, "motoda_check", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_motoda_check)
      check_motoda_comparaison = Check("MOTODA comparison", libQC_zooscan_implementation.check_motoda_comparaison.__doc__, "motoda_comparaison", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_motoda_comparaison)
      check_motoda_quality = Check("MOTODA quality", libQC_zooscan_implementation.check_motoda_quality.__doc__, "motoda_quality", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.check_motoda_quality)
      check_spelling= Check("Spelling", libQC_zooscan_implementation.check_spelling.__doc__, "spelling", SUPPORTED_DATA_COMPONANT.DATA_TABLE_XS, 2, libQC_zooscan_implementation.check_spelling)

      checks_gps = Check("GPS", libQC_zooscan_implementation.noCb.__doc__ , "GPS", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.noCb)
      checks_date = Check("Check sampling dates", libQC_zooscan_implementation.noCb.__doc__ , "Dates", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.noCb)
      checks_other_data = Check("Check other data", libQC_zooscan_implementation.noCb.__doc__ , "other data", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.noCb)
      checks_distance_parcourue = Check("Distance covered by the net", libQC_zooscan_implementation.noCb.__doc__ , "distance", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.noCb)
      checks_filtred_volume = Check("Filtered volume", libQC_zooscan_implementation.noCb.__doc__ , "volume", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.noCb)
      
      checks_multiples = Check("Proportion of multiples", libQC_zooscan_implementation.checks_multiples.__doc__ , "proportion_of_multiples", SUPPORTED_DATA_COMPONANT.DATA_TABLE, 1, libQC_zooscan_implementation.checks_multiples)

      #Fill library with blocks
      self.lib.addBlocks(block_before_scan, block_during_analysis, block_after_ecotaxa_classif)

      #Fill blocks with subblocks
      block_before_scan.addSubBlocks(subBlock_sample)
      #block_during_analysis.addSubBlocks(subBlock_sample, subBlock_acquisition, subBlock_process)
      block_during_analysis.addSubBlocks(subBlock_acquisition, subBlock_process)
      block_after_ecotaxa_classif.addSubBlocks(subBlock_multiples)

      #Fill sub blocks with checks
      subBlock_process.addChecks(check_raw_files, check_frame_type, check_scan_weight, check_process_post_scan, check_zooprocess_check, check_bw_ratio, check_pixel_size, check_sep_mask, check_process_post_sep, check_nb_lines_tsv)
      subBlock_acquisition.addChecks(check_sieve_bug, check_motoda_check, check_motoda_comparaison, check_motoda_quality, check_spelling)
      subBlock_sample.addChecks(checks_gps, checks_date, checks_other_data, checks_distance_parcourue, checks_filtred_volume)
      subBlock_multiples.addChecks(checks_multiples)

   def listChecks(self) :
      """Return an object containing all availables quallity checks"""
      return self.lib.listChecks()
   
   def runCallback(self, projects, drive, block_id):
      """Run block's QC, and return execution result as dash componants"""
      return self.lib.runCallback(projects, drive, block_id)