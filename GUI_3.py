import time

import streamlit as st
import pandas as pd
import numpy as np

import ImportTraces

st.title('Trace Analysis')

# Beschreibung der INput Widgets: https://docs.streamlit.io/library/api-reference/widgets

trace_values = []

with st.sidebar:
    uploaded_files = st.file_uploader("Upload trace files", type='.xml', accept_multiple_files=True)

    for uploaded_file in uploaded_files:
        st.write("Importing:", uploaded_file.name)
        trace_val = ImportTraces.ImportData(uploaded_file.getvalue(), 'grinding')
        trace_values.append(dict(filename=uploaded_file, trace=trace_val))
    option_traces = st.multiselect(
        'Select Traces for analysis',
        ['Green', 'Yellow', 'Red', 'Blue'],
        ['Yellow', 'Red'])
    option_X = st.selectbox(
        'Select value for the X-axis',
        ('Email', 'Home phone', 'Mobile phone'))
    option_Y = st.selectbox(
        'Select value for the Y-axis',
        ('Email', 'Home phone', 'Mobile phone'))
    option_stroke = st.selectbox(
        'Select stroke for analysis',
        ('Email', 'Home phone', 'Mobile phone'))
    option_crop_val = st.selectbox(
        'Select value for cropping',
        ('Email', 'Home phone', 'Mobile phone'))
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

from bokeh.plotting import figure

x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,help"
trace_fig = figure(
            title='Traces',
            x_axis_label='x',
            y_axis_label='y',
            tools=TOOLS)

trace_fig.line(x, y, legend_label='trace', line_width=2)

st.bokeh_chart(trace_fig, use_container_width=True)

fft_fig = figure(
          title='FFT',
          x_axis_label='x',
          y_axis_label='y',
          tools=TOOLS)

fft_fig.line(y, x, legend_label='fft', line_width=2)

st.bokeh_chart(fft_fig, use_container_width=True)

from bokeh.models import LogColorMapper
from bokeh.plotting import figure, show


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
