####################
### TEST HELPERS ###
####################

import os
import csv
import json
import re
import unicodedata


_slugify_strip_re = re.compile(r"[^\w\s-]")
_slugify_hyphenate_re = re.compile(r"[-\s]+")


def _slugify(value):
    if not isinstance(value, str):
        value = str(value)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("utf-8")
    )
    value = _slugify_strip_re.sub("", value).strip().lower()
    return _slugify_hyphenate_re.sub("-", value)


def csv_to_json(csvFilePath, jsonFilePath):
    with open(csvFilePath, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)
        data = []
        for rows in csvReader:
            data.append(rows)
    with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def make_categories_json(business, csvFilePath):
    with open(csvFilePath, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)

        dict_category = {}
        for rows in csvReader:
            if rows["business"] == business:
                key = _slugify(rows["category"])
                if key in dict_category:
                    dict_category[key].append(rows)
                else:
                    dict_category[key] = [rows]

        list_category = []
        for k in dict_category.keys():
            dic = {
                "name": dict_category[k][0]["category"],
                "slug": k,
                "elements": dict_category[k],
            }
            list_category.append(dic)

        data = dict(categories=list_category)

    jsonFilePath = os.path.join("dataset", business.lower() + ".json")
    with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def add_row_dataset(docs):
    dataset = os.path.join(".", "dataset_test.csv")
    field_names = ['business','category','subcategory', 'question','answer']
    with open(dataset, 'a') as f:
        dictwriter = csv.DictWriter(f, fieldnames=field_names)
        for row in docs:
            dictwriter.writerow(row.tags)
        f.close()


def add_tag_html(string):
    # REGEX 
    # string = re.sub(r'^http.*', f'<a href="%s">%s</a>' % (character, character), string)

    string = re.sub(r"\s+", " ", string)
    matches = re.findall(r"http.*?\S+", string)
    for match in matches:
        string = re.sub(
            re.escape(match), f'<a href="%s" target="_blank">%s</a>' % (match, match), string
        )
    return string


if __name__ == "__main__":
    csvFilePath = os.path.join(".", "dataset.csv")
    make_categories_json("CNSC", csvFilePath)
