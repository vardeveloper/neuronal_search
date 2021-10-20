import os
import csv
import json
import re
import unicodedata


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def _slugify(value):
        if not isinstance(value, str):
            value = str(value)
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf-8')
        value = _slugify_strip_re.sub('', value).strip().lower()
        return _slugify_hyphenate_re.sub('-', value)


def make_json(csvFilePath, jsonFilePath):
    data = []
    with open(csvFilePath, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)

        for rows in csvReader:
            data.append(rows)

    with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def make_json_tree(csvFilePath, jsonFilePath):
    business = {}
    category = {}
    with open(csvFilePath, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)

        for rows in csvReader:
            key_category = _slugify(rows['category'])
            if key_category in category:
                category[key_category].append(rows)
            else: 
                category[key_category] = []

            if rows['business'] in business:
                business[rows['business']] = category
            else: 
                business[rows['business']] = {}

        # new format
        list_category = []
        for k in category.keys():
            dic = {
                "name": category[k][0]['category'],
                "slug": k,
                "elements": category[k]
            }
            list_category.append(dic)
        data = dict( categories=list_category )

    with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    csvFilePath = os.path.join(".", "dataset.csv")
    jsonFilePath = os.path.join(".", "categories.json")
    make_json_tree(csvFilePath, jsonFilePath)
