import pandas as pd
import numpy as np

label = 'trace1.xml'
name_label = label
name = label
option_X = 'time'
option_Y = 'Konturabweichung_B'
x_val = pd.DataFrame([1, 2, 3, 4, 5])
y_val = pd.DataFrame([0, 1, 0, 1, 0])
amp = np.array([5, 4, 3, 2, 1])
freq = np.array([2.5, 3.1, 4.8, 9.4, 11.4])
trace1 = dict(X=x_val, Y=y_val, label=name_label, x_label=option_X, y_label=option_Y)
fft1 = dict(Amplitudes=amp, Frequencies=freq, label=name, x_label=option_X, y_label=option_Y)

label = 'trace2.xml'
name_label = label
name = label
option_X = 'time'
option_Y = 'Konturabweichung_B'
x_val = pd.DataFrame([1, 2, 3, 4, 5])
y_val = pd.DataFrame([0, 1, 0, 1, 0])
amp = np.array([10, 8, 6, 4, 2])
freq = np.array([2.7, 3.3, 4.2, 9.1, 11.8])
#freq = np.array([2.5, 3.1, 4.8, 9.4, 11.4])
trace2 = dict(X=x_val, Y=y_val, label=name_label, x_label=option_X, y_label=option_Y)
fft2 = dict(Amplitudes=amp, Frequencies=freq, label=name, x_label=option_X, y_label=option_Y)

label = 'trace3.xml'
name_label = label
name = label
option_X = 'time'
option_Y = 'Konturabweichung_B'
x_val = pd.DataFrame([1, 2, 3, 4, 5])
y_val = pd.DataFrame([0, 1, 0, 1, 0])
amp = np.array([7.5, 6, 4.5, 3, 1.5])
freq = np.array([2.2, 3.6, 4.4, 9.8, 11.4])
#freq = np.array([2.5, 3.1, 4.8, 9.4, 11.4])
trace3 = dict(X=x_val, Y=y_val, label=name_label, x_label=option_X, y_label=option_Y)
fft3 = dict(Amplitudes=amp, Frequencies=freq, label=name, x_label=option_X, y_label=option_Y)

chart_values = []
chart_values.append(dict(trace=trace1, fft=fft1))
chart_values.append(dict(trace=trace2, fft=fft2))
chart_values.append(dict(trace=trace3, fft=fft3))

import plotly.graph_objs as go
from scipy.interpolate import interp1d

# Extract frequencies from the first trace
frequencies_original = chart_values[0]['fft']['Frequencies']

# Create a list to store interpolated amplitudes
interpolated_amplitudes = []

# Loop through each trace and interpolate amplitudes
for data in chart_values:
    original_frequencies = data['fft']['Frequencies']
    original_amplitudes = data['fft']['Amplitudes']

    # Create interpolation function
    interp_func = interp1d(original_frequencies, original_amplitudes, kind='linear', fill_value="extrapolate")

    # Interpolate amplitudes
    interpolated_amplitudes.append(interp_func(frequencies_original))

# Extracting data
fft_labels = [data['fft']['label'] for data in chart_values]

# Create meshgrid for surface plot
X, Y = np.meshgrid(frequencies_original, fft_labels)

# Create the 3D surface plot
fig = go.Figure(data=[go.Surface(z=interpolated_amplitudes, x=X, y=Y)])

# Customize the layout
fig.update_layout(scene=dict(
                    xaxis_title='Frequencies',
                    yaxis_title='FFT Labels',
                    zaxis_title='Amplitudes'
                ))

# Show the plot
fig.show()