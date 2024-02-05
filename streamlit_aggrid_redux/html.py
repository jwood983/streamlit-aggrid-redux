""" This module injects an HTML file with the intent of using with streamlit components module. """
from typing import Dict, Union

from types import DataElement
from grid_options_builder import GridOptionsBuilder


def default_html(needs_enterprise: bool = False) -> str:
    """ Create the default HTML string that must have the data injected. """
    import_enterprise = ''
    if needs_enterprise:
        import_enterprise = '<script src="https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.3/ag-grid-enterprise.min.js"></script>'
    return f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Include external modules -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/ag-grid/31.0.3/ag-grid-community.min.js"></script>
        {import_enterprise}
    </head>
    <body>
        <div id=[[AG_GRID_ID]] style="width=100%;height=100%" class="[[GRID_THEME]]"></div>
        <script>
// for user-specified functions (e.g., formatters, renderers)
[[USER_FUNCTIONS]]

// create the object
let gridApi;

// inject grid options dictionary here
const gridOptions = {{
    rowData: [[GRID_ROW_DATA]],
    [[GRID_OPTIONS]]
}};

// now creaete the API
gridApi = agGrid.createGrid(query.documentSelect("#[[AG_GRID_ID]]", gridOptions))
        </script>
    </body>
</html>"""

