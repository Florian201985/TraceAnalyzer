import pandas as pd
from openpyxl import load_workbook


def export_to_excel(filename_excel, parameters, trace_fft):

    # Find the maximum length of x and y across all parameters
    max_len_x = max(len(param['trace']['X']) for param in parameters)
    max_len_y = max(len(param['trace']['Y']) for param in parameters)

    # Create a DataFrame
    df = pd.DataFrame()

    # Iterate through the parameters list
    for param in parameters:
        trace_param = param[trace_fft]
        x_label = trace_param['x_label']
        x = list(trace_param['X'].values)
        y_label = trace_param['y_label']
        y = list(trace_param['Y'].values)

        for idx in range(max_len_x-len(x)):
            x.append(float('nan'))
            y.append(float('nan'))

        # Create a DataFrame for the current parameter
        df_param = pd.DataFrame({x_label: x, y_label: y})

        # Concatenate this parameter's DataFrame with the main DataFrame
        df = pd.concat([df, df_param], axis=1)

    # Write to Excel
    df.to_excel(filename_excel, index=False)

    # Open the created Excel file
    wb = load_workbook(filename_excel)

    # Select the active sheet
    ws = wb.active

    # Insert two rows at the beginning
    ws.insert_rows(1, amount=2)

    col = 1
    for param in parameters:
        # Set the values for filename and label
        ws.cell(row=1, column=col, value=param[trace_fft]['label'])
        ws.cell(row=2, column=col, value='')
        col += 2

    # Save the modified Excel file
    wb.save(filename_excel)