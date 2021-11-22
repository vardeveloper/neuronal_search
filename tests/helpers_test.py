####################
### TEST HELPERS ###
####################

import os
import csv
import json
import re
import unicodedata


import sys
sys.path.append('../seeker-jina-lucca')
import db
from models import QuestionAnswer


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


def add_row_dataset(docs, business):
    dataset = os.path.join("dataset", business + ".csv")
    if os.path.isfile(dataset):
        field_names = ["business", "category", "subcategory", "question", "answer"]
        with open(dataset, "a") as f:
            dictwriter = csv.DictWriter(f, fieldnames=field_names)
            for row in docs:
                dictwriter.writerow(row.tags)
            f.close()


def add_tag_html(string):
    # string = re.sub(r'^http.*', f'<a href="%s">%s</a>' % (character, character), string) # REGEX 
    # string = re.sub(r"\s+", " ", string) # remove white space

    matches = re.findall(r"http.*?\S+", string)
    for match in matches:
        string = re.sub(
            re.escape(match), f'<a href="%s" target="_blank">%s</a>' % (match, match), string
        )
    return string


def save_dataset(business):
    dataset = os.path.join("dataset", business + ".csv")
    with open(dataset, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            try:
                qa = db.session.query(QuestionAnswer).filter_by(business=rows["business"], question=rows["question"]).first()
                if qa:
                    print(f'This question already exists: {qa.question}')
                    continue
                qa = QuestionAnswer(**rows)
                db.session.add(qa)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f'Error: {e}')


def create_dataset_test(business, num_iterations):
    dataset = os.path.join("dataset", business + ".csv")
    with open(dataset, "w", encoding="utf-8") as f:
        field_names = ["business", "category", "subcategory", "question", "answer"]        
        dictwriter = csv.DictWriter(f, fieldnames=field_names)
        dictwriter.writeheader()
        for _ in range(num_iterations):
            data = {
                "business": "DEVAR",
                "category": "TI",
                "subcategory": "KEOS",
                "question": "What is Neural Search?",
                "answer": "The core idea of neural search is to leverage state-of-the-art deep neural networks to build every component of a search system. In short, neural search is deep neural network-powered information retrieval. In academia, it\u2019s often called neural IR."
            }
            dictwriter.writerow(data)
        f.close()


def date_development():
    import datetime
    from dateutil import tz
    time_zone = tz.gettz("America/Lima")
    now1 = datetime.datetime.now(tz=time_zone)
    now2 = now1.strftime("%Y-%m-%d %H:%M:%S")
    now3 = datetime.datetime.utcnow
    now4 = datetime.datetime.now
    date = [now1, now2, now3, now4]
    return date

if __name__ == "__main__":
    create_dataset_test("test_5000", 5000)
    # print(date_development())
