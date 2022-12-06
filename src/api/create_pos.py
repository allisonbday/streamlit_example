# %%
import requests
from bs4 import BeautifulSoup
import random
import json

import yaml


# %%
url = "https://imfeelingprimey.com/"
source = requests.get(url).text
soup = BeautifulSoup(source, "html.parser")

s = soup.find("main")
# content = s.find('p')


# %%
items = {}
tabs = s.find_all("li", class_="prod")
all_categories = []
all_skus = []

for i in tabs:
    # CATEGORY
    span = i.find("span", class_="prod-ranking")
    category = span.get_text() if span else "No Price"
    if category != "No Price":
        category = category.split("in ")[1]
    else:
        continue

    # IMAGE
    img = i.find("img")
    # description & text (same)
    description = img.get("title")
    # type
    type = "service" if "protection plan" in str(description).lower() else "product"
    # sku
    sku = random.randrange(111111, 999999)
    all_skus.append(sku)

    # PRICE
    span = i.find("span", class_="prod-price")
    price = span.get_text() if span else "No Price"
    if "$" in price:
        price = price.split("$")[1]
    else:
        continue

    if category not in all_categories:
        all_categories.append(category)

    if category not in items:
        items[category] = []
        print(f"added {category}")
        print(items)

    # WHY DOES THIS WORK?????
    items[category].append(
        {
            "description": description,
            "type": type,
            "sku": sku,
            "price": price,
            "text": description,
        }
    )

# random.choice(items['Amazon Devices & Accessories'])
#%%
# specific skus for specific stores. Stores are from Skyrim

stores = [
    "The Pawned Prawn",
    "The Scorched Hammer",
    "Gray Pine Goods",
    "Radiant Raiment",
    "Belethor's General Goods",
    "Birna's Oddments",
    "Bits and Pieces",
]

store_skus = {
    "The Pawned Prawn": [],
    "The Scorched Hammer": [],
    "Gray Pine Goods": [],
    "Radiant Raiment": [],
    "Belethor's General Goods": [],
    "Birna's Oddments": [],
    "Bits and Pieces": [],
}

for sku in all_skus:
    store = random.choice(stores)
    store_skus[store].append(sku)

store_skus

# %%
chosen_categories = []
for i in range(10):
    chosen_categories.append(random.choice(all_categories))
chosen_categories
#%%

all_created_dates = [
    "2022-11-06 05:58:30",
    "2022-11-14 06:49:40",
    "2022-11-04 17:29:12",
    "2022-11-25 17:30:35",
    "2022-11-22 19:03:06",
    "2022-11-22 01:20:30",
    "2022-11-21 08:27:50",
    "2022-11-18 20:33:50",
]

documents = []
id = 165815632
for date in all_created_dates:
    num_pos = random.randrange(1, 6)
    for po in range(num_pos):
        cat = random.choice(chosen_categories)
        line_items = []
        subtotal = 0
        number_lineitems = random.randrange(2, 11)
        for i in range(number_lineitems):
            item = random.choice(items[cat])
            random.choice(items.get(cat))
            quantity = random.randrange(1, 10)
            item["quantity"] = quantity
            subtotal += float(item["price"]) * quantity
            line_items.append(item)
        tax = round(subtotal * 0.061, 2)
        total = round(subtotal + tax, 2)
        vendor = random.choice(stores)

        doc = {
            "category": cat,
            "created_date": date,
            "date": date,
            "document_type": "invoice",
            "id": id,
            "img_url": "https://github.com/allisonbday/streamlit_example/blob/27dfd9e96f3651ea6660fec7f364f095dda0915f/fake_pdf.pdf",
            "invoice_number": id,
            "line_items": line_items,
            "order_date": date,
            "tax": tax,
            "total": total,
            "vendor": {"name": vendor},
        }

        documents.append(doc)
        id += 1

#%%
final = {"documents": documents}
# %%
with open("pos.json", "w") as outfile:
    json.dump(final, outfile)
# %%
# save to YAML
dataMap = {
    "categories": chosen_categories,
    "vendors": stores
}