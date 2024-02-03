""" This module injects an HTML file with the intent of using with streamlit components module. """


def html() -> str:
    """ Create the HTML string. """
    return """

<html>
    <head>
        <
    </head>
    <body>
        <div id=[[AG_GRID_ID]] style="width=100%;height=100%" class="ag-quartz"></div>
        <script>
// create the object
let gridApi;

// inject grid options dictionary here
const gridOptions = {
[[GRID_OPTIONS]]
}

// now creaete the API
gridApi = agGrid.createGrid(query.documentSelect("#[[AG_GRID_ID]]", gridOptions))
        </script>
    </body>
</html>
    """