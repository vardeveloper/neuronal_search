import os
import glob
import json

from pathlib import Path
from dotenv import load_dotenv

import jina.helper
from jina import Flow
from jina import Document, DocumentArray
# from docarray import Document, DocumentArray

from jina.importer import ImportExtensions
from jina.logging.predefined import default_logger
from jina.parsers.helloworld import set_hw_chatbot_parser
# from jina.types.document.generators import from_csv

from executors.executors import MyTransformer, MyIndexer

from sqlalchemy import desc, func
from typing import Optional
from pydantic import BaseModel
import db
from models import Feedback as Model_Feedback, QuestionAnswer, Log
from helpers import make_categories_json, save_dataset, generate_search_terms_file, generate_wordcloud


class Feedback(BaseModel):
    uuid: str
    qualification: bool = False


class Category(BaseModel):
    business: str


class Question_Answer(BaseModel):
    business: str
    date_start: str
    date_end: str
    limit: int
    qualification: Optional[bool] = True


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
        category_json = os.path.join("dataset", category.business.lower() + ".json")
        if os.path.isfile(category_json):
            with open(category_json) as f:
                data = json.load(f)
            return dict(status=True, data=data)
        return dict(status=False, message="File no exists!")

    @app.post("/categories_generate/", tags=["My Extended APIs"])
    def generate_categories(category: Category):
        try:
            dataset = os.path.join("dataset", category.business.lower() + ".csv")
            if not os.path.isfile(dataset):
                return dict(status=False, message=f"Dataset {category.business.lower()}.csv no exists!")
            make_categories_json(category.business.lower(), dataset)
        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, message="Json created successfully")

    @app.post("/save_dataset/", tags=["My Extended APIs"])
    def dataset_save(category: Category):
        try:
            dataset = os.path.join("dataset", category.business.lower() + ".csv")
            if not os.path.isfile(dataset):
                return dict(status=False, message=f"Dataset {category.business.lower()}.csv no exists!")
            save_dataset(category.business.lower())
        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, message="Dataset saved successfully")

    @app.post("/get_question_answer/", tags=["My Extended APIs"])
    def get_question_answer(qa: Question_Answer):
        try:
            rows = (
                db.session.query(QuestionAnswer)
                .filter(
                    QuestionAnswer.business == qa.business
                )
                .all()
            )
            if not rows:
                return dict(status=False, message="No hay nada")

            data = []
            for row in rows:
                document = {
                    "uuid": row.uuid,
                    "business": row.business,
                    "category": row.category,
                    "subcategory": row.subcategory,
                    "question": row.question,
                    "answer": row.answer,
                    "created_at": row.created_at
                }
                data.append(document)
            body = {"data": data}

        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/get_log/", tags=["My Extended APIs"])
    def get_log(log: Question_Answer):
        try:
            rows = (
                db.session.query(Log)
                .filter(
                    Log.business == log.business.lower(),
                    Log.created_at.between(log.date_start, log.date_end)
                )
                .order_by(Log.id)
                .all()
            )
            if not rows:
                return dict(status=False, message="No hay nada")

            data = []
            for row in rows:
                document = {
                    "uuid": row.uuid,
                    "business": row.business,
                    "category": row.category,
                    "search": row.search,
                    "question": row.question,
                    "answer": row.answer,
                    "created_at": row.created_at
                }
                data.append(document)
            body = {"data": data}

        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/report_top_question/", tags=["My Extended APIs"])
    def report_top_question(log: Question_Answer):
        try:
            rows = (
                db.session.query(Log.question, Log.answer, func.count(Log.id).label('total'))
                .filter(
                    Log.business == log.business.lower(),
                    Log.question != "",
                    Log.created_at.between(log.date_start, log.date_end)
                )
                .group_by(Log.question, Log.answer)
                # .having(func.count(Log.question) > 10)
                .order_by(desc(func.count(Log.id)))
                .limit(log.limit)
                .all()
            )
            if not rows:
                return dict(status=False, message="No hay nada")

            data = []
            for row in rows:
                document = {
                    "question": row[0],
                    "answer": row[1],
                    "total": row[2]
                }
                data.append(document)
            body = {"data": data}

        except Exception as e:
            default_logger.error(f'Error: {e}')
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/report_top_category/", tags=["My Extended APIs"])
    def report_top_category(log: Question_Answer):
        try:
            rows = (
                db.session.query(Log.category, func.count(Log.id))
                .filter(
                    Log.business == log.business.lower(),
                    Log.question != "",
                    Log.category != "",
                    Log.created_at.between(log.date_start, log.date_end)
                )
                .group_by(Log.category)
                .order_by(desc(func.count(Log.id)))
                .limit(log.limit)
                .all()
            )
            if not rows:
                return dict(status=False, message="No hay nada")

            data = []
            for row in rows:
                document = {
                    "category": row[0],
                    "total": row[1]
                }
                data.append(document)
            body = {"data": data}

        except Exception as e:
            default_logger.error(f'Error: {e}')
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/report_top_feedback/", tags=["My Extended APIs"])
    def report_top_feedback(log: Question_Answer):
        try:
            sub_query = (
                db.session.query(Model_Feedback.uuid)
                .filter(
                    Model_Feedback.qualification == log.qualification,
                    Log.uuid == Model_Feedback.uuid,
                )
                .label("feedback_uuid")
            )
            rows = (
                db.session.query(
                    Log.question,
                    func.count(sub_query)
                )
                .filter(
                    Log.business == log.business.lower(),
                    Log.created_at.between(log.date_start, log.date_end),
                )
                .group_by(Log.question)
                .order_by(desc(func.count(sub_query)))
                .limit(log.limit)
                .all()
            )

            if not rows:
                return dict(status=False, message="No hay nada")

            data = []
            for row in rows:
                document = {
                    "question": row[0],
                    "total": row[1]
                }
                data.append(document)
            body = {"data": data}

        except Exception as e:
            default_logger.error(f'Error: {e}')
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/top_words/", tags=["My Extended APIs"])
    def top_words(qa: Question_Answer):
        try:
            generate_search_terms_file(qa.business.lower(), qa.date_start, qa.date_end)
            top_words = generate_wordcloud(qa.business.lower(), qa.limit)
            data = []
            for word in top_words:
                w, c = word
                d = {
                    "word": w,
                    "cantidad": c
                }
                data.append(d)
        except Exception as e:
            default_logger.error(f'Error: {e}')
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=data)

    return app


