FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH="/app/src:${PYTHONPATH}"
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EXPOSE 8501
CMD ["streamlit","run","apps/web/app.py","--server.port=8501","--server.address=0.0.0.0"]