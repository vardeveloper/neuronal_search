import sys
sys.path.append('../seeker-jina-lucca')
import db

from sqlalchemy import desc, func, select

from models import Log

def run():
    # result = db.engine.execute("ALTER TABLE public.log ADD search TEXT")
    result = db.engine.execute(
    """
        SELECT feedback.qualification AS feedback_qualification, log.question AS log_question, log.answer AS log_answer, count(feedback.id) AS total
        FROM feedback, log
        WHERE feedback.qualification = true 
        AND log.business = 'BANCOPPEL' 
        AND log.created_at BETWEEN '2021-11-01 00:00:00' AND '2021-11-30 23:59:59' 
        AND log.question is not null
        GROUP BY feedback.qualification, log.question, log.answer 
        ORDER BY count(feedback.id) DESC
        LIMIT 10
    """
    )
    print("Result 1: ", result)
    # print()
    # stmt = select(Log.question, func.count(Log.id)).\
    #          group_by(Log.question)
    #          # having(func.length(Log.question) > 4)
    # result2 = db.engine.execute(stmt).fetchall()
    # print("Result 2: ", result2)


if __name__ == "__main__":
    run()
