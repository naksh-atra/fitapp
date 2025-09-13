FROM python:3.10
WORKDIR /app

# Copy project metadata and source needed for install
COPY pyproject.toml .
COPY src/ ./src

# Install the project and its dependencies from pyproject.toml
RUN pip install --no-cache-dir -e .

# Copy the rest of the app (UI, assets, etc.)
COPY . .

# Streamlit runtime
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EXPOSE 8501
CMD ["streamlit","run","apps/web/app.py","--server.port=8501","--server.address=0.0.0.0"]
