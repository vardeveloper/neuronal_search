import csv
import os

from pathlib import Path

from jina import Flow, Document, DocumentArray
from jina.importer import ImportExtensions
from jina.logging.predefined import default_logger

from jina.parsers.helloworld import set_hw_chatbot_parser

from executors.executors import MyTransformer, MyIndexer


def _get_flow(args):
    """Ensure the same flow is used in hello world example and system test."""
    return (
        Flow(
            cors=True,
            protocol='http',
            port_expose=8000
        ).add(
            uses=MyTransformer, parallel=2, timeout_ready=6000000
        ).add(
            uses=MyIndexer, workspace=args.workdir
        )
    )


def run(args):
    """
    Execute the chatbot example.
    :param args: arguments passed from CLI
    """
    Path(args.workdir).mkdir(parents=True, exist_ok=True)

    with ImportExtensions(
            required=True,
            help_text='this demo requires Pytorch and Transformers to be installed, '
                      'if you haven\'t, please do `pip install jina[torch,transformers]`',
    ):
        import transformers
        import torch

        assert [torch, transformers]  #: prevent pycharm auto remove the above line

    targets = {
        'questions-csv': {
            # 'url': args.index_data_url,
            'filename': os.path.join(args.workdir, '../dataset.csv'),
        }
    }

    f = _get_flow(args)

    # index it!
    with f, open(targets['questions-csv']['filename']) as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='\'')
        f.index(
            DocumentArray(
                Document(id=data[0], text=data[1][0], tags={'answer': str(data[1][1])}) for data in enumerate(reader)
            )
        )
        f.block()


if __name__ == '__main__':
    args = set_hw_chatbot_parser().parse_args()
    run(args)
