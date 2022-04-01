from enum import Enum

class Mode(Enum):
    TSV = "TSV"
    HEADER = "HEADER"


class EXECUTION_STATUS(Enum):
    SUCESS = "Sucess"
    ERROR = "Error"
    KNOWN_ERROR = "Known error"

class SUPPORTED_DATA_COMPONANT(Enum):
    DATA_TABLE = "DataTable" # full width
    DATA_TABLE_XS = "DataTableXs" # width min