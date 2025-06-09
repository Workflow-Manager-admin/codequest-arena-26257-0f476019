# codequest-arena-26257-0f476019

## Running the FastAPI Backend

**To run the backend API with Uvicorn for local development:**

```bash
cd codequest_arena
uvicorn src.api.main:app --reload
```

- The app will be available at http://localhost:8000 (by default).
- If you encounter `ModuleNotFoundError: No module named 'api'`,
  ensure you are running uvicorn from inside the `codequest_arena/` directory
  and use `src.api.main:app` (not `api.main:app`).
- If using a virtual environment, activate it before running uvicorn:
  `source venv/bin/activate`

**Test commands:**
```bash
pytest          # Run inside codequest_arena/ to execute backend tests
```

Front-end and other setup details are in the `frontend/README.md`.