import os
from typing import Dict, Tuple
from uuid import uuid4

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

from jina import Executor, requests
from docarray import Document, DocumentArray
from jina.logging.predefined import default_logger

import db
from models import Log, QuestionAnswer
from helpers import add_tag_html, add_row_dataset

from dotenv import load_dotenv
load_dotenv()

class MyTransformer(Executor):
    """Transformer executor class """

    def __init__(
        self,
        pretrained_model_name_or_path: str = "sentence-transformers/multi-qa-mpnet-base-cos-v1",
        pooling_strategy: str = "mean",
        layer_index: int = -1,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.pooling_strategy = pooling_strategy
        self.layer_index = layer_index
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.pretrained_model_name_or_path
        )
        self.model = AutoModel.from_pretrained(
            self.pretrained_model_name_or_path, output_hidden_states=True
        )
        self.model.to(torch.device('cpu'))

    def _compute_embedding(self, hidden_states: 'torch.Tensor', input_tokens: Dict):

        fill_vals = {'cls': 0.0, 'mean': 0.0, 'max': -np.inf, 'min': np.inf}
        fill_val = torch.tensor(
            fill_vals[self.pooling_strategy], device=torch.device('cpu')
        )

        layer = hidden_states[self.layer_index]
        attn_mask = input_tokens['attention_mask'].unsqueeze(-1).expand_as(layer)
        layer = torch.where(attn_mask.bool(), layer, fill_val)

        embeddings = layer.sum(dim=1) / attn_mask.sum(dim=1)
        return embeddings.cpu().numpy()

    @requests
    def encode(self, docs: 'DocumentArray', **kwargs):
        with torch.inference_mode():
            if not self.tokenizer.pad_token:
                self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                self.model.resize_token_embeddings(len(self.tokenizer.vocab))

            input_tokens = self.tokenizer(
                docs[:, 'content'],
                padding='longest',
                truncation=True,
                return_tensors='pt',
            )
            input_tokens = {
                k: v.to(torch.device('cpu')) for k, v in input_tokens.items()
            }

            outputs = self.model(**input_tokens)
            hidden_states = outputs.hidden_states

            docs.embeddings = self._compute_embedding(hidden_states, input_tokens)


class MyIndexer(Executor):
    """Simple indexer class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if os.path.exists(self.workspace + '/indexer'):
            self._docs = DocumentArray.load(self.workspace + '/indexer')
        else:
            self._docs = DocumentArray()

    @requests(on="/index")
    def index(self, docs: "DocumentArray", **kwargs):
        self._docs.extend(docs)

    @requests(on="/index_docs")
    def index_docs(self, docs: "DocumentArray", parameters, **kwargs):
        self._docs.extend(docs)

        if "business" in parameters:
            add_row_dataset(docs, parameters["business"].strip().lower())

        for doc in docs:
            try:
                qa = db.session.query(QuestionAnswer).filter_by(business=doc.tags["business"], question=doc.text).first()
                if qa:
                    default_logger.error(f'This question already exists: {qa.question}')
                    continue
                qa = QuestionAnswer(**doc.tags)
                db.session.add(qa)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                default_logger.error(f'Error: {e}')

    @requests(on="/search")
    def search(self, docs: "DocumentArray", parameters, **kwargs):
        message_uuid = str(uuid4())

        if "business" in parameters:
            docs_business = DocumentArray()
            for d in filter(lambda d: d.tags["business"].strip().lower() == parameters["business"].strip().lower(), self._docs):
                docs_business.append(d)

            if docs_business:
                docs_filter = docs_business

                if "category" in parameters:
                    docs_category = DocumentArray()
                    for d in filter(lambda d: d.tags["category"].strip().lower() == parameters["category"].strip().lower(), docs_business):
                        docs_category.append(d)

                    if docs_category:
                        docs_filter = docs_category


                docs.match(
                    docs_filter,
                    metric='cosine',
                    normalization=(1, 0),
                    limit=1,
                )


                # a = np.stack(docs.get_attributes("embedding"))
                # b = np.stack(docs_filter.get_attributes("embedding"))
                # q_emb = _ext_A(_norm(a))
                # d_emb = _ext_B(_norm(b))
                # dists = _cosine(q_emb, d_emb)
                # idx, dist = self._get_sorted_top_k(dists, 3)
                # for _q, _ids, _dists in zip(docs, idx, dist):
                #     for _id, _dist in zip(_ids, _dists):
                #         if 1 - _dist > 0.4:
                #             d = Document(docs_filter[int(_id)], copy=True)
                #             d.scores["cosine"] = 1 - _dist
                #             d.tags["uuid"] = message_uuid
                #             d.tags["question"] = d.text
                #             d.tags["answer_html"] = d.tags["answer"].replace("\n", "<br>")
                #             d.pop("embedding")
                #             _q.matches.append(d)

        # Log
        try:
            question = ""
            answer = ""
            business = parameters.get("business", '').strip().lower()
            category = parameters.get("category", '').strip().lower()
            flow_id = parameters.get("flow_id", 0)
            session_id = parameters.get("session_id", 0)

            if docs.get_attributes("matches")[0]:
                matches = docs.get_attributes("matches")[0][0]
                question = matches.tags["question"]
                answer = matches.tags["answer"]

            data = {
                "uuid": message_uuid,
                "search": docs.get_attributes("text")[0],
                "question": question,
                "answer": answer,
                "business": business,
                "category": category,
                "flow_id": flow_id,
                "session_id": session_id
            }

            log = Log(**data)
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            default_logger.error(f'Error: {e}')

    @staticmethod
    def _get_sorted_top_k(
        dist: "np.array", top_k: int
    ) -> Tuple["np.ndarray", "np.ndarray"]:
        if top_k >= dist.shape[1]:
            idx = dist.argsort(axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx, axis=1)
        else:
            idx_ps = dist.argpartition(kth=top_k, axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx_ps, axis=1)
            idx_fs = dist.argsort(axis=1)
            idx = np.take_along_axis(idx_ps, idx_fs, axis=1)
            dist = np.take_along_axis(dist, idx_fs, axis=1)

        return idx, dist


def _get_ones(x, y):
    return np.ones((x, y))


def _ext_A(A):
    nA, dim = A.shape
    A_ext = _get_ones(nA, dim * 3)
    A_ext[:, dim : 2 * dim] = A
    A_ext[:, 2 * dim :] = A ** 2
    return A_ext


def _ext_B(B):
    nB, dim = B.shape
    B_ext = _get_ones(dim * 3, nB)
    B_ext[:dim] = (B ** 2).T
    B_ext[dim : 2 * dim] = -2.0 * B.T
    del B
    return B_ext


def _euclidean(A_ext, B_ext):
    sqdist = A_ext.dot(B_ext).clip(min=0)
    return np.sqrt(sqdist)


def _norm(A):
    return A / np.linalg.norm(A, ord=2, axis=1, keepdims=True)


def _cosine(A_norm_ext, B_norm_ext):
    return A_norm_ext.dot(B_norm_ext).clip(min=0) / 2
