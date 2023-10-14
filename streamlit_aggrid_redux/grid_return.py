import json

import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Union, Tuple, Any, Optional


class AgGridReturn(tuple):
    """ Effectively this class is a named tuple. """
    data: Union[pd.DataFrame, pa.Table, np.ndarray, str] = None
    selected_rows: List[Dict] = None
    column_state: List[Dict] = None
    excel_blob: Dict = None

    def __new__(cls,
                data: Union[pd.DataFrame, pa.Table, np.ndarray, str] = None,
                selected_rows: List[Dict] = None,
                column_state: List[Dict] = None,
                excel_blob: Dict = None):
        obj = super().__new__(cls)
        obj.data = data
        obj.selected_rows = selected_rows
        obj.column_state = column_state
        obj.excel_blob = excel_blob


def _cast_to_time_delta(x: pd.Series, errors: str) -> Optional[pd.Timedelta]:
    """ Try coercing the series to a Timedelta object. """
    try:
        return pd.Timedelta(x)
    except (ValueError, ):
        return s


def generate_response(data: Union[pd.DataFrame, pa.Table, np.ndarray, str],
                      component_value: Any,
                      convert_to_original_types: bool,
                      errors: str,
                      use_legacy_selected_rows: bool):
    """Generate the response according to the selected parameters and the 
    response from the component.

    Parameters
    ---------
    data: {pd.DataFrame, pa.Table, np.ndarray, str}
        The original dataframe passed to the AgGrid builder

    component_value: Any
        The response from the streamlit component.

    convert_to_original_types: bool
        The flag indicating if we should try converting the
        columns to their original types.

    errors: str
        A string indicating how errors should be handled
        in converting the columns.

    use_legacy_selected_rows: bool
        The flag indicating whether the selected rows are
        using the legacy format (True) or the current format
        (False). In most cases, the current is preferred.

    Returns
    -------
    AgGridReturn
        The returned namedtuple-like class that contains the
        responses from the AgGrid Component.
    """
    if not component_value:
        return AgGridReturn(data)

    if isinstance(component_value, str):
        component_value = json.loads(component_value)
    
    frame = pd.DataFrame(component_value["rowData"])
    original_types = component_value["originalDtypes"]

    if convert_to_original_types and not frame.empty:
        numeric_cols = [k for k, v in original_types.items() if v in ("i", "u", "f")]
        if len(numeric_cols) > 0:
            frame.loc[:, numeric_cols] = frame.loc[:, numeric_cols].apply(pd.to_numeric, errors=errors)

        text_cols = [k for k, v in original_types.items() if v in ("O", "S", "U")]
        if len(text_cols) > 0:
            frame.loc[:, text_cols] = frame.loc[:, text_cols].applymap(lambda x: np.nan if x is None else str(x))

        date_cols = [k for k, v in original_types.items() if v == "M"]
        if len(date_cols) > 0:
            frame.loc[:, date_cols] = frame.loc[:, date_cols].apply(pd.to_datetime, errors=errors)

        date_cols = [k for k, v in original_types.items() if v == "m"]
        if len(date_cols) > 0:
            frame.loc[:, date_cols] = frame.loc[:, date_cols].apply(_cast_to_time_delta, errors=errors)

    select_elem = "selectedRows" if use_legacy_selected_rows else "selectedItems"
    return AgGridReturn(
        data,
        component_value[selected_elem],
        component_value["colState"],
        component_value["ExcelBlob"]
    )   
    
