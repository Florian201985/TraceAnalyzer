import numpy as np
import pandas as pd
from scipy.fft import rfft, rfftfreq
import streamlit as st

def ParameterFFT(time_values, values):
    duration = time_values[-1] - time_values[0]
    # Sample rate in Hertz und Anzahl Datenpunkt N berechnen
    N = len(values)
    sample_rate = N / duration
    # Amplituden berechnen
    amplitudes = rfft(values)
    # Amplitude korrekt Skalieren
    amplitudes = 2.0 * np.abs(amplitudes) / N
    # Frequenzen berechnen
    frequencies = rfftfreq(N, 1 / sample_rate)
    result = dict(frequencies=frequencies, amplitudes=amplitudes)
    return result

def StrokeFFT(df):
    fft = {}
    time = list(df.T.values[0])
    for val in df.columns:
        if val == 'time' or val == 'Hubnummer_X' or val == 'Lageistwert_Y' or val == 'Lageistwert_Z':
            continue
        fft[val] = ParameterFFT(time, list(df[val].values))
    result = fft
    return result

def splitStrokes(df):
    # Find the indices of the first and last occurrence of each positive integer value
    positive_integer_values = set(val for val in df['Hubnummer_X'] if val > 0)
    first_last_occurrence_indices = {}

    for val in positive_integer_values:
        first_index = df.index[(df['Hubnummer_X'] == val)].min()
        last_index = df.index[(df['Hubnummer_X'] == val)].max()
        first_last_occurrence_indices[val] = (first_index, last_index)

    # Create a dictionary to store the separate sections
    sections = {}

    hubnummer_value = 1.0
    # Iterate through the groups and store each section in the dictionary
    for start, end in sorted(first_last_occurrence_indices.values()):
        section_data = df.iloc[start:end]
        #section_data['time'] = section_data['time'] - section_data['time'].min()  # Adjust times
        #splitted_df = section_data.drop(columns=['split_point'])
        # Interpolate missing values using the 'linear' method
        df_interpolated = section_data.interpolate(method='linear', axis=0)
        sections[f'Stroke_{hubnummer_value}'] = df_interpolated
        hubnummer_value += 1

    result = sections
    return result

def analyzeTraces(trace_values, cropping, crop_val, start, end):
    trace_dataframe = []
    for traces in trace_values:
        print('Analyzing: ' + traces['filename'].name)
        trace_dict = {}
        for trace in traces['trace']:
            val = trace.values
            cols = val.columns
            time = val[cols[0]].values
            values = val[cols[1]].values
            if 'time' not in trace_dict:
                trace_dict[cols[0]] = time
            trace_dict[cols[1]] = values

        # Convert the dict to a dataframe, split the strokes and interpolate missing values
        splitted_df = splitStrokes(pd.DataFrame(trace_dict))
        # crop the strokes by start and end point in time, Z-Pos or Y-Pos
        cropped_df = splitted_df
        if cropping:
            cropped_df = {}
            for stroke in splitted_df:
                stroke_df = splitted_df[stroke]
                if crop_val == 'time':
                    cropped_df[stroke] = stroke_df[(stroke_df['time'] >= start) & (stroke_df['time'] <= end)]
                elif crop_val == 'Z':
                    cropped_df[stroke] = stroke_df[(stroke_df['Lageistwert_Z'] >= start) & (stroke_df['Lageistwert_Z'] <= end)]
                elif crop_val == 'Y':
                    cropped_df[stroke] = stroke_df[(stroke_df['Lageistwert_Y'] >= start) & (stroke_df['Lageistwert_Y'] <= end)]
                else:
                    raise Exception('crop_val has to be time, Z or Y. The value of crop_val was: {}'.format(crop_val))
        # Analyze trace by FFT
        stroke_fft = {}
        hubnummer_value = 1.0
        for stroke in cropped_df:
            fft = StrokeFFT(cropped_df[stroke])
            stroke_fft[f'Stroke_{hubnummer_value}'] = fft
            hubnummer_value += 1.0
        trace_dataframe.append(dict(filename=traces['filename'], trace=cropped_df, fft=stroke_fft))
    result = []
    # rearranging the data so that each stroke contains the traces and the fft
    for trace in trace_dataframe:
        data = []
        for stroke in trace['trace']:
            data.append(dict(stroke=stroke, trace=trace['trace'][stroke], fft=trace['fft'][stroke]))
        result.append(dict(filename=trace['filename'], data=data))
    return result