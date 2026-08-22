#!/bin/bash

# Ensure ML models are trained if not already present
if [ ! -f "app/ml/models/budget_model.pkl" ] || [ ! -f "app/ml/models/city_embeddings.npy" ]; then
    echo "ML Models not found. Running training pipeline..."
    python app/ml/train.py
else
    echo "ML Models found."
fi

# Run database migrations (Assuming Alembic is set up, if not, FastAPI lifespan handles create_all)
# alembic upgrade head

# Start Gunicorn server
exec gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000}
