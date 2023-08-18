FROM python:3.11.4-bullseye

COPY ./requirements.txt /c2-client/requirements.txt

RUN pip install -r /c2-client/requirements.txt

COPY ./client /c2-client/client
COPY ./resources /c2-client/resources


EXPOSE 8070-8090

CMD ["python", "/c2-client/client/client.py"]
