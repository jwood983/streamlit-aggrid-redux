""" This module helps users construct the necessary grid options parameters to pass to AgGrid. """
import json

from typing import Dict, Union, Mapping, List, Callable, Literal
from streamlit.type_util import convert_anything_to_df

# local import
from .types import DataElement
from .errors import GridOptionsBuilderError


def _pandas_types(d: str) -> Dict:
    """ Convert the column type to a list of AgGrid types. """
    if d in ("i", "u", "f") or any(y in str(d) for y in ("int", "float", "double")):
        # a numeric column (integer or float)
        return dict(type="numericColumn", filter="numberColumnFilter")
    elif d == "m":
        # a timedelta column
        return dict(type="timedeltaFormat")
    elif d == "M":
        # date format
        return dict(type="dateColumn", filter="dateColumnFilter")
    else:
        # is either s text column or unknown data, treat as text
        return dict(type="rightAligned", filter="textColumnFilter")


class GridOptionsBuilder:
    """This class helps users who are unfamiliar with JS and/or
    AgGrid build the necessary dictionary needed for AgGrid to
    produce better quality grids. It is preferred to pass the
    whole element as a data dictionary than to use this class
    """
    def __init__(self, grid_options: Dict = None, **kwargs):
        if grid_options is not None:
            self.grid_options = grid_options
        else:
            self.grid_options = dict()

        # ensure the column defs is present
        if "columnDefs" not in self.grid_options:
            self.grid_options["columnDefs"] = dict()
            
        # use 'update' method to update with the remaining kwargs
        self.grid_options.update(kwargs)

        # save the default options for the grid
        self.default_options = dict(
            minWidth=100,
            editable=False,
            sortable=True,
            resizable=True
        )
        if "defaultColDef" in kwargs:
            self.default_options.update(kwargs["defaultColDef"])
        else:
            self.default_options.update(kwargs)

    @staticmethod
    def from_data(data: DataElement) -> 'GridOptionsBuilder':
        """For people who like defaults and simple things,
        this API allows users to pass in the data and
        let this package fill the columns and set the
        defaults.

        Parameters
        ----------
        data: {np.ndarray, pd.DataFrame, pa.Table}
            The data we're processing to set the grid
            options.

        Returns
        -------
        GridOptionsBuilder
            The object with decent defaults.
        """
        # options with nothing passed
        opt = GridOptionsBuilder(grid_options=dict())

        # push the default options
        opt.grid_options.update(**{"defaultColDef": opt.default_options})

        # convert the input to a frame to generate the options directly from pandas
        frame = convert_anything_to_df(data, ensure_copy=True, allow_styler=False)
        for name, dtype in zip(frame.columns, frame.dtypes):
            if "." in name:
                opt.grid_options.update(**{"suppressFieldDotNotation": True})
            opt.add_column(name, name, **_pandas_types(str(dtype)))
       
        return opt

    def add_column(self, field: str, header: str = None, **options: Mapping) -> 'GridOptionsBuilder':
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

        header_name = field if header is None else header
        defs = dict(headerName=header_name, field=field)

        if options is not None:
            defs.update(**options)
        else:
            defs.update(**self.default_options)

        self.grid_options["columnDefs"][field] = defs
        return self

    def update_column(self, field: str, header: str = None, **options: Mapping) -> 'GridOptionsBuilder':
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
        if field not in self.grid_options["columnDefs"]:
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
        """Add filters and/or column details to the sidebar.
        Defaults are to ignore both, so this must be explicitly
        marked.

        Parameters
        ----------
        filters: bool, optional
            A flag to add filters tool panel to the sidebar.
            Default is False to not add it.

        columns: bool, optional
            A flag to add selectable columns tool pane
            to the sidebar. Default is False to not
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
                
        # handle columns now (fall-through of the `if` is intended)
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

        # save the sidebar
        self.grid_options["sideBar"] = side_bar
        return self

    def add_grid_selection(self,
                           selection_mode: Literal["single", "multiple", "disabled"] = "single",
                           use_checkbox: bool = False,
                           use_header_checkbox: bool = False,
                           use_header_checkbox_filtered: bool = False,
                           clear_checkbox_on_reload: bool = False,
                           pre_selected_rows: List[int] = None,
                           multi_select_with_click: bool = False,
                           suppress_deselection: bool = False,
                           suppress_click_selection: bool = False,
                           group_selects_children: bool = True,
                           group_selects_filtered: bool = True) -> 'GridOptionsBuilder':
        """Configure how AgGrid applies user selections.

        Parameters
        ----------
        selection_mode: str, optional
            Determines how selections are done. Either
            "single", "multiple" or "disabled". Default
            is "single".

        use_checkbox: bool, optional
            A flag to indicate whether we should have
            a checkbox next to each row. Default is
            False to disable the box.

        use_header_checkbox: bool, optional
            A flag to indicate whether we should have
            a checkbox next to each header. Default
            is False to disable the box.

        use_header_checkbox_filtered: bool, optional
            If `use_header_checkbox` is True, then this
            parameter applies to the filtered result.
            Default is False.

        clear_checkbox_on_reload: bool, optional
            If using checkboxes, this option will allow
            AgGrid to clear the selected cells on the
            next grid reload. Default is False.

        pre_selected_rows: List[int], optional
            A list of rows to select on first load.
            Default is None to not select any.

        multi_select_with_click: bool, optional
            A flag indicating whether users can select
            multiple rows simply by clicking or if
            Shift key must be used (False). Default is
            False to force use of Shift key.

        suppress_deselection: bool, optional
            A flag indicating whether Ctrl key can suppress
            deselecting all other rows. Default is False.

        suppress_click_selection: bool, optional
            A flag indicating that clicking should not
            select a row. Default is False.

        group_selects_children: bool, optional
            A flag indicating that when the group is
            selected, all the elements of the group
            are selected. Default is True.

        group_selects_filtered: boo, optional
            A flag indicating that when the group is
            selected, the filtered rows are also
            selected. Default is True.

        Returns
        -------
        GridOptionsBuilder
           The updated object.
        """
        if selection_mode == "disabled":
            self.grid_options.pop("rowSelection", None)
            self.grid_options.pop("rowMultiSeletWithClick", None)
            self.grid_options.pop("suppressRowDeselection", None)
            self.grid_options.pop("suppressRowClickSelection", None)
            self.grid_options.pop("groupSelectsChildren", None)
            self.grid_options.pop("groupSelectsFiltered", None)
            return self

        # process the checkboxes
        if use_checkbox:
            # ensure this is true when using checkboxes!
            suppress_click_selection = True
            # we only need to parse the first key because it will apply to all
            first_key = next(iter(self.grid_options["columnDefs"].keys()))
            self.grid_options["columnDefs"][first_key].update(
                dict(
                    checkboxSelection=True,
                    headerCheckboxSelection=use_header_checkbox,
                    headerCheckboxSelectionFilteredOnly=use_header_checkbox_filtered,
                )
            )
            # push checkbox clearing to main grid options
            self.grid_options["clearCheckboxOnReload"] = clear_checkbox_on_reload

        # now maybe add pre-selected rows
        if pre_selected_rows is not None and len(pre_selected_rows) > 0:
            self.grid_options.update(**{"preSelectedRows": pre_selected_rows})

        # add remaining options directly--note the case sensitivity of the arguments!
        self.grid_options.update(
            **dict(
                rowSelection="single" if selection_mode.lower().startswith("si") else "multiple",
                rowMultiSelectWithClick=multi_select_with_click,
                suppressRowDeselection=suppress_deselection,
                suppressRowClickSelection=suppress_click_selection,
                groupSelectsChildren=group_selects_children,
                groupSelectsFiltered=group_selects_filtered
            )
        )
        return self

    def add_pagination(self, auto_page_size: bool = True, page_size: int = 10) -> 'GridOptionsBuilder':
        """Insert the pagination to reduce the size of
        the grid on the page. By using this API,
        pagination is automatically enabled.

        Parameters
        ----------
        auto_page_size: bool, optional
            A flag indicating that AgGrid should
            automatically calculate optimal page
            sizes. Default is True. This parameter
            takes precedence over the page size.

        page_size: int, optional
            If the previous is False, sets the maximum
            number of rows on a page. Default is 10.

        Returns
        -------
        GridOptionsBuilder
            The updated object.
        """
        if auto_page_size:
            self.grid_options.update(
                **dict(
                    pagination=True,
                    paginationAutoPageSize=True
                )
            )
        else:
            self.grid_options.update(
                **dict(
                    pagination=True,
                    paginationPageSize=page_size
                )
            )
        return self

    def remove_pagination(self) -> 'GridOptionsBuilder':
        """Remove pagination from the builder.

        Returns
        -------
        GridOptionsBuilder
            The updated object.
        """
        self.grid_options.pop("pagination", None)
        self.grid_options.pop("paginationAutoPageSize", None)
        self.grid_options.pop("paginationPageSize", None)
        return self 

    def build(self) -> Dict:
        """After completing all the elements, call this
        to return the data dictionary.

        Returns
        -------
        Dict
            The grid options data dictionary.
        """
        if not isinstance(self.grid_options["columnDefs"], list):
            self.grid_options.update(
                **dict(
                    columnDefs=list(self.grid_options["columnDefs"].values())
                )
            )
            
        return self.grid_options

    def __str__(self):
        """ Print the grid options. """
        return json.dumps(self.grid_options, indent=4)


def walk_grid_options(grid_opts: Dict, function: Callable):
    """Apply the input function to the grid options dictionary.

    Parameters
    ----------
    grid_opts: Dict
        The grid options dictionary that needs to ensure we
        have a valid JsCode Function applied to the setting.

    function: Callable
        A callable function that takes in a single agument
        (usually a string) and returns a single argument (also
        usually a string).
    """
    if isinstance(grid_opts, (Mapping, List)):
        for _, k in enumerate(grid_opts):
            if isinstance(grid_opts[k], Mapping):
                walk_grid_options(grid_opts[k], function)
            elif isinstance(grid_opts[k], List):
                for elem in grid_opts[k]:
                    walk_grid_options(elem, function)
                else:
                    grid_opts[k] = function(grid_opts[k])
