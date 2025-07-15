# python-agents/guideagent/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

#CMD ["python", "agent-service.py"]
#CMD ["python", "main.py"]

#CMD ["sh", "-c", "python agent-service.py & python main.py"]

RUN chmod +x start.sh

CMD ["./start.sh"]