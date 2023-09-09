import os
import time

import streamlit as st
import pandas as pd
import numpy as np
import itertools

from bokeh.models import LogColorMapper, Range1d, NumeralTickFormatter
from bokeh.plotting import figure
from bokeh.palettes import Dark2_5 as palette


import AnalyzeTraces
import AnanlyzeFiles
import ExportToExcel
import ImportTraces

def CalcTableRPM(number_of_starts, number_of_teeth, worm_rpm):
    result = worm_rpm * number_of_starts / number_of_teeth
    return result

def CalcFrequency(rpm):
    result = rpm / 60.0
    return result


def getMinMaxValues(analyzed_traces, option_crop_val, option_stroke):
    trace_data = analyzed_traces[0]['data'][int(option_stroke)-1]['trace']
    values = trace_data[option_crop_val]
    min_val = min(values)
    max_val = max(values)
    result = dict(min=min_val, max=max_val)
    return result


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
    # Analyzing trace without cropping
    if len(trace_values) > 0:
        analyzed_traces_temp = AnalyzeTraces.analyzeTraces(trace_values, cropping=False, crop_val='time',start=0.0, end=100.0)
    # cropping the data to specific values in Z or Y,
    # time is not working as all strokes will be cropped and time is very different between the strokes
    default_idx = options.index(option_X)
    cropping = st.checkbox('Select if traces should be cropped')
    option_crop_val = st.selectbox(
        'Select value for cropping',
        ['Lageistwert_Y', 'Lageistwert_Z'], index=1, disabled=not cropping)

    min_max = dict(min=0.0, max=100.0)
    if len(trace_values) > 0:
        min_max = getMinMaxValues(analyzed_traces_temp, option_crop_val, option_stroke)

    min_crop = st.number_input('Minimum value for cropping', min_value=min_max['min'], max_value=min_max['max'],
                               value=min_max['min'], step=1.0)
    max_crop = st.number_input('Maximum value for cropping', min_value=min_max['min'], max_value=min_max['max'],
                               value=min_max['max'], step=1.0)
    values_crop = [min_crop, max_crop]
    # Data for calculating the harmonics
    rpm = st.number_input('Define a rpm for analysis')
    number_of_teeth = st.number_input('Define number of teeth on the gear')
    number_of_starts = st.number_input('Define number of starts on the worm')

    harmonics_table = st.checkbox('Select if harmonics of the table should be marked')
    number_of_harmonics_table = st.slider(
        'Choose the number of harmonics for the table',
        1, 50, 5, disabled=not harmonics_table)

    harmonics_worm = st.checkbox('Select if harmonics of the worm should be marked')
    number_of_harmonics_worm = st.slider(
        'Choose the number of harmonics for the worm',
        1, 5, 1, disabled=not harmonics_worm)


@st.cache_data
def getChartValues(analyzed_traces, option_traces, option_X, option_Y, option_stroke):
    result = []
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
                        result.append(dict(trace=trace, fft=fft))
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
    analyzed_traces = AnalyzeTraces.analyzeTraces(trace_values, cropping=cropping, crop_val=option_crop_val,
                                                  start=values_crop[0], end=values_crop[1])
    chart_values = getChartValues(analyzed_traces, option_traces, option_X, option_Y, option_stroke)
    x_label_trace = chart_values[0]['trace']['x_label']
    y_label_trace = chart_values[0]['trace']['y_label']

    # colors has a list of colors which can be used in plots
    colors_trace = itertools.cycle(palette)
    colors_fft = itertools.cycle(palette)

    trace_fig = figure(
                title='Traces Stroke: ' + str(option_stroke),
                x_axis_label=x_label_trace,
                y_axis_label=y_label_trace,
                tools=TOOLS, width=1250)

    for val in chart_values:
        trace_fig.line(val['trace']['X'], val['trace']['Y'],
                       legend_label=val['trace']['label'],
                       line_width=2, color=next(colors_trace))

    st.bokeh_chart(trace_fig, use_container_width=False)

    if st.button("Download trace data as .xslx", type='primary'):
        home_dir = os.path.expanduser("~")
        download_path = os.path.join(home_dir, "Downloads", 'trace.xlsx')
        ExportToExcel.export_to_excel(download_path, chart_values, 'trace')

    fft_fig = figure(
              title='FFT Stroke: ' + str(option_stroke) + ', ' + str(option_Y),
              x_axis_label=x_label_fft,
              y_axis_label=y_label_fft,
              tools=TOOLS, width=1250)

    max_val = 0.0
    for val in chart_values:
        fft_fig.line(val['fft']['Frequencies'], val['fft']['Amplitudes'],
                     legend_label=val['fft']['label'],
                     line_width=2, color=next(colors_fft))
        if max(val['fft']['Amplitudes']) >= max_val:
            max_val = max(val['fft']['Amplitudes'])

    table_rpm = 0.0
    tabel_freq = 0.0
    worm_freq = 0.0
    if harmonics_table or harmonics_worm:
        table_rpm = CalcTableRPM(number_of_starts, number_of_teeth, rpm)
        tabel_freq = CalcFrequency(table_rpm)
        worm_freq = CalcFrequency(rpm)

    for idx in range(number_of_harmonics_table):
        t_freq = tabel_freq * (idx + 1)
        fft_fig.line([t_freq, t_freq], [-1.0, 1.0],
                     legend_label='table rpm',
                     line_width=1, color='red')
    for idx in range(number_of_harmonics_worm):
        w_freq = worm_freq * (idx + 1)
        fft_fig.line([w_freq, w_freq], [-1.0, 1.0],
                     legend_label='worm rpm',
                     line_width=1, color='red', line_dash='dashed')
    # Set the y-axis formatter to use standard notation
    fft_fig.yaxis.formatter = NumeralTickFormatter(format="0.00000")
    fft_fig.y_range = Range1d(0, max_val)
    st.bokeh_chart(fft_fig, use_container_width=False)

    if st.button("Download fft data as .xslx", type='primary'):
        home_dir = os.path.expanduser("~")
        download_path = os.path.join(home_dir, "Downloads", 'fft.xlsx')
        ExportToExcel.export_to_excel(download_path, chart_values, 'fft')

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
