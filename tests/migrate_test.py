import sys
sys.path.append('../seeker-jina-lucca')
import db

from sqlalchemy import desc, func, select

from models import Log

def run():
    # result = db.engine.execute("ALTER TABLE public.log ADD search TEXT")
    result = db.engine.execute(
    """
        SELECT log.question, log.answer, count(log.id) AS total 
        FROM log 
        WHERE log.business = 'BANCOPPEL' 
        AND log.question != '' 
        AND log.created_at BETWEEN '2021-11-01 00:00:00' AND '2021-11-22 23:59:59' 
        GROUP BY log.question, log.answer
        ORDER BY count(log.id)
        LIMIT 10
    """
    )
    print("Result 1: ", result)
    print()
    stmt = select(Log.question, func.count(Log.id)).\
             group_by(Log.question)
             # having(func.length(Log.question) > 4)
    result2 = db.engine.execute(stmt).fetchall()
    print("Result 2: ", result2)


if __name__ == "__main__":
    run()
