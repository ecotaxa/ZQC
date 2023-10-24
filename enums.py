from enum import Enum

class Mode(str, Enum):
    TSV = "TSV"
    HEADER = "HEADER"
    TSV_2 = "TSV_2"

class EXECUTION_STATUS(str, Enum):
    SUCESS = "Sucess"
    ERROR = "Error"
    KNOWN_ERROR = "Known error"

class SUPPORTED_DATA_COMPONANT(str, Enum):
    DATA_TABLE = "DataTable" # full width
    DATA_TABLE_XS = "DataTableXs" # width min