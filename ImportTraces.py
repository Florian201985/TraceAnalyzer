import re

import numpy as np
import pandas as pd
import xmltodict
import pandas

from Trace import Trace


def ImportData(path, traceType):
    axis_out = []
    # path = 'C:\\01_Arbeit\\431008\\DatenMaschine\\Moment_B_C.xml'
    # xml_data = open(path, 'r').read()
    xml_data = path
    xmlDict = xmltodict.parse(xml_data)

    trace_data = xmlDict['traceSession']['traceData']['dataFrame']['rec']
    table = ({**value} for value in trace_data)

    # Daten in einen DataFrame importieren
    df = pandas.DataFrame(table).astype(float)

    # Benennung der Daten
    trace = []
    trace_names = xmlDict['traceSession']['traceData']['dataFrame']['dataSignal']
    for trace_name in trace_names:
        temp = ''
        if '/Nck/!SD/' in trace_name['@name']:
            temp = re.findall("/Nck/!SD/(.*)", trace_name['@name'])[0]
        elif '/Nck/!SEMA/' in trace_name['@name']:
            temp = re.findall("/Nck/!SEMA/(.*)", trace_name['@name'])[0]
        elif '/Channel/!SMA/' in trace_name['@name']:
            temp = re.findall("/Channel/!SMA/(.*)", trace_name['@name'])[0]
        elif '/Nck/!S/' in trace_name['@name']:
            temp = re.findall("/Nck/!S/(.*)", trace_name['@name'])[0]
        elif '/Nck/!GD2/' in trace_name['@name']:
            temp = re.findall("/Nck/!GD2/(.*)", trace_name['@name'])[0]
        temp_strs = temp.replace('/', '').replace(',', '').replace('[', '').replace(']', '').split(" ")
        name = temp_strs[0]
        axis_number = 0
        if len(temp_strs) > 1:
            axis_number = int(temp_strs[2])
        key = trace_name['@key']
        id = trace_name['@id']

        if name == 'nckServoDataActPos2ndEnc64':
            value_description_long = 'Lageistwert'
            value_description_short = 'Lageistwert'
            unit = 'mm'
        elif name == 'nckServoDataContDev64':
            value_description_long = 'Konturabweichung'
            value_description_short = 'Konturabweichung'
            unit = 'mm'
        elif name == 'nckServoDataCmdTorque64':
            value_description_long = 'Momenten-/Kraft-Sollwert (begrenzt)'
            value_description_short = 'Momenten_Kraft_Sollwert'
            unit = 'Nm'
        elif name == 'nckServoDataActCurr64':
            value_description_long = 'Momentenbildender Stromistwert'
            value_description_short = 'Stromistwert'
            unit = 'A'
        elif name == 'nckServoDataDrvLoad64':
            value_description_long = 'Auslastung (m_soll/m_soll,grenz)'
            value_description_short = 'Auslastung'
            unit = '%'
        elif name == 'nckServoDataActVelMot64':
            value_description_long = 'Drehzahl-/Geschwindigkeitsistwert Motor'
            value_description_short = 'Drehzahl_Geschwindigkeitsistwert'
            unit = 'rpm/ m/s'
        elif name == 'measPosDev':
            value_description_long = 'Lageistwert-Differenz zwischen 2 Messsystemen'
            value_description_short = 'Messsystemen_Differenz'
            unit = 'mm'
        elif name == 'nckServoDataActPos1stEnc64':
            value_description_long = 'Lageistwert_Messsystem_1'
            value_description_short = 'Lageistwert_Messsystem_1'
            unit = 'mm'
        elif name == 'nckServoDataActPos2ndEnc64':
            value_description_long = 'Lageistwert_Messsystem_2'
            value_description_short = 'Lageistwert_Messsystem_2'
            unit = 'mm'
        elif name == 'nckServoDataCtrlDev64':
            value_description_long = 'Regeldifferenz'
            value_description_short = 'Regeldifferenz'
            unit = 'mm'
        elif name == 'nckServoDataActEnc64':
            value_description_long = 'Aktives_Messsystem'
            value_description_short = 'Aktives_Messsystem'
            unit = ''
        elif name == 'actToolBasePos':
            value_description_long = 'Werkzeugaufnahme'
            value_description_short = 'Werkzeugaufnahme'
            unit = ''
        elif name == 'GRD_ACTUALSTROKENUMBER':
            value_description_long = 'Hubnummer'
            value_description_short = 'Hubnummer'
            unit = ''
        else:
            value_description_long = 'unknown'
            value_description_short = 'unknown'
            unit = ''
        if axis_number == 0:
            axis = 'No'
        elif axis_number == 1:
            axis = 'X'
        elif axis_number == 2:
            axis = 'Y'
        elif axis_number == 3:
            axis = 'B'
        elif axis_number == 5:
            axis = 'A'
        elif axis_number == 7:
            axis = 'C'
        elif axis_number == 11:
            axis = 'Z'
        else:
            axis = 'unknown'
        trace.append(Trace(value_description_long, value_description_short, axis, key, id, unit))

    df.rename(columns={'@time': 'time'}, inplace=True)
    time = df['time']

    for td in trace:
        key = '@' + td.id
        name = td.name_short
        if traceType != 'km0':
            name += '_' + td.axis
        df.rename(columns={key: name}, inplace=True)
        values = df[name]
        if name == 'Hubnummer_X':
            values = values.replace(np.nan, -10)
        else:
            values = values.replace(np.nan, None)

        values = values.astype(float)
        vals = pd.concat([time, values], axis=1)
        td.setValues(vals)

    return trace
