""" The main workhorse of the package, massages inputs to fit component needs. """
import json
import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Any, List, Mapping, Union, Any, Dict, Tuple

# local import
from .errors import AgGridBuilderError, AgGridOptionsBuilderError
from .grid_options_builder import GridOptionsBuilder, walk_grid_options


class AgGridBuilder:
    data: str = "{}"
    grid_options: Dict = None
    shape: Tuple[int, int] = None
    columns_auto_size_mode: str = "none"
    return_mode: str = "input"
    allow_unsafe_js: bool = False
    enable_enterprise_modules: bool = True  # FIXME: maybe eliminate this, just need license key?
    license_key: str = None
    convert_to_original_types: bool = True
    errors: str = "coerce"
    reload_data: bool = False
    columns_state: List[Dict]: None
    theme: str = "streamlit"
    custom_css: str = None
    update_on: List[str | Tuple[str, int]] = None
    enable_quick_search: bool = False
    excel_export_mode: str = "none"
    excel_export_multiple_sheets: Dict: None

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
    """ Create a new immutable AgGridBuilder class object. """
    obj = super().__new__(cls)
    
    return obj
