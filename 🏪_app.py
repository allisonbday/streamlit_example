# IMPORTS ---------------------------------------------------------------------
import pandas as pd
import json
import yaml
import re

# streamlit
import streamlit as st
from annotated_text import annotated_text

# aggrid
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid import GridUpdateMode, DataReturnMode

# YAML ------------------------------------------------------------------------
POs_yml = r"name.yml"
with open(POs_yml, "r") as file:
    dataMap = yaml.safe_load(file)

categories = dataMap["categories"]
vendors = dataMap["vendors"]
doc_types = ["invoice", "receipt"]

# FUNCTIONS -------------------------------------------------------------------


@st.cache
def get_and_clean_api():
    from read_pos import ReadJSON

    path = r"pos.json"
    f = open(path)
    data = json.load(f)
    out = ReadJSON(data)

    return out


@st.cache
def wrangle_documents(api_data):
    doc_columns = [col for col in api_data.columns if "documents." in col]
    docs_df = (
        api_data[doc_columns]
        .drop_duplicates()
        .sort_values(by=["documents.created_date"], ascending=False)
    )
    docs_df = docs_df[
        [
            "documents.id",
            "documents.created_date",
            "documents.vendor.name",
            "documents.category",
            "documents.invoice_number",
            "documents.tax",
            "documents.total",
            "documents.document_type",
            "documents.order_date",
            "documents.img_url",
        ]
    ]  # todo: don't hardcode this

    return docs_df


def wrangle_lineitems(api_data, selected_po_id):
    item_columns = [col for col in api_data.columns if "documents." not in col]
    item_columns += ["documents.id", "documents.vendor.name"]
    items_df = api_data[api_data["documents.id"] == selected_po_id][item_columns]

    return items_df


# PULL JSON FUNCTIONS ---------------------------------------------------------

# numcheck - https://www.ag-grid.com/javascript-data-grid/cell-editors/#example-rich-cell-editor--dynamic-parameters
numcheck = """class NumericEditor {
    // gets called once before the renderer is used
    init(params) {
        // create the cell
        this.eInput = document.createElement('input');

        if (this.isCharNumeric(params.charPress)) {
            this.eInput.value = params.charPress;
        } else {
            if (params.value !== undefined && params.value !== null) {
                this.eInput.value = params.value;
            }
        }

        this.eInput.addEventListener('keypress', (event) => {
            if (!this.isKeyPressedNumeric(event)) {
                this.eInput.focus();
                if (event.preventDefault) event.preventDefault();
            } else if (this.isKeyPressedNavigation(event)) {
                event.stopPropagation();
            }
        });

        // only start edit if key pressed is a number, not a letter
        const charPressIsNotANumber =
            params.charPress && '1234567890'.indexOf(params.charPress) < 0;
        this.cancelBeforeStart = !!charPressIsNotANumber;
    }

    isKeyPressedNavigation(event) {
        return event.key === 'ArrowLeft' || event.key === 'ArrowRight';
    }

    // gets called once when grid ready to insert the element
    getGui() {
        return this.eInput;
    }

    // focus and select can be done after the gui is attached
    afterGuiAttached() {
        this.eInput.focus();
    }

    // returns the new value after editing
    isCancelBeforeStart() {
        return this.cancelBeforeStart;
    }

    // returns the new value after editing
    getValue() {
        return parseFloat(this.eInput.value).toFixed(2);
    }

    // any cleanup we need to be done here
    destroy() {
        // but this example is simple, no cleanup, we could  even leave this method out as it's optional
    }

    // if true, then this editor will appear in a popup
    isPopup() {
        // and we could leave this method out also, false is the default
        return false;
    }

    isCharNumeric(charStr) {
        return charStr && !!/(\d|.)/.test(charStr);
    }

    isKeyPressedNumeric(event) {
        const charStr = event.key;
        return this.isCharNumeric(charStr);
    }
}"""
numcheck_jscode = JsCode(numcheck)

