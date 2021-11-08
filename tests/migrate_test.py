import sys
sys.path.append('../seeker-jina-lucca')
import db


def run():
    result = db.engine.execute("ALTER TABLE public.log ADD search TEXT")
    print(result)


if __name__ == "__main__":
    run()
