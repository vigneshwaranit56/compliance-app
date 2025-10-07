# Compliance Platform - FastAPI Implementation

This is a minimal FastAPI implementation generated from the provided OpenAPI document.
Run:

```
pip install -r requirements.txt
uvicorn main:app --reload
```

Project structure:
- main.py : application entry
- app/
  - models.py : Pydantic schemas
  - storage.py : in-memory storage (replace with DB)
  - routers/
    - organizations.py
    - documents.py
    - dashboard.py
    - assets.py
- requirements.txt# compliance-app
