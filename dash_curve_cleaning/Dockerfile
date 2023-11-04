FROM nginx/unit:1.23.0-python3.9

ENV PIP_INDEX_URL=http://192.168.17.23/pypi/simple/
ENV PIP_TRUSTED_HOST=192.168.17.23

COPY ./app /app
COPY nginx_unit/config.json /docker-entrypoint.d/config.json

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && apt-get install -y libsnappy-dev build-essential

RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r /tmp/requirements.txt

RUN apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean

RUN useradd -r -u 1001 -g root worker
#USER worker
