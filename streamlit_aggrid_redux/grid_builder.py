""" The main workhorse of the package, massages inputs to fit component needs. """
import json

from typing import List, Mapping, Union, Dict, Tuple, Literal, Iterable
from streamlit.errors import StreamlitAPIException
from streamlit.type_util import convert_anything_to_df

# local import
from .code import JsCode
from .types import DataElement
from .errors import GridBuilderError
from .grid_options_builder import GridOptionsBuilder, walk_grid_options


######################################################################
# Converter functions
######################################################################
def _make_error_msg(field: str, input: str, options: Iterable[str]):
    """ Helper function to make a cleaner error message. """
    opts = ', '.join(map(lambda x: f"'{x}'", options))
    return f"Input {field} '{input}' is invalid. Options are {opts}."


def _serialize_data(data: DataElement) -> List[Dict]:
    """ Convert the input data element into a JSON string. """
    try:
        frame = convert_anything_to_df(data, ensure_copy=True, allow_styler=False)
    except (ValueError, StreamlitAPIException):
        # reraise error
        raise GridBuilderError(f"Cannot serialize data of type '{type(data)}'")
    # fix Datetime and Timestamp columns
    for column, dtype in zip(frame.columns, frame.dtypes):
        if dtype in ("m", "M"):
            frame[column] = frame[column].astype(str)
    return json.loads(frame.to_json(orient="records", date_format="%Y/%m/%d %H:%M:%s"))


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


def _process_theme(theme: str) -> str:
    """ Ensure the theme is correct. """
    theme_opts = ("alpine", "balham", "material", "streamlit", "excel", "astro",
                  "alpine-dark", "balham-dark", "streamlit-dark", "astro-dark")
    if theme not in theme_opts:
        raise GridBuilderError(_make_error_msg("Theme", theme, theme_opts))
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


def _process_conversion_errors(convert: bool, errors: str) -> str:
    if convert and errors not in ("raise", "ignore"):
        raise GridBuilderError(
            f"Error handling '{errors}' is invalid, should be 'raise' or 'ignore'"
        )
    return errors


def _process_css(custom_css: Union[Dict, str]) -> Dict:
    """ Ensure the CSS is a python dict. """
    if custom_css is None:
        return dict()
    elif isinstance(custom_css, Dict):
        return custom_css
    elif isinstance(custom_css, str):
        return json.loads(custom_css)
    else:
        raise GridBuilderError(
            f"Custom CSS is neither a dict nor a string by {type(custom_css)}"
        )
    
def _process_update_on(updates: List[str], options: Dict) -> List[str]:
    """ Ensure that updates include columnVisible and if we have checkboxes visible. """
    # ensure at least columns being visible kicks back the data
    if updates is None:
        updates = ["columnVisible"]
    
    # if selection changed wasn't already set, see if we need to add it
    if "selectionChanged" not in updates:
        # see if checkboxSelection is set in one of the column defs
        for element in options["columnDefs"]:
            if "checkboxSelection" in element.keys():
                updates.append("selectionChanged")
                break
    
    return updates


######################################################################
# Builder Class
######################################################################
class GridBuilder:
    data: List[Dict] = [dict()]
    grid_options: Dict = None
    height: int = None
    columns_auto_size_mode: int = 0
    return_mode: int = 0
    allow_unsafe_js: bool = False
    enable_enterprise_modules: bool = True
    license_key: str = None
    convert_to_original_types: bool = True
    errors: Literal["raise", "ignore"] = "ignore"
    reload_data: bool = False
    column_state: List[Dict] = None
    theme: str = "streamlit"
    custom_css: Dict = None
    update_on: List[Union[str, Tuple[str, int]]] = None
    enable_quick_search: bool = False
    excel_export_mode: str = "none"

    def __new__(cls,
                data: DataElement,
                grid_options: Union[Dict, GridOptionsBuilder] = None,
                height: int = None,
                columns_auto_size_mode: str = "none",
                return_mode: str = "input",
                allow_unsafe_js: bool = False,
                enable_enterprise_modules: bool = True,
                license_key: str = None,
                convert_to_original_types: bool = True,
                errors: str = "ignore",
                reload_data: bool = False,
                column_state: List[Dict] = None,
                theme: str = "streamlit",
                custom_css: str = None,
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
        obj.errors = _process_conversion_errors(convert_to_original_types, errors.lower())
        obj.theme = _process_theme(theme.lower())
        obj.excel_export_mode = _process_excel_export_mode(excel_export_mode.lower())
        obj.custom_css = _process_css(custom_css)

        # remaining items do not need cleaning
        obj.height = height
        obj.allow_unsafe_js = allow_unsafe_js
        obj.enable_enterprise_modules = enable_enterprise_modules
        obj.license_key = license_key
        obj.convert_to_original_types = convert_to_original_types
        obj.reload_data = reload_data
        obj.column_state = column_state
        obj.enable_quick_search = enable_quick_search

        # handle the grid options now
        if grid_options is None:
            # if it is None, create default instance from data
            obj.grid_options = GridOptionsBuilder.from_data(data).build()
        elif isinstance(grid_options, GridOptionsBuilder):
            # if it's from the Builder, built it
            obj.grid_options = grid_options.build()
        elif isinstance(grid_options, dict):
            # otherwise we should save it
            obj.grid_options = grid_options
        elif isinstance(grid_options, str):
            # maybe they passed a string version?
            obj.grid_options = json.loads(grid_options)
        else:
            raise GridBuilderError(
                f"Unknown type for grid options: '{type(grid_options)}'"
            )
        
        # if the height is none, flag the domLayout as autoHeight
        if obj.height is None:
            obj.grid_options.update(
                **dict(
                    domLayout="autoHeight"
                )
            )

        # if any checkbox is set, ensure that selectionUpdate is added to 'update_on' param
        obj.update_on = _process_update_on(update_on, obj.grid_options)

        # now update with the embedded JS code
        walk_grid_options(
            obj.grid_options,
            lambda v: v.code if isinstance(v, JsCode) else v
        )

        return obj.process_deprecated(**kwargs)

    def process_deprecated(self, **kwargs: Mapping):
        """ In case we need to process deprecated parameters, handle them here. """
        return self

