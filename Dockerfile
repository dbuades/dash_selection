FROM python:3.7.4

ADD src /dash/

WORKDIR /dash/

RUN pip install -r ./requirements.txt

CMD [ "python", "./script.py" ]
