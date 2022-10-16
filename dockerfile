FROM python:3.9-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ src/
ARG PYTHONUNBUFFERED=0
CMD [ "python", "src/main.py" ]
