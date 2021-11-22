import sys
sys.path.append('../seeker-jina-lucca')
import db


def run():
    # result = db.engine.execute("ALTER TABLE public.log ADD search TEXT")
    result = db.engine.execute(
    """
        SELECT log.id AS log_id, log.uuid AS log_uuid, log.search AS log_search, log.question AS log_question, log.answer AS log_answer, log.business AS log_business, log.category AS log_category, log.flow_id AS log_flow_id, log.session_id AS log_session_id, log.created_at AS log_created_at, count(log.question) AS count_1 
        FROM log 
        WHERE log.business = 'BANCOPPEL' 
        AND log.question != '' 
        AND log.created_at BETWEEN '2021-11-01 00:00:00' AND '2021-11-22 23:59:59' 
        GROUP BY log.question 
        LIMIT 10
    """
    )

    print(result)


if __name__ == "__main__":
    run()
