FROM python:3.11

ADD main.py .

ADD database.py .

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY locdir/ /locdir/

CMD ["python", "./main.py"]