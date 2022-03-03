import os
import glob
from pathlib import Path

from dotenv import load_dotenv
import jina.helper
from jina import Flow
from jina import Document, DocumentArray
from jina.importer import ImportExtensions
from jina.logging.predefined import default_logger
from jina.parsers.helloworld import set_hw_chatbot_parser
from executors.executors import MyTransformer, MyIndexer

from db.session import SessionLocal
from models import QuestionAnswer
from api.api_v1.api import endpoints


def _get_flow(args):
    """Ensure the same flow is used in hello world example and system test."""
    return (
        Flow(cors=True, protocol="http", port_expose=8000)
        .add(uses=MyTransformer, replicas=os.getenv("FLOW_EXECUTOR_REPLICAS"))
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
        import transformers, torch

        assert [torch, transformers]  #: prevent pycharm auto remove the above line

    jina.helper.extend_rest_interface = endpoints
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
                default_logger.info(f"[ {dataset} ]")
                with open(dataset) as fp:
                    f.index(
                        DocumentArray.from_csv(fp, field_resolver={"question": "text"}),
                        show_progress=True
                    )
                break
            f.block()

    if os.getenv("DATASET_SOURCE") == "DB":
        with f:
            db = SessionLocal()
            rows = db.query(QuestionAnswer).all()
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
