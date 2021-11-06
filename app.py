import os
import json

from pathlib import Path
from dotenv import load_dotenv

import jina.helper
from jina import Flow, Document, DocumentArray
from jina.importer import ImportExtensions
from jina.logging.predefined import default_logger
from jina.parsers.helloworld import set_hw_chatbot_parser
from jina.types.document.generators import from_csv

from executors.executors import MyTransformer, MyIndexer

from pydantic import BaseModel
import db
from models import Feedback as Model_Feedback, QuestionAnswer
from helpers import make_categories_json


class Feedback(BaseModel):
    uuid: str
    qualification: bool = False


class Category(BaseModel):
    business: str


def extend_rest_function(app):
    @app.post("/feedback/", tags=["My Extended APIs"])
    def create_feedback(feedback: Feedback):
        row = (
            db.session.query(Model_Feedback)
            .where(Model_Feedback.uuid == feedback.uuid)
            .first()
        )
        if row:
            return dict(status=False, message="You have already evaluated the answer")

        try:
            fb = Model_Feedback(feedback.uuid, feedback.qualification)
            db.session.add(fb)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, message="Successfully saved message")

    @app.post("/categories/", tags=["My Extended APIs"])
    def get_categories(category: Category):
        path_filename = os.path.join("dataset", category.business.lower() + ".json")
        if os.path.isfile(path_filename):
            with open(path_filename) as f:
                data = json.load(f)
            return dict(status=True, data=data)
        return dict(status=False, message="File no exists!")

    @app.post("/categories_generate/", tags=["My Extended APIs"])
    def generate_categories(category: Category):
        try:
            csvFilePath = os.path.join(".", "dataset.csv")
            make_categories_json(category.business, csvFilePath)
        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, message="Json created successfully")

    return app


def _get_flow(args):
    """Ensure the same flow is used in hello world example and system test."""
    return (
        Flow(cors=True, protocol="http", port_expose=8000)
        .add(uses=MyTransformer, parallel=2, timeout_ready=-1)
        .add(uses=MyIndexer, workspace=args.workdir)
    )


def run(args):
    """
    Execute the chatbot example.
    :param args: arguments passed from CLI
    """
    Path(args.workdir).mkdir(parents=True, exist_ok=True)

    with ImportExtensions(
        required=True,
        help_text="this demo requires Pytorch and Transformers to be installed, "
        "if you haven't, please do `pip install jina[torch,transformers]`",
    ):
        import transformers
        import torch

        assert [torch, transformers]  #: prevent pycharm auto remove the above line

    jina.helper.extend_rest_interface = extend_rest_function
    f = _get_flow(args)
    f.expose_endpoint(
        "/index_docs",
        summary="add document in dataset",
        tags=["APIs"],
        methods=["POST"],
    )

    # index it!
    with f:
        rows = db.session.query(QuestionAnswer).all()
        f.index(
            DocumentArray(
                Document(
                    id=data,
                    text=str(data.question),
                    tags={
                        "question": str(data.question),
                        "answer": str(data.answer),
                        "business": str(data.business),
                        "category": str(data.category),
                        "subcategory": str(data.subcategory),
                    },
                )
                for data in rows
            ),
            show_progress=True,
        )
        f.block()


if __name__ == "__main__":
    load_dotenv()
    args = set_hw_chatbot_parser().parse_args()
    run(args)