def _get_flow(args):
    """Ensure the same flow is used in hello world example and system test."""
    return (
        Flow(cors=True, protocol="http", port_expose=8000)
        .add(uses=MyTransformer, replicas=os.getenv("FLOW_EXECUTOR_REPLICAS"), timeout_ready=-1)
        .add(uses=MyIndexer, workspace=args.workdir)
        .plot('flow.svg')
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

    if os.getenv("DATASET_SOURCE") == "CSV":
        with f:
            for dataset in glob.iglob(os.path.join("dataset", "*.csv")):
                default_logger.info(f'[ {dataset} ]')
                with open(dataset) as fp:
                    f.index(
                        DocumentArray.from_csv(fp, field_resolver={"question": "text"}),
                        show_progress=True
                    )
            f.block()

    if os.getenv("DATASET_SOURCE") == "DB":
        with f:
            rows = db.session.query(QuestionAnswer).all()
            f.index(
                DocumentArray(
                    Document(
                        id=data,
                        text=data.question,
                        tags={
                            "question": data.question,
                            "answer": data.answer,
                            "business": data.business,
                            "category": data.category,
                            "subcategory": data.subcategory
                        }
                    )
                    for data in rows
                ),
                show_progress=True
            )
            f.block()


if __name__ == "__main__":
    load_dotenv()
    args = set_hw_chatbot_parser().parse_args()
    run(args)
