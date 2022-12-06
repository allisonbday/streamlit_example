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