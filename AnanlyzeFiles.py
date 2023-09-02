def getfilenames(data):
    result = []
    for file in data:
        result.append(file['filename'].name)
    return result