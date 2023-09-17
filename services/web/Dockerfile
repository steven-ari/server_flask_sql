# pull official base image
FROM python:3.10.7-slim

# set work directory
WORKDIR /usr/src/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

# install system dependencies: general, tesseract, opencv, pdf2img
RUN apt-get update && apt-get install -y netcat
RUN apt-get -y install libleptonica-dev tesseract-ocr 
RUN apt-get -y install libtesseract-dev python3-pil 
RUN apt-get -y install tesseract-ocr-eng tesseract-ocr-script-latn
RUN apt-get -y install ffmpeg libsm6 libxext6
RUN apt-get -y install poppler-utils

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/requirements.txt
RUN pip install -r requirements.txt
RUN pip install debugpy

# run entrypoint.sh
ENTRYPOINT ["/usr/src/entrypoint.sh"]
