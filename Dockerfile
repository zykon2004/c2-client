FROM python:3.11.4-bullseye

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./client /app

EXPOSE 7000-9000

CMD ["python", "app/client.py"]
