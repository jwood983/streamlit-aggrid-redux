""" The main workhorse of the package, massages inputs to fit component needs. """
import json
import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Any, List, Mapping, Union, Any, Dict, Tuple

# local import
from .errors import GridBuilderError, GridOptionsBuilderError
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
        
        
def _serialize_data(data: DataElemet) -> Dict:
    """ Convert the input data element into a JSON string. """
    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient="records")
    elif isinstnace(data, pa.Table):
        # There ought to be a better way for serializing pyarrow tables
        return data.to_pydict()
    elif isinstance(data, np.ndarray):
        # use json decoder
        return json.dumps(data, cls=NumpyArrayEncoder)
    elif isinstance(data, str):
        # presume it's already JSON
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            raise GridBuilderError("Cannot convert input data from string to JSON dictionary")
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
    if theme not in ("alpine", "balham", "material",  "streamlit", "excel", "astro"):
        raise GridBuilderError(
            _make_error_msg("Theme", theme, ["alpine", "balham", "material", "streamlit", "excel", "astro"])
        )
    return theme


def _process_excel_export_mode(mode: str) -> str:
    """ Ensure the excel export mode is set correctly. """
    if mode == "none":
        return "NONE"
    elif mode == "manual":
        return "MANUAL"
    elif mode == "automatic":
        return "TRIGGER"
    else:
        raise GridBuilderError(
            _make_error_msg("Excel export mode", mode, ["none", "manual", "automatic"])
        )


def _process_data_types(convert: bool, data: DataElement) -> List:
    """ If conversion is requested, return the list of data element types. """
    if not convert:
        return []
    if isinstance(data, pd.DataFrame):
        return dict(zip(data.columns, (t.kind for t in data.dtypes)))
    elif isinstance(data, pa.Table):
        # FIXME: ensure this works. Could just use above
        schema = data.schema
        return dict(zip(data.column_names, (schema.field(c).type for c in data.column_names)))
    elif isinstance(data, np.ndarray):
        # FIXME: figure this one out
        return []
    else:
        raise GridBuilderError(f"Cannot get data types of input data with type '{type(data)}'")
        

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
    enable_enterprise_modules: bool = True
    license_key: str = None
    convert_to_original_types: bool = True
    errors: str = "coerce"
    dtypes: Union[List[str], Dict[str, List[str]]] = None
    reload_data: bool = False
    columns_state: List[Dict] = None
    theme: str = "streamlit"
    custom_css: str = None
    update_on: List[Union[str, Tuple[str, int]]] = None
    enable_quick_search: bool = False
    excel_export_mode: str = "none"

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
        obj.dtypes = _process_data_types(convert_to_original_types, data)

        # remaining items do not need cleaning
        obj.height = height
        obj.allow_unsafe_js = allow_unsafe_js
        obj.enable_enterprise_modules = enable_enterprise_modules
        obj.license_key = license_key
        obj.reload_data = reload_data
        obj.columns_state = column_state
        obj.custom_css = custom_css
        obj.update_on = update_on
        obj.enable_quick_search = enable_quick_search

        # handle the grid options now
        if isinstance(grid_options, GridOptionsBuilder):
            obj.grid_options = grid_options.build()
        elif isinstance(grid_options, dict):
            obj.grid_options = grid_options

        # now update with the passed kwargs
        obj.grid_options.update(**kwargs)
        
        return obj.process_deprecated(**kwargs)

    def process_deprecated(self, **kwargs: Mapping):
        """ In case we need to process deprecated parameters, handle them here. """
        return self
