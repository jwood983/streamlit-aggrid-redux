""" This is the initial import function for using Streamlit AgGrid Redux. """
import streamlit.components.v1 as components

# common imports
import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Union, List, Dict, Tuple
from decouple import config as dconfig
from streamlit.components.v1.components import MarshallComponentException

# local imports
from .code import JsCode
from .errors import AgGridBuilderError, AgGridOptionsBuilderError
from .grid_return import AgGridReturn, generate_response
from .grid_options import AgGridOptions
from .grid_options_builder import AgGridOptionsBuilder, walk_grid_options

# ensure these imports can be used in Python code importing this module
__all__ = [
    'JsCode',
    'AgGridBuilderError', 'AgGridOptionsBuilderError',
    'AgGridReturn',
    'AgGridOptions',
    'AgGridOptionsBuilder'
]


_RELEASE = dconfig("AGGRID_RELEASE", default=True, cast=bool)

if not _RELEASE:
    warnings.warn("WARNING: ST_AGGRID is in development mode.")
    _component_func = components.declare_component("agGrid", url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend","build")
    _component_func = components.declare_component("agGrid", path=build_dir)


# the main api
def ag_grid(
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
    columns_state: List[Dict]: None,
    theme: str = "streamlit",
    custom_css: str = None,
    use_legacy_selected_rows: bool = False,
    key: str = None,
    update_on: List[str | Tuple[str, int]] = None,
    enable_quick_search: bool = False,
    excel_export_mode: str = "none",
    excel_export_multiple_sheets: Dict: None,
    **kwargs):
    """ FIXME: add all parameters. """
    # throw an error for now
    raise NotImplementedError("Working on it")
    # first, use an internal class to massage the API inputs
    try:
        grid = AgGridBuilder(
            data,
            grid_options,
            (height, None),
            columns_auto_size_mode,
            return_mode,
            allow_unsafe_js,
            enable_enterprise_modules,
            license_key,
            convert_to_original_types,
            errors,
            reload_data,
            columns_state,
            theme
            custom_css,
            update_on,
            enable_quick_search,
            excel_export_mode,
            excel_export_multiple_sheets
        )
    except (AgGridBuilderError, AgGridOptionsBuilderError, Exception) as err:
        # rereaise errors
        raise err
    
    # now call the component
    try:
        component_value = _component_func(
            grid_ptions=grid.gridOptions,
            row_data=grid.row_data,
            height=grid.height,
            columns_auto_size_mode=cgrid.olumns_auto_size_mode, 
            return_mode=grid.return_mode, 
            frame_dtypes=grid.dtypes,
            allow_unsafe_js=grid.allow_unsafe_jsc,
            enable_enterprise_modules=grid.enable_enterprise_modules,
            license_key=grid.license_key,
            reload_data=grid.reload_data,
            columns_state=grid.columns_state,
            theme=grid.theme,
            custom_css=grid.custom_css,
            update_on=grid.update_on,
            manual_update=grid.manual_update,
            enable_quicksearch=grid.enable_quicksearch,
            excel_export_mode=grid.excel_export_mode,
            excel_export_multiple_sheets=grid.excel_export_multiple_sheets,
            key=key
        )
    except MarshallComponentException as err:
        # reraise this error but with JsCode note on it first
        args = list(ex.args)
        args[0] += ". If you're using custom JsCode objects on gridOptions, ensure that allow_unsafe_jscode is True."
        ex = MarshallComponentException(*args)
        raise(ex)

    # now generate the response
    return generate_response(component_value, data, grid.convert_to_original_types, grid.errors)
        
