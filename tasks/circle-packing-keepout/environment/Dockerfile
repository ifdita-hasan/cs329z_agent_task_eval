# Starting environment for the circle-packing task.
FROM python:3.12.16-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337

RUN pip install --no-cache-dir numpy==2.5.3 scipy==1.18.1

WORKDIR /app
COPY check_packing.py /app/check_packing.py
