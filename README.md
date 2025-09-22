# Rainfall Prediction Dashboard

A real-time AI-powered rainfall prediction system that provides continuous weather forecasting with intelligent threat assessment.

## Overview

This application uses a trained neural network model to predict rainfall probability in real-time. The system generates realistic weather data based on historical patterns and provides instant predictions with visual threat indicators.

## Features

### Real-time Predictions
- Continuous AI predictions updated every second
- Rainfall probability displayed as percentage (0-100%)
- Automatic data generation based on historical weather patterns
- No manual input required - fully autonomous operation

### Intelligent Threat Assessment
- Low Threat (0-39%): Normal conditions with green indicators
- Medium Threat (40-69%): Moderate risk with yellow indicators  
- High Threat (70%+): Critical conditions with red warnings and visual alerts

### Professional Dashboard
- Clean, modern interface with light theme
- Responsive design for all devices
- Real-time status indicators
- Current weather data display
- Visual threat level indicators with color coding

## Technical Architecture

### Machine Learning Model
- PyTorch neural network with 3 fully connected layers
- Input features: 9 weather parameters including pixel data, rainfall history, and forecasting metrics
- Trained on Pakistan rainfall dataset
- Model outputs converted to probability percentages using sigmoid normalization

### Backend Technology
- Flask web framework for API endpoints
- Background threading for continuous predictions
- Real-time data streaming capabilities
- Joblib for model serialization

### Frontend Technology
- Vanilla JavaScript for real-time updates
- CSS3 with modern styling and animations
- Responsive grid layout
- Professional color scheme with threat-based styling

## Installation

### Prerequisites
- Python 3.7 or higher
- Required Python packages (install via pip)

### Setup Instructions

1. Clone or download the project files
2. Install required dependencies:
```bash
pip install torch numpy pandas scikit-learn flask joblib
```

3. Ensure the following files are present:
   - `model.pth` (trained PyTorch model)
   - `scaler.pkl` (feature scaler)
   - `Rain_fall_in_Pakistan.csv` (training dataset)

4. Run the application:
```bash
python app.py
```

5. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## File Structure

```
project/
├── app.py                          # Main Flask application
├── model.py                        # Model training script
├── model.pth                       # Trained neural network model
├── scaler.pkl                      # Feature scaling parameters
├── Rain_fall_in_Pakistan.csv       # Training dataset
├── templates/
│   ├── dashboard.html              # Original dashboard interface
│   └── realtime_dashboard.html     # Real-time prediction interface
└── README.md                       # Project documentation
```

## API Endpoints

### GET /
Returns the main dashboard interface

### GET /latest
Returns the most recent prediction data in JSON format:
```json
{
  "prediction": 45.2,
  "raw_prediction": 2.1847,
  "threat_level": "MEDIUM",
  "timestamp": "2025-09-22T14:30:15.123456",
  "features": {
    "n_pixels": 1250.5,
    "rfh": 12.3,
    "rfh_avg": 8.7,
    "r1h": 5.2,
    "r1h_avg": 4.1,
    "r3h": 15.8,
    "r3h_avg": 12.4,
    "rfq": 0.85,
    "r3q": 0.92
  }
}
```

### POST /predict
Accepts manual feature input for custom predictions

## Model Details

### Input Features
- n_pixels: Number of precipitation pixels detected
- rfh: Recent rainfall height measurement
- rfh_avg: Average rainfall height over time period
- r1h: 1-hour rainfall measurement
- r1h_avg: Average 1-hour rainfall
- r3h: 3-hour rainfall measurement  
- r3h_avg: Average 3-hour rainfall
- rfq: Rainfall frequency quotient
- r3q: 3-hour rainfall quotient

### Model Architecture
- Input Layer: 9 features
- Hidden Layer 1: 64 neurons with ReLU activation
- Hidden Layer 2: 32 neurons with ReLU activation
- Output Layer: 1 neuron for regression output

### Data Processing
- StandardScaler normalization applied to all input features
- Raw model outputs converted to percentages using sigmoid transformation
- Realistic data generation based on original dataset statistics

## Configuration

### Prediction Frequency
The system updates predictions every second. To modify this interval, adjust the sleep time in the `continuous_prediction()` function:

```python
time.sleep(1)  # Update every 1 second
```

### Threat Thresholds
Threat levels can be customized in the `get_threat_level()` function:

```python
def get_threat_level(percentage):
    if percentage >= 70:    # High threat threshold
        return "HIGH"
    elif percentage >= 40:  # Medium threat threshold
        return "MEDIUM"
    else:
        return "LOW"
```

## Troubleshooting

### Common Issues

**Model Loading Error**
- Ensure `model.pth` file exists and was trained with the same architecture
- Verify PyTorch installation and compatibility

**Scaler Loading Error**
- Confirm `scaler.pkl` was created using joblib, not pickle
- Check file permissions and accessibility

**Data Generation Issues**
- Verify `Rain_fall_in_Pakistan.csv` is accessible
- Ensure CSV contains the required feature columns

**Port Already in Use**
- Change the port in `app.run()` or stop other Flask applications

### Performance Optimization
- For production deployment, use a WSGI server like Gunicorn
- Consider implementing caching for frequently accessed data
- Monitor memory usage with continuous prediction threading

## License

This project is provided as-is for educational and research purposes.

## Support

For technical issues or questions about implementation, refer to the Flask and PyTorch documentation for additional guidance on web application deployment and machine learning model integration.