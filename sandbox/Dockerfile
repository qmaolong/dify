FROM python:3.10-slim-bookworm

RUN echo "deb http://mirrors.aliyun.com/debian testing main" > /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
