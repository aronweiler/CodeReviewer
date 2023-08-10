FROM python:latest

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/ src/

ENTRYPOINT ["python3", "-u", "/src/app.py"]
