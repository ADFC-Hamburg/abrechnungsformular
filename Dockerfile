# syntax=docker/dockerfile:1

FROM python:3.11.2

WORKDIR /abrechnungsformular

COPY ./requirements.txt /abrechnungsformular/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /abrechnungsformular/requirements.txt

COPY . /abrechnungsformular

CMD ["python3", "abrechnungsformular.py"]
