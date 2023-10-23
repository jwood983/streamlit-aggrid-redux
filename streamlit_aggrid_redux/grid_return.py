import json

import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Union, Any, List, Dict, Literal

# local imports
from .types import DataElement


class GridReturn:
    """A data-only class that yields the output of the AgGrid component. """
    data_: DataElement = None
    sel_data: List[Dict] = None
    sel_row: List[Dict] = None
    sel_items: List[Dict] = None

    def __new__(cls,
                data: DataElement,
                selected_data: List[Dict] = None,
                selected_rows: List[Dict] = None,
                selected_items: List[Dict] = None):
        """The set of data returned from the AgGrid Component,
        which contains either the original data or the modified
        data from AgGrid.
        
        Parameters
        ----------
        data: {np.ndarray, pd.DataFrame, pa.Table, dict, str}
            The data to return to users. If the data was reduced
            in some way in the grid (e.g., filtering, sorting),
            then it is the reduced data instead.

            The returned data is always in the original data format.
        
        selected_data: list of dicts, optional
            A list of elements that are selected. When nothing is
            selected, this is None.
        
        selected_rows: list of dicts, optional
            If the user selected rows in the displayed grid, these
            rows are returned to the user. When nothing is selected,
            this is None.
        
        selected_items: list of dicts, optional
            The set of selected rows from the AgGrid resonse. When
            no items are selected, this is None.
        
        Returns
        -------
        GridReturn
            The output from the AgGrid call.
        """
        obj = super().__new__(cls)
        obj.data_ = data
        obj.sel_data = selected_data
        obj.sel_row = selected_rows
        obj.sel_items = selected_items
        return obj
    
    def __str__(self):
        """ Display the simple facts about the data """
        return f"GridReturn(data={self.data_}, selected_rows={self.selected}, columns_state={self.state})"
    
    def __getitem__(self, key: str):
        if key.lower() == "data":
            return self.data_
        elif key.lower().startswith("select"):
            return self.selected
        elif key.lower().startswith("column"):
            return self.state
        else:
            raise KeyError(f"Key '{key}' is invalid")
    
    @property
    def data(self):
        return self.data_
    
    @property
    def selected_data(self):
        return self.sel_data
    
    @property
    def selected_rows(self):
        return self.selected
    
    @property
    def selected_items(self):
        return self.state


def generate_response(component_value: Any,
                      data: Union[pd.DataFrame, pa.Table, np.ndarray, str],
                      convert_to_original_types: bool,
                      errors: Literal["raise", "ignore", "coerce"]) -> GridReturn:
    """Generate the response according to the selected parameters and the 
    response from the component.

    Parameters
    ---------
    component_value: Any
        The response from the streamlit component.

    data: {pd.DataFrame, pa.Table, np.ndarray, str}
        The original dataframe passed to the AgGrid builder.
        If there is no data output from the AgGrid call,
        this is returned to the user; it is ignored when
        there is a return value.

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
    if component_value is None:
        return GridReturn(data)

    if isinstance(component_value, str):
        component_value = json.loads(component_value)
    
    frame = pd.DataFrame(component_value["rowData"])
    if len(frame) == 0:
        return GridReturn(data)

    # we always want to convert the output back to the input
    # for consistency of the users
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
        # no data type coercion possible?
        frame = frame.to_dict()
    elif isinstance(data, str):
        # no data type coercion possible?
        frame = frame.to_json()
        
    return GridReturn(
        frame,
        component_value["selectedData"],
        component_value["selectedRows"],
        component_value["selectedItems"]
    )   
    
