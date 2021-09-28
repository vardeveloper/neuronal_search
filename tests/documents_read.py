import csv
import os

from pathlib import Path

from jina.parsers.helloworld import set_hw_chatbot_parser



def run(args):
    print(args)
    targets = {
        'questions-csv': {
            # 'url': args.index_data_url,
            'filename': os.path.join('../demo-search', 'dataset.csv'),
        }
    }

    print(os.path.join('../demo-search', 'dataset.csv'))

    with open(targets['questions-csv']['filename']) as fp:
        reader = csv.reader(fp, delimiter=';', quotechar='\'')

        for data in enumerate(reader):
            print("ID: ", data[0] )
            print("text: ", data[1][0])
            print("answer: ", data[1][1])
            print("business: ", data[1][2])
            print("category: ", data[1][3])
        # gene = from_csv(fp, field_resolver={'question': 'text'})
        # for i in gene:
        #     print(i)
        # result = [x for x in gene]
        # print(result)

if __name__ == '__main__':
    args = set_hw_chatbot_parser().parse_args()
    run(args)