# Wildfire-Risk-Analysis

wildfire_forecast/
├── data_pipeline/
│   ├── preprocess.py
│   ├── train_model.py
│   ├── requirements.txt
│   └── Dockerfile          <-- optional if you want to containerize training
│
├── model_store/
│   └── model.pkl           <-- output of training (ignored by git)
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── package.json
│   ├── src/
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
