""" The main workhorse of the package, massages inputs to fit component needs. """
import json
import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Any, List, Mapping, Union, Any, Dict, Tuple

# local import
from .errors import AgGridBuilderError, AgGridOptionsBuilderError
from .grid_options_builder import GridOptionsBuilder, walk_grid_options

DataElement = Union[pd.DataFrame, pa.Table, np.ndarray, str]


######################################################################
# Converter functions
######################################################################
def _make_error_msg(field: str, input: str, options: List[str]):
    """ Helper function to make a cleaner error message. """
    opts = ', '.join(map(lambda x: f"'{x}'", options))
    return f"Input {field} '{input}' is invalid. Options are {opts}."
    
class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
        
        
def _serialize_data(data: DataElemet) -> str:
    """ Convert the input data element into a JSON string. """
    if isinstance(data, pd.DataFrame):
        return data.to_json(orient="records")
    elif isinstnace(data, pa.Table):
        # There ought to be a better way for serializing pyarrow tables
        return _serialize_data(data.to_pandas())
    elif isinstance(data, np.ndarray):
        # use json decoder
        return json.dumps(data, cls=NumpyArrayEncoder)
    elif isinstance(data, str):
        # presume it's already JSON
        return data
    else:
        raise GridBuilderError(f"Cannot serialize data of type '{type(data)}'")


def _process_auto_size_mode(mode: str) -> int:
    """ Ensure the auto size mode is correct. """
    if mode == "none":
        return 0
    elif "fit" in mode:
        return 2 if "all" in mode else 1
    else:
        raise GridBuilderError(
            _make_error_msg("Column Auto Size Mode", mode, ["none", "fit", "fit all"])
        )


def _process_return_mode(mode: str) -> int:
    """ Ensure the data return mode is correct. """
    if mode == "input":
        return 0
    elif "filter" in mode:
        return 2 if "sort" in mode else 1
    else:
        raise GridBuilderError(
            _make_error_msg("Return mode", mode, ["input", "filter", "filter sort"])
        )


def _process_conversions(convert: bool, errors: str) -> str:
    """ Ensure the conversion errors parameter, if requested, is correct. """
    if convert and errors not in ("raise", "coerce", "ignore"):
        raise GridBuilderError(
            _make_error_msg("Conversion error", errors, ["raise", "coerce", "ignore"])
        )
    return errors


def _process_theme(theme: str) -> str:
    """ Ensure the theme is correct. """
    if theme not in ("alpine", "balham", "streamlit", "excel"):
        raise GridBuilderError(
            _make_error_msg("Theme", them, ["alpine", "balham", "streamlit", "excel"])
        )
    return theme

def _process_excel_export_mode(mode: str) -> str:
    """ Ensure the excel export mode is set correctly. """
    if mode == "none":
        return "NONE"
    elif mode == "manual":
        return "MANUAL"
    elif "blob" in mode:
        return "FILE_BLOB_IN_GRID_RESPONSE" if "file" in mode else "SHEET_BLOB_IN_GRID_RESPONSE"
    elif "trigger" in mode:
        return "TRIGGER_DOWNLOAD"
    elif "multiple" in mode:
        return "MULTIPLE_SHEETS"
    else:
        raise GridbuilderError(
            _make_error_msg("Excel export mode",
                            mode,
                            ["none", "manual", "file blob", "sheet blob", "trigger", "multiple"])
        )

######################################################################
# Builder Class
######################################################################
class AgGridBuilder:
    data: str = "{}"
    grid_options: Dict = None
    height: int = None
    columns_auto_size_mode: int = 0
    return_mode: int = 0
    allow_unsafe_js: bool = False
    enable_enterprise_modules: bool = True  # FIXME: maybe eliminate this, just need license key?
    license_key: str = None
    convert_to_original_types: bool = True
    errors: str = "coerce"
    reload_data: bool = False
    columns_state: List[Dict] = None
    theme: str = "streamlit"
    custom_css: str = None
    update_on: List[str | Tuple[str, int]] = None
    enable_quick_search: bool = False
    excel_export_mode: str = "none"
    excel_export_multiple_sheets: Dict = None

    def __new__(cls,
                data: Union[pd.DataFrame, pa.Table, np.ndarray, str],
                grid_options: Dict = None,
                height: int = None,
                columns_auto_size_mode: str = "none",
                return_mode: str = "input",
                allow_unsafe_js: bool = False,
                enable_enterprise_modules: bool = True,
                license_key: str = None,
                convert_to_original_types: bool = True,
                errors: str = "coerce",
                reload_data: bool = False,
                columns_state: List[Dict] = None,
                theme: str = "streamlit",
                custom_css: str = None,
                use_legacy_selected_rows: bool = False,
                update_on: List[str | Tuple[str, int]] = None,
                enable_quick_search: bool = False,
                excel_export_mode: str = "none",
                excel_export_multiple_sheets: Dict = None,
                **kwargs):
        """ Create a new immutable AgGridBuilder class object. """
        obj = super().__new__(cls)

        # process data that needs to be cleansed
        obj.data = _serialize_data(data)
        obj.columns_auto_size_mode = _process_auto_size_mode(columns_auto_size_mode.lower())
        obj.return_mode = _process_return_mode(return_mode.lower())
        obj.convert_to_original_types = convert_to_original_types
        obj.errors = _process_conversion_errors(convert_to_original_types, errors.lower())
        obj.theme = _process_theme(theme.lower())
        obj.excel_export_mode = _process_excel_export_mode(excel_export_mode.lower())

        # remaining items do not need cleaning
        obj.height = height
        obj.allow_unsafe_js = allow_unsafe_js
        obj.enable_enterprise_modules = enable_enterprise_modules
        obj.license_key = license_key
        obj.reload_data = reload_data
        obj.columns_state = column_state
        obj.custom_css = custom_css
        obj.use_legacy_selected_rows = use_legacy_selected_rows
        obj.update_on = update_on
        obj.enable_quick_search = enable_quick_search
        obj.excel_export_multiple_sheets = excel_export_multiple_sheets

        # handle the grid options now
        obj.grid_options = GridOptionsBuilder(grid_options, data, custom_css, **kwargs)
        
        return obj.process_deprecated(**kwargs)

    def process_deprecated(self, **kwargs: Mapping):
        """ In case we need to process deprecated parameters, handle them here. """
        return self
