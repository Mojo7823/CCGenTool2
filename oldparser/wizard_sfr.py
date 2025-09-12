import pandas as pd
import numpy as np
import joblib

# Load the trained model and encoder from files from current directory
model = joblib.load('resources/trained_model_sfr.joblib')
encoder = joblib.load('resources/encoder_sfr.joblib')
#model = joblib.load('/home/mojo/Desktop/PyCCToolBox/prediction/sfr/trained_model.joblib')
#encoder = joblib.load('/home/mojo/Desktop/PyCCToolBox/prediction/sfr/encoder.joblib')


def binary_to_sfrs(binary_output, sfr_columns):
    sfr_list = []
    for idx, value in enumerate(binary_output[0]):
        if value == 1:
            sfr_list.append(sfr_columns[idx])
    return sfr_list

def predict_sfrs(device_type, eal_level):
    new_data = pd.DataFrame({'DeviceType': [device_type], 'eal_level': [eal_level]})

    # Encode the categorical feature 'DeviceType' using the loaded encoder
    encoded_device_type = encoder.transform(new_data[['DeviceType']])
    encoded_device_type = pd.DataFrame(encoded_device_type, columns=encoder.get_feature_names_out(['DeviceType']))

    # Replace the original 'DeviceType' column with the encoded columns
    new_data = new_data.drop('DeviceType', axis=1)
    new_data = pd.concat([new_data, encoded_device_type], axis=1)

    # Remove 'EAL' prefix from 'eal_level' and convert to integer
    new_data['eal_level'] = new_data['eal_level'].str.replace('EAL', '').astype(int)

    # Make predictions on the new data
    binary_predictions = model.predict(new_data)

    # Load the SFR column names
    sfr_columns = pd.read_csv('resources/sfr_columns.csv', header=None)[0].tolist()

    # Convert binary predictions to SFRs
    sfr_predictions = binary_to_sfrs(binary_predictions, sfr_columns)

    return sfr_predictions