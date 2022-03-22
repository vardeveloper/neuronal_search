from sqlalchemy import desc, func
from jina.logging.predefined import default_logger

from db.session import SessionLocal
from schemas import Question_Answer
from models import Feedback as Model_Feedback, Log
from helpers import generate_search_terms_file, generate_wordcloud


def endpoints(app):
    @app.post("/report_top_question", tags=["reports"])
    def report_top_question(log: Question_Answer):
        """
        gets the most searched questions
        """
        try:
            db = SessionLocal()
            rows = (
                db.query(
                    Log.question, Log.answer, func.count(Log.id).label("total")
                )
                .filter(
                    Log.business == log.business.lower(),
                    Log.question != "",
                    Log.created_at.between(log.date_start, log.date_end),
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
                document = {"question": row[0], "answer": row[1], "total": row[2]}
                data.append(document)
            body = {"data": data}

        except Exception as e:
            default_logger.error(f"Error: {e}")
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/report_top_category", tags=["reports"])
    def report_top_category(log: Question_Answer):
        """
        gets the most searched categories
        """
        try:
            db = SessionLocal()
            rows = (
                db.query(Log.category, func.count(Log.id))
                .filter(
                    Log.business == log.business.lower(),
                    Log.question != "",
                    Log.category != "",
                    Log.created_at.between(log.date_start, log.date_end),
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
                document = {"category": row[0], "total": row[1]}
                data.append(document)
            body = {"data": data}

        except Exception as e:
            default_logger.error(f"Error: {e}")
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/report_top_feedback", tags=["reports"])
    def report_top_feedback(log: Question_Answer):
        """
        gets a list of the rated questions sorted from highest to lowest
        """
        try:
            db = SessionLocal()
            sub_query = (
                db.query(Model_Feedback.uuid)
                .filter(
                    Model_Feedback.qualification == log.qualification,
                    Log.uuid == Model_Feedback.uuid,
                )
                .label("feedback_uuid")
            )
            rows = (
                db.query(Log.question, func.count(sub_query))
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
                document = {"question": row[0], "total": row[1]}
                data.append(document)
            body = {"data": data}

        except Exception as e:
            default_logger.error(f"Error: {e}")
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=body)

    @app.post("/top_words", tags=["reports"])
    def top_words(qa: Question_Answer):
        """
        gets a list of the most repeated words
        """
        try:
            generate_search_terms_file(qa.business.lower(), qa.date_start, qa.date_end)
            top_words = generate_wordcloud(qa.business.lower(), qa.limit)
            data = []
            for word in top_words:
                w, c = word
                d = {"word": w, "cantidad": c}
                data.append(d)
        except Exception as e:
            default_logger.error(f"Error: {e}")
            return dict(status=False, message=str(e))
        else:
            return dict(status=True, data=data)

    return app
