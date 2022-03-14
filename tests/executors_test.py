import os
import sys
sys.path.append('../prototype-jina')

from jina import Executor, requests, DocumentArray, Document
from jina.types.document.generators import from_csv

import db
from helpers_test import add_row_dataset
from models import QuestionAnswer


class MyExec(Executor):
    @requests
    def index(self, docs: "DocumentArray", **kwargs):
        print("SPLIT")
        rv = docs.split(tag="business")
        print(rv['CNSC'])
        print()

        print("FILTER")
        docs_business = DocumentArray()
        for d in filter(lambda d: d.tags["business"] == 'CNSC', docs):
            docs_business.append(d)
        print(docs_business)
        print()

    @requests
    def foo(self, docs, **kwargs):
        # for d in docs:
        #     d.text = "hello world"
        add_row_dataset(docs, 'CNSC')
        print()


def run():
    m = MyExec()
    da = DocumentArray(
        [
            Document(
                text="What is Neural Search?",
                tags={
                    "question": "What is Neural Search?",
                    "answer": "The core idea of neural search is to leverage state-of-the-art deep neural networks to build every component of a search system. In short, neural search is deep neural network-powered information retrieval. In academia, it’s often called neural IR.",
                    "business": "DEVAR",
                    "category": "TI",
                    "subcategory": "KEOS",
                }
            ),
            Document(
                text="What is Jina?",
                tags={
                    "question": "What is Jina?",
                    "answer": "Jina🔊 is a neural search framework that empowers anyone to build SOTA and scalable deep learning search applications in minutes.",
                    "business": "VARDEL",
                    "category": "TI",
                    "subcategory": "KEOS",
                }
            )
        ]
    )
    print(da)
    m.foo(da)


if __name__ == "__main__":
    run()

    # m = MyExec()
    # filename = os.path.join("dataset", "cnsc.csv")
    # with open(filename) as fp:
    #     da = DocumentArray(from_csv(fp, field_resolver={"question": "text"}))
    # m.index(da)
