FROM python:3.9-slim

RUN apt-get update && \
    apt-get install --quiet --assume-yes \
    libffi-dev \
    libssl-dev \
    python3-pip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY app /app/code

CMD ["uvicorn", "code.main:app", "--host", "0.0.0.0", "--port", "80"]
