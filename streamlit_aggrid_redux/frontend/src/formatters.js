import { duration } from "moment"
import { format } from "date-fns-tz"
import { parseISO, compareAsc } from "date-fns"

// some formatting functions
function dateFormatter(isoString, formatterString) {
    try {
        let date = parseISO(isoString)
        return format(date, formatterString)
    }
    catch {
        return isoString
    }
    finally {
      // does nothing on purpose
    }
}

function currencyFormatter(number, currencySymbol) {
    let n = Number.parseFloat(number)
    if (!Number.isNaN(n)) {
        return currencySymbol + n.toFixed(2)
    }
    else {
        return number
    }
}

function numberFormatter(number, precision) {
    let n = Number.parseFloat(number)
    if (!Number.isNaN(n)) {
        return n.toFixed(precision)
    }
    else {
        return number
    }
}

const columnFormatters = {
    columnTypes: {
        dateColumnFilter: {
            filter: "agDateColumnFilter",
            filterParams: {
                comparator: (filterValue, cellValue) => 
                    compareAsc(parseISO(cellValue), filterValue),
            },
        },
        numberColumnFilter: {
            filter: "agNumberColumnFilter",
        },
        shortDateTimeFormat: {
            valueFormatter: (params) =>
                dateFormatter(params.value, "dd/MM/yyyy HH:mm"),
        },
        customDateTimeFormat: {
            valueFormatter: (params) =>
                dateFormatter(params.value, params.column.colDef.custom_format_string),
        },
        customNumericFormat: {
            valueFormatter: (params) =>
                numberFormatter(params.value, params.column.colDef.precision ?? 2),
        },
        customCurrencyFormat: {
            valueFormatter: (params) =>
                currencyFormatter(params.value, params.column.colDef.custom_currency_symbol),
        },
        timedeltaFormat: {
            valueFormatter: (params) => duration(params.value).humanize(true),
        },
    },
}

export { columnFormatters };