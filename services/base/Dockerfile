FROM python:3.8-slim

WORKDIR /project
COPY *.sh ./
RUN chmod 500 *.sh
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY exceptions.py .
COPY connection_manager/ connection_manager/

CMD ["/project/startup.sh"]
