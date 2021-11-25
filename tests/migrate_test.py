import sys

sys.path.append("../seeker-jina-lucca")
import db

from sqlalchemy import desc, func, select

from models import Log, Feedback


def get_query_a():
    sub_query = (
        db.session.query(Feedback.uuid)
        .filter(
            Feedback.qualification == True,
            Log.uuid == Feedback.uuid,
        )
        .label("count")
    )
    rows = (
        db.session.query(Log.question, func.count(sub_query))
        .filter(
            Log.business == "bancoppel",
            Log.created_at.between("2021-11-01 00:00:00", "2021-11-30 23:59:59"),
        )
        .group_by(Log.question)
        .order_by(desc(func.count(sub_query)))
        .limit(10)
        .all()
    )
    return rows


def get_query_b():
    # result = db.engine.execute("ALTER TABLE public.log ADD search TEXT")
    result = db.engine.execute(
        """
        SELECT DISTINCT feedback.uuid, feedback.qualification, log.question, log.answer, count(feedback.id) AS total
        FROM feedback, log
        WHERE feedback.qualification = true 
        AND log.business = 'bancoppel' 
        AND log.created_at BETWEEN '2021-11-01 00:00:00' AND '2021-11-30 23:59:59' 
        AND log.question is not null
        GROUP BY feedback.uuid, feedback.qualification, log.question, log.answer 
        ORDER BY count(feedback.id) DESC
        LIMIT 10
    """
    )
    return result


def get_query_c():
    stmt = (
        select(Log.question, func.count(Log.id))
        .group_by(Log.question)
        .having(func.length(Log.question) > 4)
    )
    result = db.engine.execute(stmt).fetchall()
    return result


def run():
    result = db.engine.execute("ALTER TABLE public.log ADD search TEXT")


if __name__ == "__main__":
    print()
    print([x for x in get_query_a()])
