import json

import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Union, Any, List, Dict, Literal


class GridReturn(tuple):
    """ Effectively this class is a named tuple. """
    data: Union[pd.DataFrame, pa.Table, np.ndarray, dict, str] = None
    selected_rows: List[Dict] = None
    column_state: List[Dict] = None

    def __new__(cls,
                data: Union[pd.DataFrame, pa.Table, np.ndarray, dict, str] = None,
                selected_rows: List[Dict] = None,
                column_state: List[Dict] = None):
        obj = super().__new__(cls)
        obj.data = data
        obj.selected_rows = selected_rows
        obj.column_state = column_state
        return obj


def _cast_to_time_delta(x: pd.Series) -> Union[pd.Timedelta, pd.Series]:
    """ Try coercing the series to a Timedelta object. """
    try:
        return pd.Timedelta(x)
    except ValueError:
        return x


def generate_response(data: Union[pd.DataFrame, pa.Table, np.ndarray, str],
                      component_value: Any,
                      convert_to_original_types: bool,
                      errors: Literal["raise", "ignore", "coerce"]) -> GridReturn:
    """Generate the response according to the selected parameters and the 
    response from the component.

    Parameters
    ---------
    data: {pd.DataFrame, pa.Table, np.ndarray, str}
        The original dataframe passed to the AgGrid builder.
        If there is no data output from the AgGrid call,
        this is returned to the user; it is ignored when
        there is a return value.

    component_value: Any
        The response from the streamlit component.

    convert_to_original_types: bool
        The flag indicating if we should try converting the
        columns to their original types.

    errors: {"raise", "ignore", "coerce"}
        A string indicating how errors should be handled
        in converting the columns.

    Returns
    -------
    GridReturn
        The returned namedtuple-like class that contains the
        responses from the AgGrid Component.
    """
    if not component_value:
        return GridReturn(data)

    if isinstance(component_value, str):
        component_value = json.loads(component_value)
    
    frame = pd.DataFrame(component_value["rowData"])
    if len(frame) == 0:
        return GridReturn(data)

    # check types before converting
    if isinstance(data, pd.DataFrame):
        if convert_to_original_types:
            frame = frame.astype(data.dtypes.to_dict(), errors=errors)
    elif isinstance(data, pa.Table):
        if convert_to_original_types:
            frame = pa.Table.from_pandas(frame, data.schema)
        else:
            frame = pa.Table.from_pandas(frame)
    elif isinstance(data, np.ndarray):
        if convert_to_original_types:
            frame = frame.to_numpy(dtype=data.dtype)
        else:
            frame = frame.to_numpy()
    elif isinstance(data, dict):
        # no data type coercion possible
        frame = frame.to_dict()
    elif isinstance(data, str):
        # no data type coercion possible?
        frame = frame.to_json()
        
    return GridReturn(
        frame,
        component_value["selectedItems"],
        component_value["colState"]
    )   
    
