#!/bin/bash

alembic upgrade head

# pytest -sv app/tests/integration_tests/test_hotels/test_hotels_api.py

gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
