def getfilenames(data):
    result = []
    for file in data:
        result.append(file['filename'].name)
    return result


def getOptionsAxis(data):
    result = ['time']
    if len(data) > 0:
        for val in data[0]['trace']:
            if val.name_short == 'Hubnummer':
                result.append(val.name_short)
            else:
                result.append(val.name_short + '_' + val.axis)
    return result


def getStrokes(data):
    result = ['all']
    number_of_strokes = 0
    if len(data) > 0:
        for val in data[0]['trace']:
            if val.name_short == 'Hubnummer':
                values = val.values
                number_of_strokes = values['Hubnummer_X'].max()
    for stroke_num in range(int(number_of_strokes)):
        result.append(str(stroke_num+1))
    return result