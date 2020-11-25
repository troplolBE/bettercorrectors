FROM python:3.9

LABEL maintainer='tcastron'
LABEL version='0.1'
LABEL description='container that runs the bettercorrecors program'

WORKDIR /bettercorrectors

COPY requirements.txt .
COPY *.py .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
