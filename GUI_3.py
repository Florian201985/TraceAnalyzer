import time

import streamlit as st
import pandas as pd
import numpy as np
from bokeh.models import LogColorMapper
from bokeh.plotting import figure, show

import AnalyzeTraces
import AnanlyzeFiles
import ImportTraces

st.title('Trace Analysis')

# Beschreibung der Input Widgets: https://docs.streamlit.io/library/api-reference/widgets

trace_values = []

with st.sidebar:
    uploaded_files = st.file_uploader("Upload trace files", type='.xml', accept_multiple_files=True)

    for uploaded_file in uploaded_files:
        st.write("Importing:", uploaded_file.name)
        trace_val = ImportTraces.ImportData(uploaded_file.getvalue(), 'grinding')
        trace_values.append(dict(filename=uploaded_file, trace=trace_val))
    filenames = AnanlyzeFiles.getfilenames(trace_values)
    option_traces = st.multiselect(
        'Select Traces for analysis',
        filenames, filenames)
    options = AnanlyzeFiles.getOptionsAxis(trace_values)
    option_X = st.selectbox(
        'Select value for the X-axis',
        options)
    option_Y = st.selectbox(
        'Select value for the Y-axis',
        options)
    strokes = AnanlyzeFiles.getStrokes(trace_values)
    option_stroke = st.selectbox(
        'Select stroke for analysis',
        strokes)
    default_idx = options.index(option_X)
    option_crop_val = st.selectbox(
        'Select value for cropping',
        options, index=default_idx) # default: Same as option_X
    values_crop_min = st.slider(
        'Minimum and Maximum value for cropping',
        0.0, 100.0, (25.0, 75.0))
    rpm = st.number_input('Define a rpm for analysis')
    harmonics = st.checkbox('Select if harmonics should be marked')

    df = pd.DataFrame()
    csv = df.to_csv().encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )

def getChartValues(analyzed_traces, option_traces, option_X, option_Y, option_stroke):
    if option_Y == 'Hubnummer':
        option_Y += '_X'
    selected_stroke = 'Stroke_' + str(float(option_stroke))
    for filename in option_traces:
        idx = 0
        for filename_analysis in analyzed_traces:
            name = filename_analysis['filename'].name
            if filename == name:
                data = analyzed_traces[idx]
                for act_stroke in data['data']:
                    if act_stroke['stroke'] == selected_stroke:
                        stroke_data = act_stroke
                        x_val = stroke_data['trace'][option_X]
                        y_val = stroke_data['trace'][option_Y]
                        trace = dict(X=x_val, Y=y_val, label=name, x_label=option_X, y_label=option_Y)
                        # prüfen ob option_y in fft vorhanden, falls ja speichern falls nein None
                        fft = dict(Amplitudes=[], Frequencies=[], label='', x_label='', y_label='')
                        keys = []
                        for key in stroke_data['fft']:
                            keys.append(key)
                        if option_Y in keys:
                            fft = dict(Amplitudes=stroke_data['fft'][option_Y]['amplitudes'],
                                       Frequencies=stroke_data['fft'][option_Y]['frequencies'],
                                       label=name, x_label=option_X, y_label=option_Y)
                        result = dict(trace=trace, fft=fft)
                        break
                break
            idx += 1
    return result


TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,help"

analyzed_traces = []
x_label_trace = 'x'
y_label_trace = 'y'
x_label_fft = 'amplitudes'
y_label_fft = 'frequencies'
if len(trace_values) > 0:
    analyzed_traces = AnalyzeTraces.analyzeTraces(trace_values, cropping=False, crop_val='Z', start=230, end=240)
    chart_values = getChartValues(analyzed_traces, option_traces, option_X, option_Y, option_stroke)
    x_label_trace = chart_values['trace']['x_label']
    y_label_trace = chart_values['trace']['y_label']

    trace_fig = figure(
                title='Traces Stroke: ' + str(option_stroke),
                x_axis_label=x_label_trace,
                y_axis_label=y_label_trace,
                tools=TOOLS)

    trace_fig.line(chart_values['trace']['X'], chart_values['trace']['Y'],
                   legend_label=chart_values['trace']['label'],
                   line_width=2)

    st.bokeh_chart(trace_fig, use_container_width=True)

    fft_fig = figure(
              title='FFT Stroke: ' + str(option_stroke) + ', ' + str(option_Y),
              x_axis_label=x_label_fft,
              y_axis_label=y_label_fft,
              tools=TOOLS)

    fft_fig.line(chart_values['fft']['Frequencies'], chart_values['fft']['Amplitudes'],
                 legend_label=chart_values['fft']['label'],
                 line_width=2)

    st.bokeh_chart(fft_fig, use_container_width=True)



def normal2d(X, Y, sigx=1.0, sigy=1.0, mux=0.0, muy=0.0):
    z = (X-mux)**2 / sigx**2 + (Y-muy)**2 / sigy**2
    return np.exp(-z/2) / (2 * np.pi * sigx * sigy)

X, Y = np.mgrid[-3:3:200j, -2:2:200j]
Z = normal2d(X, Y, 0.1, 0.2, 1.0, 1.0) + 0.1*normal2d(X, Y, 1.0, 1.0)
image = Z * 1e6

color_mapper = LogColorMapper(palette="Viridis256", low=1, high=1e7)

plot = figure(x_range=(0,1), y_range=(0,1), tools=TOOLS)
r = plot.image(image=[image], color_mapper=color_mapper,
               dh=1.0, dw=1.0, x=0, y=0)

#color_bar = r.construct_color_bar(padding=1)

#plot.add_layout(color_bar, "right")

st.bokeh_chart(plot, use_container_width=True)
