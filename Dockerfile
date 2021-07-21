FROM jinaai/jina:2.0.2-devel

COPY . /workspace
WORKDIR /workspace

RUN apt-get update && pip install -r requirements.txt

RUN python app.py

ENTRYPOINT ["python", "app.py"]
