""" This is the initial import function for using Streamlit AgGrid Redux. """
import streamlit.components.v1 as components

# common imports
from typing import Union, List, Dict, Tuple, Mapping
from decouple import config
from streamlit.components.v1.components import MarshallComponentException

# local imports
from .code import JsCode
from .errors import AgGridBuilderError, AgGridOptionsBuilderError
from .grid_return import AgGridReturn, generate_response
from .grid_builder import AgGridBuilder, DataElement
from .grid_options_builder import AgGridOptionsBuilder, walk_grid_options

# ensure these imports can be used in Python code importing this module
__all__ = [
    'JsCode',
    'AgGridBuilderError', 'AgGridOptionsBuilderError',
    'AgGridReturn',
    'AgGridBuilder', 'DataElement'
    'AgGridOptionsBuilder'
]


_RELEASE = config("AGGRID_RELEASE", default=True, cast=bool)

if not _RELEASE:
    warnings.warn("WARNING: streamlit-aggrid-redux is in development mode.")
    _component_func = components.declare_component("agGrid", url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend","build")
    _component_func = components.declare_component("agGrid", path=build_dir)


# the main api
def ag_grid(
    data: DataElement,
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
    key: str = None,
    update_on: List[str | Tuple[str, int]] = None,
    enable_quick_search: bool = False,
    excel_export_mode: str = "none",
    excel_export_multiple_sheets: Dict = None,
    **kwargs: Mapping) -> AgGridReturn:
    """Render the input data element using JS AgGrid.

    Parameters
    ----------
    data: {pd.DataFrame, pa.Table, np.ndarray, str}
        The data element to display.

    grid_options: dict, optional
        The optional set of parameters to pass to AgGrid
        that specify how the data is displayed on screen.
        See https://www.ag-grid.com/javascript-data-grid/grid-options/
        for details. Default is None to use AgGrid defaults.

    height: int, optional
        The height of the grid, in pixels. Default is
        None to let AgGrid decide height.
        
    columns_auto_size_mode: str, optional
        A string flag to determine how AgGrid handles the width
        of columns. Options are "none", "fit" and "fit all".
        Default is "none" to not auto-size the columns.
        
    return_mode: str, optional
        A string flag that determines how the data is returned
        from AgGrid. Options are "input", "filter" and "filter sort".
        Default is "input".
        
    allow_unsafe_js: bool, optional
        A flag indicating whether we want to inject JS into the
        grid options (e.g., for formatting numbers or dates). Default
        is False.

        WARNING: There are no protections or checks of the code
        injected. Use at your own risk.
        
    enable_enterprise_modules: bool, optional
        A flag indicating whether AgGrid Enterprise Modules are 
        available (True) or not (False). Default is True, but
        requires a license key.
        
    license_key: str, optional
        The AgGrid Enterprise Module license key. Unused if
        `enable_enterprise_modules=False`. Default is None.
        
    convert_to_original_types: bool, optional
        A flag indicating whether the modified data output should
        coerced back to the original types. Default is True.
        
    errors: str, optional
        A string flag to passed to Pandas data converters. Options
        are "coerce", "ignore" or "raise". Default is "coerce" which
        makes invalid cells NaN/NaT.
        
    reload_data: bool, optional
        A flag indicating whether AgGrid should reload data when
        refreshing. Default is False.
        
    columns_state: List[Dict], optional
        A set of dictionaries of how the data should be displayed 
        in AgGrid. Default is None.
        
    theme: str, optional
        The theme to apply to the AgGrid display. Options are "streamlit",
        "alpine", "balham" and "excel".
        
    custom_css: str, optional
        A stringified dictionary of custom CSS commands to pass to
        AgGrid. Default is None.
        
    use_legacy_selected_rows: bool, optional
        A flag indicating how the return value from AgGrid is processed.
        Default is False to use current method, which should be all use
        cases.
        
    key: str, optional
        The streamlit key to pass to the component function for cases
        when data is displayed twice to avoid singleton errors. Default
        is None.
        
    update_on: List[str | Tuple[str, int]], optiona
        A list of AgGrid update methods when a cell is modified. See
        https://www.ag-grid.com/javascript-data-grid/cell-editing/#editing-events
        for details. Default is None.
        
    enable_quick_search: bool, optional
        A flag indicating whether the quick search bar should appear
        at the top of the grid (True) or not (False). Default is False.
        
    excel_export_mode: str, optional
        A string flag indicating how Excel export should be handled. Options
        are "none", "manual", "file blob", "sheet blob", "trigger" and
        "multiple". Default is "none"; when exporting is desired, most use
        cases should be "manual".
        
    excel_export_multiple_sheets: Dict[str, List[str]], optional
        A dictionary indicating which sheets contains which columns. The
        sheet names are the dictionary keys while the list of columns are
        the values. Default is None

    **kwargs: Mapping
        All remaining inputs are passed as key-value pairs to the grid options
        dictionary. Default is None.

    Returns
    -------
    AgGridReturn
        An immutable class that returns the output from the AgGrid (e.g., 
        after modifications, filtering, sorting).
    """
    # first, use an internal class to massage the API inputs
    try:
        grid = AgGridBuilder(
            data,
            grid_options,
            height,
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

    # if not in release mode, we hide a parameter "return_grid" that returns the grid
    if not _RELEASE and "return_mode" in kwargs and kwargs["return_mode"]:
        return grid

    # throw an error for now
    raise NotImplementedError("Working on it")
    
    # now call the component
    try:
        component_value = _component_func(
            grid_options=grid.grid_ptions,
            row_data=grid.data,
            height=grid.height,
            columns_auto_size_mode=grid.columns_auto_size_mode, 
            return_mode=grid.return_mode, 
            data_types=grid.data_types,
            allow_unsafe_js=grid.allow_unsafe_js,
            enable_enterprise_modules=grid.enable_enterprise_modules,
            license_key=grid.license_key,
            reload_data=grid.reload_data,
            columns_state=grid.columns_state,
            theme=grid.theme,
            custom_css=grid.custom_css,
            update_on=grid.update_on,
            manual_update=grid.manual_update,
            enable_quick_search=grid.enable_quick_search,
            excel_export_mode=grid.excel_export_mode,
            excel_export_multiple_sheets=grid.excel_export_multiple_sheets,
            key=key
        )
    except MarshallComponentException as err:
        # reraise this error but with JsCode note on it first, maybe.
        args = list(err.args)
        if not grid.allow_unsafe_js:
            args[0] += ". If using custom JS Code, set allow_unsafe_js to True."
        # re-raise
        raise MarshallComponentException(*args)
        

    # now generate the response
    return generate_response(component_value, data, grid.convert_to_original_types, grid.errors)
        
