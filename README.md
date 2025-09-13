---
title: Fitapp
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
python_version: "3.10"
tags:
- streamlit
pinned: false
short_description: Workout planning app
---

# Fitapp

Interactive Streamlit app for planning and exploring workout routines, deployed on Hugging Face Spaces via the Docker SDK.

## Features
- Streamlit-based UI for quick iteration and sharing
- Dockerized runtime for reproducible deploys on Spaces
- Pyproject-first packaging with src/ layout

## Tech stack
- Python 3.10
- Streamlit
- Hugging Face Spaces (SDK: Docker, app_port 8501)

## Project structure
.
├── apps/web/app.py      # Streamlit entry point
├── src/fitapp_core/     # Core logic (src layout)
├── Dockerfile           # Container entry for Spaces
├── pyproject.toml       # Dependencies & metadata (PEP 621)
└── README.md

## Local development
Create and activate a virtual environment:
python -m venv .venv && source .venv/bin/activate   # on Linux/Mac
.venv\Scripts\activate                             # on Windows

Install in editable mode:
pip install -e .

Run Streamlit locally:
streamlit run apps/web/app.py

## Deployment (Hugging Face Spaces)
- This Space uses the Docker SDK. The YAML block at the top of README selects `sdk: docker` and `app_port: 8501`.
- The Dockerfile installs the project (`pip install -e .`) and starts the app with:
  streamlit run apps/web/app.py --server.port=8501 --server.address=0.0.0.0
- Pushes to `main` trigger an automatic build and redeploy.
- Use the Space’s Build and Container logs for diagnostics.

## Configuration
- No API keys or secrets are required at this time.
- If added later, store them as Space Secrets/Variables and access with os.getenv.
- The optional `python_version` field in the YAML ensures Python 3.10 is used.

## Contributing
- Fork the repo, create a feature branch, and run:
  pip install -e .
- Develop with Streamlit locally, then open a PR.
- Optionally, add a GitHub Actions workflow to smoke-test installation and imports.

## License
Open source — MIT (or your chosen license).

---

### Notes
- Hugging Face Spaces requires the YAML block at the very top of README.md for metadata.
- For Docker SDK apps, `app_port` tells Spaces which internal container port to expose.
- The actual app startup is defined by the Dockerfile CMD.
- Do not add `app_file` for Docker SDK — the Dockerfile governs the process.
