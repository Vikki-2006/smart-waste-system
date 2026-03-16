# Smart Waste Collection System

A complete IoT and AI-powered Smart Waste Management system built with Python Flask, Scikit-learn, SQLite, and vanilla HTML/CSS/JS.

## Features
- **IoT Simulation**: Real-time interval updates to simulate connected bins.
- **Machine Learning**: Random Forest model to predict future overflow scenarios.
- **Route Optimization**: Dijkstra-based graph algorithm to calculate fastest waste collection paths.
- **Dashboard API**: Flask REST APIs providing all backend telemetry.
- **Web Interface**: Modern dark-themed, dashboard featuring live tables and charts.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Initial ML Data**
   ```bash
   cd dataset
   python generate_data.py
   ```
   *(This generated `waste_data.csv` used for ML model training.)*

3. **Run the Backend Application**
   ```bash
   cd backend
   python app.py
   ```
   *(This also initializes the SQLite DB and performs an initial training of the ML model if the data exists.)*

4. **Access the System**
   Open your browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Project Structure
- `backend/app.py`: Main Flask application router.
- `backend/database.py`: SQLite connection and models.
- `backend/model.py`: Scikit-learn Random Forest model config.
- `backend/route_optimizer.py`: Routing algorithm.
- `frontend/`: Web application HTML, CSS, & JS.
- `dataset/`: Training synthetic data generation script.
