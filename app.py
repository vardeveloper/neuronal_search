import os
import json

from pathlib import Path

import jina.helper
from jina import Flow, Document, DocumentArray
from jina.importer import ImportExtensions
from jina.logging.predefined import default_logger
from jina.parsers.helloworld import set_hw_chatbot_parser
from jina.types.document.generators import from_csv

from executors.executors import MyTransformer, MyIndexer

from pydantic import BaseModel
import db
from models import Feedback as Model_Feedback


class Feedback(BaseModel):
    uuid: str
    qualification: bool = False


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

    @app.get("/categories/", tags=["My Extended APIs"])
    def get_categories():
        with open(os.path.join(".", "categories.json")) as f:
            data = json.load(f)
        return dict(status=True, data=data)

    @app.post("/categories/", tags=["My Extended APIs"])
    def get_categories():
        with open(os.path.join(".", "categories.json")) as f:
            data = json.load(f)
        return dict(status=True, data=data)

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

    targets = {
        "questions-csv": {
            # 'url': args.index_data_url,
            "filename": os.path.join(args.workdir, "../dataset.csv"),
        }
    }

    jina.helper.extend_rest_interface = extend_rest_function
    f = _get_flow(args)

    # index it!
    with f, open(targets["questions-csv"]["filename"]) as fp:
        f.index(from_csv(fp, field_resolver={"question": "text"}), show_progress=True)
        f.block()


if __name__ == "__main__":
    args = set_hw_chatbot_parser().parse_args()
    run(args)
