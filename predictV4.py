import warnings
import pandas as pd
import numpy as np

from MQTT import *
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from keras.models import Sequential
from keras.layers import LSTM, Dense

# Suppress warning
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

def predict_weather():
# Load the data
    temperature = pd.read_json(
        "https://io.adafruit.com/api/v2/banhbaochien/feeds/feed-temp/data"
    ).value
    humidity = pd.read_json(
        "https://io.adafruit.com/api/v2/banhbaochien/feeds/feed-humidity/data"
    ).value

# Combine the data into a single dataframe
    data = pd.concat([temperature, humidity], axis=1)
    data.columns = ["temperature", "humidity"]

# Target variable: 1 for rainy, 0 for sunny (adjust threshold as needed)
    data['label'] = np.where(data['humidity'] > 0.7, 1, 0)

# Features and target variable
    X = data[['temperature', 'humidity']]
    y = data['label']

# Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

# Make predictions on the test set
    y_pred = model.predict(X_test)

# Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")

# Now you can use the trained model for predictions on new data
    new_data_point = np.array([[25.5, 0.65]])
    prediction = model.predict(new_data_point)
    print(f"Prediction: {'Rainy' if prediction[0] == 1 else 'Sunny'}")
    prediction = 'Rainy' if prediction[0] == 1 else 'Sunny'

    return prediction

def predict():
    # Load the data
    temperature = pd.read_json(
        "https://io.adafruit.com/api/v2/banhbaochien/feeds/feed-temp/data"
    ).value
    humidity = pd.read_json(
        "https://io.adafruit.com/api/v2/banhbaochien/feeds/feed-humidity/data"
    ).value
    
    # Combine the data into a single dataframe
    data = pd.concat([temperature, humidity], axis=1)
    data.columns = ["temperature", "humidity"]

    # Split the data into training and testing sets
    train_size = int(len(data) * 0.8)
    train_data = data.iloc[:train_size, :]
    test_data = data.iloc[train_size:, :]

    # Normalize the data
    mean = train_data.mean()
    std = train_data.std()
    train_data = (train_data - mean) / std
    test_data = (test_data - mean) / std

    # Prepare the data for LSTM
    def prepare_data(data, look_back=1):
        X, y = [], []
        for i in range(len(data) - look_back - 1):
            X.append(data[i : (i + look_back), :])
            y.append(data[i + look_back, :])
        return np.array(X), np.array(y)

    look_back = 10
    train_X, train_y = prepare_data(train_data.values, look_back)
    test_X, test_y = prepare_data(test_data.values, look_back)

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(50, input_shape=(look_back, 2)))
    model.add(Dense(2))
    model.compile(loss="mean_squared_error", optimizer="adam")

    # Train the model
    model.fit(train_X, train_y, epochs=100, batch_size=32, verbose=2)

    # Make predictions on the test data
    test_predict = model.predict(test_X)

    # Inverse transform the predictions and actual values
    test_predict = (test_predict * std.values) + mean.values
    test_y = (test_y * std.values) + mean.values

    # Select the best predicted value for temperature and humidity
    best_predict = test_predict[-1, :]
    best_predict_temperature = round(best_predict[0], 2)
    best_predict_humidity = round(best_predict[1], 2)

    # Check the possibility of rain based on humidity threshold
    rain_threshold = 0.7  
    possibility_of_rain = best_predict_humidity > rain_threshold
    
    return best_predict_temperature, best_predict_humidity, possibility_of_rain

def predictionMainloop():
    while True:
        predictedTemp, predictedHumid, possibility_of_rain = predict()
        
        # Publish predictions and pump activation status
        client.publish("banhbaochien/feeds/predict_temp", str(predictedTemp))
        client.publish("banhbaochien/feeds/predict_humid", str(predictedHumid))
        if predict_weather() == 'Rainy':
            client.publish("banhbaochien/feeds/feed_pump", str(0))
        else:
            client.publish("banhbaochien/feeds/feed_pump", str(1))
        
        # Slow down data due to throttling
        time.sleep(40)

# Run the main loop
predictionMainloop()
