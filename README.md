# SeekerCNSC

[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg?raw=true  "We fully commit to open-source")](https://get.jina.ai)

A demo neural search project that uses Jina. Jina is the cloud-native neural search framework powered by state-of-the-art AI and deep learning.

## Features

## Install

```bash
pip install -r requirements.txt
```

## Set environment variables

.

## Run

| Command                  | Description                  |
| :---                     | :---                         |
| ``python app.py``        | To index files/data          |

## APIs

Search
```bash
curl --request POST 'http://0.0.0.0:8000/search/' --header 'Content-Type: application/json' --data-raw '{"data":["What is Neural Search?"], "parameters": {"business": "CNSC"}}'
```

Body
```bash
{
    "data":["What is Neural Search?"],
    "parameters": {
        "business": "CNSC"
    }
}
```


Index Docs
```bash
curl --request POST 'http://0.0.0.0:8000/index_docs/' --header 'Content-Type: application/json'
```

Body
```bash
{
    "data":[
        {
            "text": "What is Neural Search?",
            "tags": {
                "business": "DEVAR", 
                "category": "TI",
                "subcategory": "KEOS",
                "question": "What is Neural Search?",
                "answer": "The core idea of neural search is to leverage state-of-the-art deep neural networks to build every component of a search system. In short, neural search is deep neural network-powered information retrieval. In academia, it’s often called neural IR."
            }
        },
        {
            "text": "What is Jina?",
            "tags": {
                "question": "What is Jina?",
                "answer": "Jina🔊 is a neural search framework that empowers anyone to build SOTA and scalable deep learning search applications in minutes.",
                "business": "VARDEL", 
                "category": "TI",
                "subcategory": "KEOS"
            }
        }
    ]
}
```

Feedback
```bash
curl --request POST 'http://0.0.0.0:8000/feedback/' --header 'Content-Type: application/json'
```
Body
```bash
{
    "uuid": "8e402293-de3d-492c-b277-275c3f0313ed",
    "qualification": true
}
```

Get Categoies
```bash
curl --request POST 'http://0.0.0.0:8000/categories/' --header 'Content-Type: application/json'
```
Body
```bash
{
    "business": "CNSC"
}
```

Generate Categoies
```bash
curl --request POST 'http://0.0.0.0:8000/categories_generate/' --header 'Content-Type: application/json'
```
Body
```bash
{
    "business": "CNSC"
}
```

## Note:
.

## License

Copyright (c) 2020 luca. All rights reserved.
