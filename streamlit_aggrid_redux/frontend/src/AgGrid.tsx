import { Streamlit, ComponentProps, withStreamlitConnection, } from "streamlit-component-lib"

import React, { ReactNode } from "react"

import { AgGridReact } from "@ag-grid-community/react"
import { CsvExportModule } from "@ag-grid-community/csv-export"
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model"
import { ModuleRegistry, ColumnApi, GridApi, DetailGridInfo } from "@ag-grid-community/core"

// need to move all of these enterprise modules to another package
import { MenuModule } from "@ag-grid-enterprise/menu"
import { LicenseManager } from "@ag-grid-enterprise/core"
import { SideBarModule } from "@ag-grid-enterprise/side-bar"
import { GridChartsModule } from "@ag-grid-enterprise/charts"
import { ClipboardModule } from "@ag-grid-enterprise/clipboard"
import { SetFilterModule } from "@ag-grid-enterprise/set-filter"
import { StatusBarModule } from "@ag-grid-enterprise/status-bar"
import { SparklinesModule } from "@ag-grid-enterprise/sparklines"
import { RichSelectModule } from "@ag-grid-enterprise/rich-select"
import { ExcelExportModule } from "@ag-grid-enterprise/excel-export"
import { MultiFilterModule } from "@ag-grid-enterprise/multi-filter"
import { RowGroupingModule } from "@ag-grid-enterprise/row-grouping"
import { MasterDetailModule } from "@ag-grid-enterprise/master-detail"
import { RangeSelectionModule } from "@ag-grid-enterprise/range-selection"
import { ColumnsToolPanelModule } from "@ag-grid-enterprise/column-tool-panel"
import { FiltersToolPanelModule } from "@ag-grid-enterprise/filter-tool-panel"

import { debounce, throttle } from "lodash"

// local imports
import deepMap from "./utils"

//import "./agGridStyle.scss"
import "@ag-grid-community/styles/ag-grid.min.css";
import "@ag-grid-community/styles/ag-theme-alpine.min.css";
import "@ag-grid-community/styles/ag-theme-balham.min.css";
import "@ag-grid-community/styles/ag-theme-material.min.css";
import "./ag-theme-excel.min.css"
import "./ag-theme-streamlit.min.css"

import "@astrouxds/ag-grid-theme/dist/main.css";
import "@fontsource/source-sans-pro";


type CSSDict = { [key: string]: { [key: string]: string } }

function getCSS(styles: CSSDict): string {
    var css = []
    for (let selector in styles) {
        let style = selector + " {"
        for (let prop in styles[selector]) {
            style += prop + ": " + styles[selector][prop] + ";"
        }

        style += "}"
        css.push(style)
    }
    return css.join("\n")
}

function addCustomCss(customCss: CSSDict): void {
    var css = getCSS(customCss)
    var styleSheet = document.createElement("style")
    styleSheet.type = "text/css"
    styleSheet.innerText = css
    document.head.appendChild(styleSheet)
}


function parseJsCodeFromPython(v: string) {
    const JS_PLACEHOLDER = "--x_x--0_0--"
    let funcReg = new RegExp(
        `${JS_PLACEHOLDER}\\s*((function|class)\\s*.*)\\s*${JS_PLACEHOLDER}`
    )

    let match = funcReg.exec(v)

    if (match) {
        const funcStr = match[1]
        // eslint-disable-next-line
        return new Function("return " + funcStr)()
    }
    else {
        return v
    }
}

function GridToolBar(props: any) {
    if (props.enabled) {
        return (
            <div id="gridToolBar" style={{ paddingBottom: 30 }}>
                <div className="ag-row-odd ag-row-no-focus ag-row ag-row-level-0 ag-row-position-absolute">
                    <div className="">
                        <div className="ag-cell-wrapper">{props.children}</div>
                    </div>
                </div>
            </div>
        ) 
    }
    return <></>
}

function QuickSearch(props: any) {
    if (props.enableQuickSearch) {
        return (
            <input
                className="ag-cell-value"
                type="text"
                onChange={props.onChange}
                onKeyUp={props.showOverlay}
                placeholder="quickfilter..."
                style={{ marginLeft: 5, marginRight: 5 }}
            />
        )
    }
    return <></>
}

function ManualDownloadButton(props: any) {
    if (props.enabled) {
        return (
            <button onClick={props.onClick} style={{ marginLeft: 5, marginRight: 5 }}>
                Download
            </button>
        )
    }
    return <></>
}

class AgGrid<S = {}> extends React.Component<ComponentProps, S> {
    private api!: GridApi
    private columnApi!: ColumnApi
    private gridOptions: any
    private gridContainerRef: React.RefObject<HTMLDivElement>
    private isGridAutoHeightOn: boolean
    private notYetFitColumns: boolean = true
    private renderedGridHeightPrevious: number = 0
    private preSelectAllRows: boolean = false
    private clearCheckboxOnReload: boolean = false

