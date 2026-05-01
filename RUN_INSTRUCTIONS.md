# How to Run Crop Recommendation Website

## Prerequisites
- Python 3.7+ venv active
- `pip install -r requirements.txt`

## Steps
1. Train models (if needed):
```
venv/Scripts/python.exe model.py
```
Generates pkl files.

2. Run Flask server:
```
venv/Scripts/python.exe app.py
```

3. Open browser: http://127.0.0.1:5000

4. Enter soil/weather values, submit for ML + rule recs.

Server auto-reloads on code changes. Ctrl+C to stop.

**Currently running!** Test with samples.md.