# edit color
edit_color = """function(e) {
  let api = e.api;
  let rowIndex = e.rowIndex;
  let col = e.column.colId;

  let rowNode = api.getDisplayedRowAtIndex(rowIndex);
  api.flashCells({
    rowNodes: [rowNode],
    columns: [col],
    flashDelay: 100000000000000000000
  });

};"""
edit_color_jscode = JsCode(edit_color)

# PAGE SET UP -----------------------------------------------------------------
st.set_page_config(page_icon="🏪", page_title="PO dashboard", layout="wide")
st.image(
    "https://emojipedia-us.s3.amazonaws.com/source/microsoft-teams/337/convenience-store_1f3ea.png",
    width=100,
)
st.title("Product Order Dashboard")

###############################################################################

# Imputs expander

with st.expander("**API Inputs**", expanded=False):

    pull_since = st.date_input(
        "Pull Since"
    )  # change sesion state to new date on change?

    annotated_text(
        "New API pull url = ",
        "{enviornmental_url}api/documents/?created__gte=",
        (f"{pull_since}", "date input", "#8ef"),
    )
    st.info(
        """
        Since this example file is pulling from a json file, this date selector doesn't do anything. 
        But when it is hooked up to an API, it gets added as a variable in the url.
        """,
        icon="ℹ️",
    )

api_data = get_and_clean_api()

# DOCUMENT
st.header("Select Document")

docs_df = wrangle_documents(api_data)
# Aggrid
gb = GridOptionsBuilder.from_dataframe(docs_df)
gb.configure_selection(selection_mode="false", use_checkbox=True, pre_selected_rows=[0])
# doc type
gb.configure_column(
    "documents.document_type",
    editable=True,
    cellEditor="agRichSelectCellEditor",
    cellEditorParams={"values": doc_types},
    cellEditorPopup=True,
)
# doc category
gb.configure_column(
    "documents.category",
    editable=True,
    cellEditor="agRichSelectCellEditor",
    cellEditorParams={"values": categories},
    cellEditorPopup=True,
)

# doc tax
gb.configure_column(
    "documents.tax",
    editable=True,
    cellEditor=numcheck_jscode,
    cellEditorPopup=True,
    valueFormatter="'$' + x.toLocaleString()",
)
# doc total
gb.configure_column(
    "documents.total",
    editable=True,
    cellEditor=numcheck_jscode,
    cellEditorPopup=True,
    valueFormatter="'$' + x.toLocaleString()",
)
# doc invoice_number
gb.configure_column(
    "documents.invoice_number",
    editable=True,
    cellEditor="agTextCellEditor",
    cellEditorPopup=True,
)
# doc vendor
gb.configure_column(
    "documents.vendor.name",
    editable=True,
    cellEditor="agRichSelectCellEditor",
    cellEditorParams={"values": vendors},
    cellEditorPopup=True,
)

# doc order_date
gb.configure_column(
    # todo: https://ag-grid.com/javascript-data-grid/cell-editors/#datepicker-cell-editing-example
    "documents.order_date",
    editable=True,
    type=["dateColumnFilter", "customDateTimeFormat"],
    custom_format_string="yyyy-MM-dd",
)  # todo: when you edit, save the info in same yyyy-mm-dd format (currently only saves edit)


gb.configure_grid_options(
    enableRangeSelection=True, onCellValueChanged=edit_color_jscode
)
gridOptions = gb.build()

docs_grid = AgGrid(
    docs_df,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True,
    reload_data=False,
)


# EDIT LINE ITEMS
selected_po_id = docs_grid["selected_rows"][0]["documents.id"]
selected_vendor = docs_grid["selected_rows"][0]["documents.vendor.name"]
st.subheader(f"***{selected_vendor}*** Line Items")

with st.expander("PO URL", expanded=False):
    # eventually pull url every time doc is changed
    st.write(docs_grid["selected_rows"][0]["documents.img_url"])

items_df = wrangle_lineitems(api_data, selected_po_id)

# columns that need IN LINE EDITS
# ! category - multiselect
gb_items = GridOptionsBuilder.from_dataframe(
    items_df[
        [
            "description",
            # "documents.vendor.name",
            "type",
            "sku",
            "quantity",
            "price",
            "text",
        ]
    ]
)