    constructor(props: any) {
        super(props)
        // console.log("Grid INIT called", props)

        this.gridContainerRef = React.createRef()

        ModuleRegistry.register(ClientSideRowModelModule)
        ModuleRegistry.register(CsvExportModule)

        if (props.args.custom_css) {
            addCustomCss(props.args.custom_css)
        }

        if (props.args.enable_enterprise_modules) {
            // need to find a way to lazy load these modules...
            ModuleRegistry.registerModules([
                ExcelExportModule,
                GridChartsModule,
                SparklinesModule,
                ColumnsToolPanelModule,
                FiltersToolPanelModule,
                MasterDetailModule,
                MenuModule,
                RangeSelectionModule,
                RichSelectModule,
                RowGroupingModule,
                SetFilterModule,
                MultiFilterModule,
                SideBarModule,
                StatusBarModule,
                ClipboardModule,
            ])

            if ("license_key" in props.args) {
                LicenseManager.setLicenseKey(props.args["license_key"])
            }
            else {
                console.log("Enterprise modules requested without license key; using trial version")
            }
        }

        // add some items from input grid options
        this.isGridAutoHeightOn = this.props.args.grid_options?.domLayout === "autoHeight"

        if (("clearCheckboxOnReload" in this.props.args.grid_options)) {
            this.clearCheckboxOnReload = this.props.args.grid_options["clearCheckboxOnReload"];
            delete this.props.args.grid_options["clearCheckboxOnReload"];
        }
        if (("preSelectAllRows" in this.props.args.grid_options)) {
            this.preSelectAllRows = this.props.args.grid_options["preSelectAllRows"];
            delete this.props.args.grid_options["preSelectAllRows"];
        }

        this.parseGridOptions()
    }

    private parseGridOptions() {
        let formatter = () => {
            import("./formatters").then(({ columnFormatters }) => { return columnFormatters; })
        }
        let gridOptions = Object.assign(
            {},
            formatter,
            this.props.args.grid_options
        )
        
        if (this.props.args.allow_unsafe_js) {
            console.warn("Flag allow_unsafe_js is on.")
            gridOptions = deepMap(gridOptions, parseJsCodeFromPython)
        }
        this.gridOptions = gridOptions
    }

    private attachStreamlitRerunToEvents(api: GridApi) {
        const updateEvents = this.props.args.update_on
        const doReturn = (e: any) => this.returnGridValue()
        
        // ensure that updateEvents exists before trying!
        if (updateEvents) {
            updateEvents.forEach((element: any) => {
                if (Array.isArray(element)) {
                    api.addEventListener(element[0], debounce(doReturn, element[1]))
                }
                else {
                    api.addEventListener(element, doReturn)
                }
            })
        }
    }

    private downloadAsExcelIfRequested() {
        if (this.api && this.props.args.excel_export_mode === "TRIGGER") {
            this.api.exportDataAsExcel()
        }
    }

    private clearSelectedRows() {
        if (this.api) {
            this.api.deselectAll()
        }
    }

    private resizeGridContainer() {
        const renderedGridHeight = this.gridContainerRef.current?.clientHeight
        if (renderedGridHeight && renderedGridHeight > 0 && renderedGridHeight !== this.renderedGridHeightPrevious) {
            this.renderedGridHeightPrevious = renderedGridHeight
            Streamlit.setFrameHeight(renderedGridHeight)

            // Run fitColumns() only once when it first becomes visible with height > 0
            // This should solve auto_size_mode issues with st.tabs
            if (this.notYetFitColumns) {
                this.notYetFitColumns = false
                this.fitColumns()
            }
        }
    }

    private fitColumns() {
        const columns_auto_size_mode = this.props.args.columns_auto_size_mode
        
        switch (columns_auto_size_mode) {
            case 1:
            case "FIT_ALL_COLUMNS_TO_VIEW":
                this.api.sizeColumnsToFit()
                break
            
            case 2:
            case "FIT_CONTENTS":
                this.columnApi.autoSizeAllColumns()
                break
            
            default:
                // does nothing on purpose
                break
        }
    }

    private async getGridReturnValue() {
        let returnData: any[] = []
        let returnMode = this.props.args.return_mode
        
        switch (returnMode) {
            case 0:
                // ALL_DATA
                this.api.forEachLeafNode((row: { data: any }) => returnData.push(row.data))
                break
            
            case 1:
                // FILTERED_DATA
                this.api.forEachNodeAfterFilter((row: { group: any; data: any }) => {
                    if (!row.group) {
                        returnData.push(row.data)
                    }
                })
                break
            
            case 2:
                // FILTERED_SORTED_DATA
                this.api.forEachNodeAfterFilterAndSort((row: { group: any; data: any }) => {
                    if (!row.group) {
                        returnData.push(row.data)
                    }
                })
                break
        }
        
        let returnValue = {
            rowData: returnData,
            selectedRows: this.api.getSelectedRows(),
            selectedItems: this.api.getSelectedNodes().map((n: { rowIndex: any; id: any; data: any }, i: any) => ({
                _selectedRowNodeInfo: { nodeRowIndex: n.rowIndex, nodeId: n.id },
                ...n.data,
            })),
            // uncomment the below line for debugging help; otherwise is useless
            //, colState: this.columnApi.getColumnState()
        }
        return returnValue
    }

