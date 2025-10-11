# Wildfire Risk Analysis

Full-stack project for analyzing and forecasting wildfire risks.

---

## 📁 Directory Structure

```text
wildfire_forecast/
├── data_pipeline/              # Scripts for data processing and model training
│   ├── preprocess.py           # Preprocess raw wildfire data
│   ├── train_model.py          # Train and evaluate model
│   ├── requirements.txt        # Dependencies for training environment
│   └── Dockerfile              # (Optional) Docker container for training
│
├── model_store/                # Trained models (not tracked by Git)
│   └── model.pkl               # Output from model training
│
├── backend/                    # Backend API service
│   ├── app.py                  # API logic using Flask or FastAPI
│   ├── requirements.txt        # Backend dependencies
│   └── Dockerfile              # Docker setup for backend
│
├── frontend/                   # Frontend UI (e.g., React app)
│   ├── package.json            # Frontend dependencies
│   ├── src/                    # Source code for UI
│   └── Dockerfile              # Docker setup for frontend
│
├── docker-compose.yml          # Compose file to run all services
└── README.md                   # Project overview and setup instructions
