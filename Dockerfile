FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY app /app/code

CMD ["uvicorn", "code.main:app", "--host", "0.0.0.0", "--port", "80"]