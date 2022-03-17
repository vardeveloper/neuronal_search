from typing import Dict

from jina import Executor, requests, DocumentArray, Flow, Document


class MyDB(Executor):
    db = DocumentArray.empty(1000)

    @requests(on='/delete')
    def foo1(self, docs: DocumentArray, parameters: Dict, **kwargs):
        # use docs.id as delete ids
        for d in docs:
            try:
                del self.db[d.id]
            except:
                print(f'try del non exist: {d.id}')

    @requests(on='/remove')
    def foo2(self, docs: DocumentArray, parameters: Dict, **kwargs):
        # use docs.id as delete ids
        for _id in parameters['delete_int_ids']:
            _id = int(_id)
            del self.db[_id]
            print(f'bye doc {_id}')

    @requests(on='/destroy_everything_we_have')
    def foo3(self, docs: DocumentArray, parameters: Dict, **kwargs):
        # use docs.id as delete ids
        self.db.clear()
        print(f'all gone!')


with Flow().add(uses=MyDB) as f:
    f.post('/delete', DocumentArray([Document(id='hello')]))
    f.post('/remove', parameters={'delete_int_ids': [1, 2, 3]})
    f.post('/destroy_everything_we_have')
