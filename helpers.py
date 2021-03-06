import os
import csv
import json
import re
import unicodedata

from db.session import SessionLocal
from models import QuestionAnswer, Log
from sqlalchemy import desc, func

import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS


_slugify_strip_re = re.compile(r"[^\w\s-]")
_slugify_hyphenate_re = re.compile(r"[-\s]+")

db = SessionLocal()


def _slugify(value):
    if not isinstance(value, str):
        value = str(value)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("utf-8")
    )
    value = _slugify_strip_re.sub("", value).strip().lower()
    return _slugify_hyphenate_re.sub("-", value)


def add_tag_html(string):
    matches = re.findall(r"http.*?\S+", string)
    for match in matches:
        string = re.sub(
            re.escape(match),
            f'<a href="%s" target="_blank">%s</a>' % (match, match),
            string,
        )
    return string


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

    jsonFilePath = os.path.join("dataset", business + ".json")
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


def save_dataset(business):
    dataset = os.path.join("dataset", business + ".csv")
    with open(dataset, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            try:
                qa = db.query(QuestionAnswer).filter_by(business=rows["business"], question=rows["question"]).first()
                if qa:
                    print(f'This question already exists: {qa.question}')
                    continue
                qa = QuestionAnswer(**rows)
                db.add(qa)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f'Error: {e}')


def generate_search_terms_file(business, date_start, date_end):
    dataset = os.path.join("dataset", business + "_search_terms.txt")
    with open(dataset, "w", encoding="utf-8") as f:
        try:
            search = (
                db.query(func.lower(Log.search).label('search'))
                .filter(
                    Log.business == business,
                    Log.created_at.between(date_start, date_end),
                )
                .all()
            )
            for s in search:
                f.write(s.search)
                f.write("\n")
        except Exception as e:
            print(f"Error: {e}")


def generate_wordcloud(business, limit):
    # Read the whole text.
    text_words = business + "_search_terms.txt"
    text = open(os.path.join("dataset", text_words)).read()

    # set stopwords
    nltk.download('stopwords') # download only once
    stop_words_sp = set(stopwords.words('spanish'))

    # create the wordcloud object
    wordcloud = WordCloud(stopwords=stop_words_sp, collocations=False).generate(text)

    # create a dictionary of word frequencies
    text_dictionary = wordcloud.process_text(text)

    # sort the dictionary
    word_freq = {
        k: v
        for k, v in sorted(text_dictionary.items(), reverse=True, key=lambda item: item[1])
    }

    return list(word_freq.items())[:limit]


if __name__ == "__main__":
    pass
