function(e) {
  let api = e.api;
  let rowIndex = e.rowIndex;
  let col = e.column.colId;

  let rowNode = api.getDisplayedRowAtIndex(rowIndex);
  api.flashCells({
    rowNodes: [rowNode],
    columns: [col],
    flashDelay: 100000000000000000000
  });

};
