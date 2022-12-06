"""
Allison Day - December 2022
"""

import pandas as pd


def ReadJSON(json_data):
    """
    Makes the api json into a pandas df
    """
    line_items_df = pd.json_normalize(
        json_data,
        record_path=["documents", "line_items"],
        meta=[
            ["documents", "id"],
            ["documents", "created_date"],
            ["documents", "document_type"],
            ["documents", "img_url"],
            ["documents", "order_date"],
            ["documents", "category"],
            ["documents", "vendor", "name"],
            ["documents", "invoice_number"],
            ["documents", "tax"],
            ["documents", "total"],
        ],
        errors="ignore",
    )

    return line_items_df


# # test
# import json
# f = open(path)
# data = json.load(f)
# out = ReadJSON(data)

# out
