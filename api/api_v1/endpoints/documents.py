import os
import json

from fastapi import File, UploadFile, Form

from db.session import SessionLocal
from schemas import Feedback, Category, Log, Business
from models import Feedback as Model_Feedback, QuestionAnswer, Log as Model_Log
from helpers import make_categories_json, save_dataset


def endpoints(app):
    @app.post("/feedback", tags=["documents"])
    def create_feedback(feedback: Feedback):
        """
        Rate a question obtained by search
        """
        db = SessionLocal()
        row = (
            db.query(Model_Feedback)
            .where(Model_Feedback.uuid == feedback.uuid)
            .first()
        )
        if row:
            return dict(status=False, message="You have already evaluated the answer")

        try:
            fb = Model_Feedback(feedback.uuid, feedback.qualification)
            db.add(fb)
            db.commit()
        except Exception as e:
            db.rollback()
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, message="Successfully saved message")

    @app.post("/categories", tags=["documents"])
    def get_categories(category: Category):
        """
        gets all the categories of a specific dataset
        """
        category_json = os.path.join("dataset", category.business.lower() + ".json")
        if os.path.isfile(category_json):
            with open(category_json) as f:
                data = json.load(f)
            return dict(status=True, data=data)
        return dict(status=False, message="File no exists!")

    @app.post("/categories_generate", tags=["documents"])
    def generate_categories(category: Category):
        """
        generate a json file with all categories
        """
        try:
            dataset = os.path.join("dataset", category.business.lower() + ".csv")
            if not os.path.isfile(dataset):
                return dict(
                    status=False,
                    message=f"Dataset {category.business.lower()}.csv no exists!",
                )
            make_categories_json(category.business.lower(), dataset)
        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, message="Json created successfully")

    @app.post("/save_dataset", tags=["documents"])
    def dataset_save(category: Category):
        """
        saves a dataset to the database
        """
        try:
            dataset = os.path.join("dataset", category.business.lower() + ".csv")
            if not os.path.isfile(dataset):
                return dict(
                    status=False,
                    message=f"Dataset {category.business.lower()}.csv no exists!",
                )
            save_dataset(category.business.lower())
        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, message="Dataset saved successfully")

    @app.post("/get_question_answer", tags=["documents"])
    def get_question_answer(business: Business):
        """
        gets the questions and answers from the database
        """
        try:
            db = SessionLocal()
            rows = (
                db.query(QuestionAnswer)
                .filter(QuestionAnswer.business == business.business)
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
                    "created_at": row.created_at,
                }
                data.append(document)
            body = {"data": data}

        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/get_log", tags=["documents"])
    def get_log(log: Log):
        """
        gets the logs of the searches filtered by dates
        """
        try:
            db = SessionLocal()
            rows = (
                db.query(Model_Log)
                .filter(
                    Model_Log.business == log.business.lower(),
                    Model_Log.created_at.between(log.date_start, log.date_end),
                )
                .order_by(Model_Log.id)
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
                    "created_at": row.created_at,
                }
                data.append(document)
            body = {"data": data}

        except Exception as e:
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post('/load_data', tags=["documents"])
    async def load_dataset(file: UploadFile = File(...), customer_code: str = Form(...)):
        """
        Upload a dataset to the local repository
        """
        try:
            text = await file.read()
            fname = customer_code + ".csv"
            dirs = "dataset"
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            fname_path = os.path.join(os.getcwd(), os.path.join(dirs, fname))
            with open(fname_path, 'wb') as f:
                f.write(text)
            
            return {'status': True, 'message': f"Successfully loaded dataset"}, 200
        except Exception as e:
            return {'status': False, 'message': e}, 400

    return app
