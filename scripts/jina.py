import os
import csv
import json
import requests


URL_JINA = "https://jinadev.keos.co/index.php/index_docs/"
DIRNAME = os.path.dirname(os.path.realpath(__file__))


def make_document(business):
    dataset = os.path.join(DIRNAME, "dataset/" + business + ".csv")
    with open(dataset, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)
        data = []
        for rows in csvReader:
            document = {
                "text": rows["question"],
                "tags": {
                    "business": rows["business"],
                    "category": rows["category"],
                    "subcategory": rows["subcategory"],
                    "question": rows["question"],
                    "answer": rows["answer"],
                },
            }
            data.append(document)
        body = {"data": data, "parameters": {"business": business.upper()}}

    jsonFilePath = os.path.join(DIRNAME, "dataset/" + business + ".json")
    with open(jsonFilePath, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(body, indent=4))


def send_document(business):
    try:
        jsonFilePath = os.path.join(DIRNAME, "dataset/" + business + ".json")
        with open(jsonFilePath, encoding="utf-8") as jsonf:
            payload = json.load(jsonf)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url=URL_JINA, headers=headers, json=payload)
        print(response.json())
    except Exception as e:
        print("Error method request : {0}".format(e))


if __name__ == "__main__":
    make_document("devar")
    send_document("devar")