# item description
gb_items.configure_column(
    "description",
    editable=True,
    cellEditor="agLargeTextCellEditor",  # change to integer
    cellEditorPopup=True,
)

# item quantity
gb_items.configure_column(
    "quantity",
    editable=True,
    cellEditor=numcheck_jscode,  # change to integer
    cellEditorPopup=True,
)
# item price
gb_items.configure_column(
    "price",
    editable=True,
    cellEditor=numcheck_jscode,
    cellEditorPopup=True,
    valueFormatter="'$' + x.toLocaleString()",
)


# ADD AND DELETE https://discuss.streamlit.io/t/ag-grid-component-with-input-support/8108/333
string_to_add_row = "\n\n function(e) { \n \
let api = e.api; \n \
let rowIndex = e.rowIndex + 1; \n \
api.applyTransaction({addIndex: rowIndex, add: [{}]}); \n \
    }; \n \n"

string_to_delete = "\n\n function(e) { \n \
let api = e.api; \n \
 let sel = api.getSelectedRows(); \n \
api.applyTransaction({remove: sel}); \n \
    }; \n \n"


cell_button_add = JsCode(
    """
    class BtnAddCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
             <span>
                <style>
                .btn_add {
                  background-color: limegreen;
                  border: none;
                  color: white;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 10px;
                  font-weight: bold;
                  height: 2.5em;
                  width: 8em;
                  cursor: pointer;
                }

                .btn_add :hover {
                  background-color: #05d588;
                }
                </style>
                <button id='click-button' 
                    class="btn_add" 
                    >&CirclePlus; Add</button>
             </span>
          `;
        }

        getGui() {
            return this.eGui;
        }

    };
    """
)

# todo: make this an event and add popup to stop accidental deletions
cell_button_delete = JsCode(
    """
    class BtnCellRenderer {
        init(params) {
            console.log(params.api.getSelectedRows());
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
             <span>
                <style>
                .btn {
                  background-color: #F94721;
                  border: none;
                  color: white;
                  font-size: 10px;
                  font-weight: bold;
                  height: 2.5em;
                  width: 8em;
                  cursor: pointer;
                }

                .btn:hover {
                  background-color: #FB6747;
                }
                </style>
                <button id='click-button'
                    class="btn"
                    >&#128465; Delete</button>
             </span>
          `;
        }

        getGui() {
            return this.eGui;
        }

    };
    """
)

gb_items.configure_column(
    "Delete",
    headerTooltip="Click on Button to remove row",
    editable=False,
    filter=False,
    onCellClicked=JsCode(string_to_delete),
    cellRenderer=cell_button_delete,
    autoHeight=True,
    suppressMovable="true",
)

gb_items.configure_column(
    "",
    headerTooltip="Click on Button to add new row",
    editable=False,
    filter=False,
    onCellClicked=JsCode(string_to_add_row),
    cellRenderer=cell_button_add,
    autoHeight=True,
    wrapText=True,
    lockPosition="left",
    checkboxSelection=True,
    selection_mode="multiple",
)

gb_items.configure_default_column(editable=True)
gb_items.configure_grid_options(
    enableRangeSelection=True, onCellValueChanged=edit_color_jscode
)
gridOptions_items = gb_items.build()

items_grid = AgGrid(
    items_df,
    gridOptions=gridOptions_items,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.AS_INPUT,
    enable_enterprise_modules=True,
    # highlight
    # key="lineitems_grid",
    allow_unsafe_jscode=True,
    reload_data=False,
)


if st.button("ready to return?"):
    selected_docs = docs_grid["selected_rows"]
    end_items = items_grid["data"].drop(
        ["documents.id", "documents.vendor.name"], axis=1
    )
    for i in selected_docs:
        for key in i.keys():
            new_key = re.sub("documents.", "", key)
            i[new_key] = i.pop(key)
        i["line_items"] = end_items.to_dict("records")
        i["vendor"] = {"name": i.pop("vendor.name")}

    st.subheader("Returnable Format")
    st.info(
        """
    We went through all this effort to edit and correct the POs, so we want to save our work.
    To do that we need to return it"""
    )
    st.write(selected_docs[0])
    st.balloons()
