FROM jinaai/jina:2.6.4

COPY . /workspace
WORKDIR /workspace

RUN apt-get update && pip install -r requirements.txt

RUN python app.py

ENTRYPOINT ["python", "app.py"]