    private returnGridValue() {
        this.getGridReturnValue().then((v: any) => Streamlit.setComponentValue(v))
    }

    private defineContainerHeight() {
        if (this.isGridAutoHeightOn) {
            return {
                width: this.props.width,
            }
        }
        else {
            return {
                width: this.props.width,
                height: this.props.args.height,
            }
        }
    }

    private getThemeClass() {
        const themeName = this.props.args.theme
        const themeBase = this.props.theme?.base
        
        var themeClass = "ag-theme-" + themeName
        
        if (themeBase === "dark" && themeName !== "material") {
            themeClass = themeClass + "-dark"
        }
        return themeClass
    }

    public componentDidUpdate(prevProps: any, prevState: S, snapshot?: any) {
        const previous_export_mode = prevProps.args.excel_export_mode
        const current_export_mode = this.props.args.excel_export_mode
    
        if (previous_export_mode !== current_export_mode && current_export_mode === "TRIGGER") {
            this.downloadAsExcelIfRequested()
        }
        
        // this forces a reload of the whole grid at each step
        if (this.props.args.reload_data && this.api) {
            this.api.setRowData(JSON.parse(this.props.args.row_data))
            // pinned top & bottom rows are passed in not via row data but as a grid option
            if (this.props.args.grid_options["pinnedTopRowData"]) {
                this.api.setPinnedTopRowData(this.props.args.grid_options["pinnedTopRowData"])
            }
            if (this.props.args.grid_options["pinnedBottomRowData"]) {
                this.api.setPinnedBottomRowData(this.props.args.grid_options["pinnedBottomRowData"])
            }
        }

        // maybe clear the selected rows
        if (this.clearCheckboxOnReload) {
            this.clearSelectedRows()
        }
    }

    private onGridReady(event: any) {
        this.api = event.api
        this.columnApi = event.columnApi
        
        this.attachStreamlitRerunToEvents(this.api)
        this.api.forEachDetailGridInfo((i: DetailGridInfo) => {
            if (i.api !== undefined) {
                this.attachStreamlitRerunToEvents(i.api)
            }
        })
        
        this.api.setRowData(JSON.parse(this.props.args.row_data))
        this.processPreselection()
    }

    private onGridSizeChanged(event: any) {
        this.resizeGridContainer()
    }

    private processPreselection() {
        // do we want to pre-select all rows?
        if (this.preSelectAllRows) {
            this.api.selectAll()
            this.returnGridValue()
        }
        else {
            // check on pre-selected rows
            if (this.props.args.grid_options["preSelectedRows"] || this.props.args.grid_options["preSelectedRows"]?.length() > 0) {
                for (var idx in this.props.args.grid_options["preSelectedRows"]) {
                    this.api.getRowNode(this.props.args.grid_options["preSelectedRows"][idx])?.setSelected(true, false, 'selectableChanged')
                    this.returnGridValue()
                }
            }
        }
    }

    public render = (): ReactNode => {
        let shouldRenderGridToolbar =
            this.props.args.enable_quick_search === true ||
            this.props.args.excel_export_mode === "MANUAL"
    
        return (
            <div
                id="gridContainer"
                className={this.getThemeClass()}
                ref={this.gridContainerRef}
                style={this.defineContainerHeight()}
            >
                <GridToolBar enabled={shouldRenderGridToolbar}>
                    <ManualDownloadButton
                        enabled={this.props.args.excel_export_mode === "MANUAL"}
                        onClick={(e: any) => this.api?.exportDataAsExcel()}
                    />
                    <QuickSearch
                        enableQuickSearch={this.props.args.enable_quick_search}
                        showOverlay={throttle(() => this.api.showLoadingOverlay(), 1000, {
                            trailing: false,
                        })}
                        onChange={debounce((e) => {
                            this.api.setQuickFilter(e.target.value)
                            this.api.hideOverlay()
                        }, 1000)}
                    />
                </GridToolBar>
                <AgGridReact
                    onGridReady={(e: any) => this.onGridReady(e)}
                    onGridSizeChanged={(e: any) => this.onGridSizeChanged(e)}
                    gridOptions={this.gridOptions}
                ></AgGridReact>
            </div>
        )
    }
}

export default withStreamlitConnection(AgGrid)