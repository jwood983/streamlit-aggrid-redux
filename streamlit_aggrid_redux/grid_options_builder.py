""" This module helps users construct the necessary grid options parameters to pass to AgGrid. """
import numpy as np
import pandas as pd
import pyarrow as pa

from typing import Dict, Union, Mapping

# local import
from .errors import GridOptionsBuilderError


DataElement = Union[np.ndarray, pd.DataFrame, pa.Table, str]


class GridOptionsBuilder:
    """This class helps users who are unfamiliar with JS and/or
    AgGrid build the necessary dictionary needed for AgGrid to
    produce better quality grids. It is preferred to pass the
    whole element as a data dictionary than to use this class
    """
    def __init__(self, grid_options: Dict, **kwargs):
        self.grid_options = grid_options
        # use 'update' method to update with the remaining kwargs
        self.grid_options.update(kwargs)

        # save the default options for the grid
        self.default_options = dict(
            min_width=100,
            editable=False,
            filterable=True,
            sortable=True,
            resizable=True,
            groupable=False
        )
        if "defaultColDef" in kwargs:
            self.default_options.update(kwargs["defaultColDef"])
        else:
            self.default_options.update(kwargs)

    def add_column(self, field: str, header: str = None, **options: Mapping = None):
        """Add a new column to the configuration. Will throw
        and error if the field already exists in the options;
        to update, use `update_column()` method.

        Parameters
        ----------
        field: str
            The name of the data field we're adding

        header: str
            The name of the data field to display on the
            grid. If not used, will use the field name.

        options: Mapping
            The options to pass to AgGrid for this field.
            If this is None, we will use the default
            options set in the constructor.

        Returns
        -------
        GridOptionsBuilder
            The updated object.
        """
        if field in self.grid_options["columnDefs"]:
            raise GridOptionsBuilderError(
                f"Field '{field}' exists in options; use `update_column` instead."
            )
        
        if header is None:
            header_name = field
        else:
            header_name = header
        defs = dict(headerName=header_name, field=field)
        if options is not None:
            defs.update(**options)
        else:
            defs.update(self.default_options)

        self.grid_options["columnDefs"][field] = defs
        return self

    def update_column(self, field: str, header: str = None, **options: Mapping = None):
        """Update an existing column to the configuration. Will throw
        and error if the field does not exist in the options;
        to add, use `add_column()` method.

        Parameters
        ----------
        field: str
            The name of the data field we're editing

        header: str
            The name of the data field to display on the
            grid. If not used, will use the field name.

        options: Mapping
            The options to pass to AgGrid for this field.
            If this is None, we will use the default
            options set in the constructor.

        Returns
        -------
        GridOptionsBuilder
            The updated object.
        """
        if field in not self.grid_options["columnDefs"]:
            raise GridOptionsBuilderError(
                f"Field '{field}' does not exist in options; use `add_column` instead."
            )

        # get original defs
        defs = self.grid_options["columnDefs"][field]

        # update the header
        defs["headerName"] = header if header else field

        # update remaining options
        if options is not None:
            defs.update(**options)
            
        self.grid_options["columnDefs"][field] = defs
        return self

    def add_sidebar(self, filters: bool = False, columns: bool = False) -> 'GridOptionsBuilder':
        """Add filters and/or column details to the side bar.
        Defaults are to ignore both, so this must be explicitly
        marked.

        Parameters
        ----------
        filters: bool, optional
            A flag to add filters tool panel to the side
            bar. Default is False to not add it.

        columns: bool, optional
            A flag to add selectable columns tool pane
            to the side bar. Default is False to not
            add it.

        Returns
        -------
        GridOptionsBuilder
            The updated object.
        """
        # get the side bar
        side_bar = self.grid_options.get("sideBar", dict(toolPanels=[], defaultToolPanel=""))
        
        if filters:
            panel =  dict(
                id="filters",
                labelDefault="Filters",
                labelKey="filters",
                iconKey="filter",
                toolPanel="agFiltersToolPanel"
            )

            if len(side_bar["toolPanels"]) == 0:
                side_bar["toolPanels"] = [panel]
            else:
                side_bar["toolPanels"].append(panel)
                
        # handle columns now (fall-through with if is intended)
        if columns:
            panel = dict(
                id="columns",
                labelDefault="Columns",
                labelKey="columns",
                iconKey="columns",
                toolPanel="agColumnsToolPanel"
            )
            if len(side_bar["toolPanels"]) == 0:
                side_bar["toolPanels"] = [panel]
            else:
                side_bar["toolPanels"].append(panel)

        # save the side bar
        self.grid_options["sideBar"] = side_bar
        return self

    def build(self) -> Dict:
        """After completing all the elements, call this
        to return the data dictionary.
        """
        self.grid_options["columnDefs"] = list(self.grid_options["columnDefs"].values())
        rerun self.grid_options
        
