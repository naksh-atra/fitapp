# Fitapp

Interactive Streamlit app for planning and exploring workout routines, deployed on Hugging Face Spaces.

## Features
- Streamlit-based UI for quick iteration and sharing
- Dockerized runtime for reproducible deploys on Spaces
- Pyproject-first packaging with src/ layout

## Tech stack
- Python 3.10
- Streamlit
- Hugging Face Spaces (SDK: Docker)

## Project structure
.
├── apps/web/app.py      # Streamlit entry point
├── src/fitapp_core/     # Core logic (src layout)
├── Dockerfile           # Container entry for Spaces
├── pyproject.toml       # Dependencies & metadata (PEP 621)
└── README.md

## Local development
python -m venv .venv && source .venv/bin/activate   # on Linux/Mac
.venv\Scripts\activate                             # on Windows
pip install -e .
streamlit run apps/web/app.py

## Deployment (Hugging Face Spaces)
This Space uses the Docker SDK. The Dockerfile installs the project (pip install -e .) and runs:
streamlit run apps/web/app.py --server.port=8501 --server.address=0.0.0.0

Pushes to main trigger automatic rebuild and redeploy. Build and container logs can be viewed on the Space page for status.

## Configuration
No API keys required at present. If added later, use Space Secrets/Variables and read them via os.getenv.

## Contributing
Fork the repo, create a feature branch, pip install -e ., develop with Streamlit locally, and open a PR. Optionally, enable GitHub Actions CI to validate installs and run basic smoke checks on each PR.

## License
MIT (or your chosen license)
