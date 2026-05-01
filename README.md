# Rytech Crop Recommendation Website

A Flask-based crop recommendation web application that uses soil and weather inputs to suggest suitable crops, estimate profitability, and provide historical user recommendations. The app is built with Python, machine learning models, Google OAuth login, and optional MongoDB persistence for saved history.

## Features

- Soil + weather crop suitability prediction
- Rule-based and ML-based recommendations
- Profit estimation for selected crops
- Google login with OAuth
- Optional MongoDB history tracking
- Automatic model training if model files are missing
- Responsive frontend with Flask templates

## Repository Structure

- `app.py` — main Flask application
- `crops_data.py` — crop metadata and economics used for recommendations
- `model.py` — helper to train and serialize ML models
- `requirements.txt` — Python dependencies
- `samples.md` — test input examples
- `static/` — JavaScript, CSS, and image assets
- `templates/` — Flask HTML templates
- `.env.example` — sample environment variables file

## Setup

1. Install Python 3.7 or newer.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in any required values:

```bash
copy .env.example .env
```

## Environment Variables

The app supports the following variables in `.env`:

```text
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://127.0.0.1:27017/cropdb
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

- `SECRET_KEY` is used by Flask for session security.
- `MONGO_URI` is optional; without MongoDB the app still runs but history is disabled.
- Google OAuth values are optional; if unset, the login page will show a configuration warning.

## Run Locally

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

If the model pickle files are missing, the app will train them automatically on startup.

## Notes

- `README.md` now replaces the earlier `RUN_INSTRUCTIONS.md` for a cleaner repository.
- The repository is configured to ignore virtual environments and generated model artifacts.
- For deployment, use a Python-compatible host such as Render, Fly.io, Railway, or Azure App Service.

## Deployment

This project is a server-based Flask app, so it should be deployed to a Python hosting platform rather than a static-only provider.

## Testing

Use `samples.md` for example inputs and quick manual validation.
