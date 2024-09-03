import os
import pandas as pd
from datetime import datetime
import openpyxl
import dyntools
import csv

global script_directory
script_directory = os.getcwd()


# ------------------------------------------------------------------------------------------------------------------
def report():
    # Get the current working directory
    script_directory = os.getcwd()

    # Define the folder containing Excel files
    ExcelFolder = 'csv_folder'

    # Define the path to the main Excel file (Report.xlsx)
    file_name = 'UserInputs.xlsx'
    file_path = os.path.join(script_directory, file_name)

    # Read the main Excel file into a DataFrame
    df = pd.read_excel(file_path, sheet_name='Sheet1')

    # Assuming df and df_Excel are your DataFrames
    pick_values = ['PickTime1Event1', 'PickTime2Event1', 'PickTime1Event2', 'PickTime2Event2',
                   'PickTime1Event3', 'PickTime2Event3']
    Sequential = ['Sequential1', 'Sequential2', 'Sequential3']
    print_values = [['PickVal11Event1', 'PickVal21Event1', 'PickVal11Event2', 'PickVal21Event2',
                     'PickVal11Event3', 'PickVal21Event3'],
                    ['PickVal12Event1', 'PickVal22Event1', 'PickVal12Event2', 'PickVal22Event2',
                     'PickVal12Event3', 'PickVal22Event3'],
                    ['PickVal13Event1', 'PickVal23Event1', 'PickVal13Event2', 'PickVal23Event2',
                     'PickVal13Event3', 'PickVal23Event3']]

    # Iterate over each file name in the 'File' column
    for index, Excel_name in df['File'].items():
        # Check if Excel_name is not NaN
        if pd.notna(Excel_name):
            # Construct the full path to each Excel file in ExcelFolder
            Excel_path = os.path.join(script_directory, ExcelFolder, str(Excel_name))
            # Initialize variables for header row detection
            header_row = None
            skip_rows = 0

            # Find the header row containing 'Time(s)' in df_Excel
            while header_row is None:
                df_temp = pd.read_csv(Excel_path, skiprows=skip_rows, header=None)
                # Check if any row contains 'Time(s)' as a string
                header_row_indices = df_temp[
                    df_temp.apply(lambda row: 'Time(s)' in str(row.values), axis=1)].index.tolist()
                if header_row_indices:
                    header_row = header_row_indices[0]  # Extract the index from the list
                else:
                    skip_rows += 1

            # Read the Excel file starting from the identified header row
            df_Excel = pd.read_csv(Excel_path, skiprows=header_row)
            df_Excel['Time(s)'] = pd.to_numeric(df_Excel['Time(s)'], errors='coerce')
            for time_pick_index, time_pick in enumerate(pick_values):
                time_value = df.at[index, time_pick]
                for seq_index, seq_col in enumerate(Sequential):
                    col_to_find = df.at[index, seq_col]
                    # Find the index of the row where 'Time(s)' is closest to time_value
                    if 'Time(s)' in df_Excel.columns:
                        closest_time_index = (df_Excel['Time(s)'] - time_value).abs().idxmin()
                        # Extract the value from df_Excel based on 'value_to_find' at the closest time index
                        if col_to_find in df_Excel.columns:
                            found_value = df_Excel.at[closest_time_index, col_to_find]
                            print_col = print_values[seq_index][time_pick_index]
                            df.loc[index, print_col] = round(found_value, 2)
    # Save the updated DataFrame back to Report.xlsx
    df.to_excel(file_path, index=False)  # Set index=False to avoid writing row indices


# ------------------------------------------------------------------------------------------------------------------
def UserInput():
    # Define the folder and main file paths
    ExcelFolder = 'Excel_File'
    file_name = 'UserInputs.xlsx'
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, file_name)
    # Read the main Excel file into a DataFrame
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    df['XIncrement'] = df['XIncrement'].astype(float)
    Sequential = ['Sequential1', 'Sequential2', 'Sequential3']
    Max = ['Max1', 'Max2', 'Max3']
    Min = ['Min1', 'Min2', 'Min3']
    Increment = ['Increment1', 'Increment2', 'Increment3']

    # Initialize columns for storing results if they don't exist
    if 'XMin' not in df.columns:
        df['XMin'] = None
    if 'XMax' not in df.columns:
        df['XMax'] = None
    for min_col, max_col, inc_col in zip(Min, Max, Increment):
        if min_col not in df.columns:
            df[min_col] = None
        if max_col not in df.columns:
            df[max_col] = None
        if inc_col not in df.columns:
            df[inc_col] = None

    for col in Min + Max + Increment:
        if col in df.columns:
            df[col] = df[col].astype(float)
    # Iterate over each file name in the 'File' column

    for index, Excel_name in df['File'].items():
        if pd.notna(Excel_name):
            start_times = {}
            stop_times = {}
            average_value = {}
            max_value = {}
            min_value = {}

            # Construct the full path to each Excel file in ExcelFolder
            Excel_path = os.path.join(script_directory, ExcelFolder, str(Excel_name))

            # Initialize variables for header row detection
            header_row = None
            skip_rows = 0

            # Find the header row containing 'Time(s)'
            while header_row is None:
                df_temp = pd.read_excel(Excel_path, sheet_name='Sheet1', skiprows=skip_rows, header=None)
                header_row = df_temp[df_temp.apply(lambda row: 'Time(s)' in str(row.values), axis=1)].index.tolist()
                if header_row:
                    header_row = header_row[0]  # Extract the index from the list
                else:
                    skip_rows += 1

            # Read the Excel file starting from the identified header row
            df_Excel = pd.read_excel(Excel_path, sheet_name='Sheet1', skiprows=header_row)
            for seq_col in Sequential:
                value_to_check = df[seq_col].iloc[index]
                for i in range(len(df_Excel) - 1):  # Assuming iteration over rows with indices
                    if not pd.isna(value_to_check):
                        this_value = round(df_Excel[value_to_check].iloc[i], 5)
                        next_value = round(df_Excel[value_to_check].iloc[i + 1], 5)
                        if this_value != next_value:
                            start_times[seq_col] = df_Excel['Time(s)'].iloc[i]
                            break
                for i in range(len(df_Excel) - 2, -1, -1):
                    if not pd.isna(value_to_check):
                        this_value = round(df_Excel[value_to_check].iloc[i], 5)
                        next_value = round(df_Excel[value_to_check].iloc[i + 1], 5)
                        if this_value != next_value:
                            stop_times[seq_col] = df_Excel['Time(s)'].iloc[i + 1]
                            break

            XMin_value = min(start_times.values())
            XMax_value = max(stop_times.values())
            if df['FaultDuration'].iloc[index] != 'LessThanOne':
                df.loc[index, 'XMin'] = round(XMin_value, 0) - 1
                df.loc[index, 'XMax'] = round(XMax_value, 0) + 1

                XIncrement_value = (XMax_value - XMin_value)
                if round(XIncrement_value / 20, 1) < 1:
                    df.loc[index, 'XIncrement'] = float(0.5)
                else:
                    df.loc[index, 'XIncrement'] = round(XIncrement_value / 20, 0)
            else:
                df.loc[index, 'XMin'] = round(df['PickTime1Event1'].iloc[index], 0) - 5
                df.loc[index, 'XMax'] = round(df['PickTime2Event1'].iloc[index], 0) + 5
                df.loc[index, 'XIncrement'] = float(0.5)

            # Check if the header row contains values from the sequential columns
            for seq_col in Sequential:
                value_to_check = df[seq_col].iloc[index]
                if value_to_check in df_Excel.columns:
                    average_value[seq_col] = df_Excel[value_to_check].mean()
                    max_value[seq_col] = df_Excel[value_to_check].max()
                    min_value[seq_col] = df_Excel[value_to_check].min()

            # Calculate min and max values with adjustments for each sequential column
            for seq_col, min_col, max_col, inc_col in zip(Sequential, Min, Max, Increment):
                if seq_col in average_value:
                    min_val = max(min_value[seq_col], average_value[seq_col] * 0.1)
                    max_val = min(max_value[seq_col], average_value[seq_col] * 10)
                    if abs(max_val) < 2:
                        if (round((max_val - min_val) / 20, 2) > 0):
                            df.loc[index, min_col] = round((min_val - round((max_val - min_val) / 20, 2)), 2)
                            df.loc[index, max_col] = round((max_val + round((max_val - min_val) / 20, 2)), 2)
                            df.loc[index, inc_col] = round((max_val - min_val) / 20, 2)
                        else:
                            df.loc[index, min_col] = round((min_val - 0.01), 2)
                            df.loc[index, max_col] = round((max_val + 0.01), 2)
                            df.loc[index, inc_col] = 0.01
                    else:
                        if (round((max_val - min_val) / 20, 0) > 0):
                            df.loc[index, min_col] = round(min_val - round((max_val - min_val) / 20, 0), 0)
                            df.loc[index, max_col] = round(max_val + round((max_val - min_val) / 20, 0), 0)
                            df.loc[index, inc_col] = round((max_val - min_val) / 20, 0)
                        else:
                            df.loc[index, min_col] = round(min_val - 1, 0)
                            df.loc[index, max_col] = round(max_val + 1, 0)
                            df.loc[index, inc_col] = 1

    # Save the updated DataFrame back to UserInputs.xlsx
    df.to_excel(file_path, index=False)  # Set index=False to avoid writing row indices


# ------------------------------------------------------------------------------------------------------------------

def create_folder(folder_name):
    full_path = os.path.join(script_directory, folder_name)
    # Check if the folder already exists
    if not os.path.exists(full_path):
        # Create the folder
        os.makedirs(full_path)


# ----------------------------------------------------
def boolOut2Xlsx(str_path_out, str_path_xlsx):
    obj_chnf = dyntools.CHNF(str_path_out)
    short_title, chanid, chandata = obj_chnf.get_data()
    keys = list(chanid.keys())
    ordered_keys = [keys[-1]] + keys[:-1]
    rows = list(zip(*chandata.values()))
    with open(str_path_xlsx, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            [chanid[key].decode('utf-8') if isinstance(chanid[key], bytes) else chanid[key] for key in ordered_keys])
        writer.writerow(ordered_keys)
        writer.writerows(rows)


# =============================================================================
def Out_To_Excel():
    folder_name_Excel = "csv_folder"
    create_folder(folder_name_Excel)
    folder_name = "Out_File"
    folder_path = os.path.join(script_directory, folder_name)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".out"):  # Check if the file is a .sav file
                file_name_without_extension = os.path.splitext(file)[0]
                file_path = os.path.join(root, file)
                str_path_out = os.path.join(script_directory, folder_name_Excel)
                csv_file = "{}.csv".format(file_name_without_extension)
                str_path_xlsx = os.path.join(str_path_out, csv_file)
                boolOut2Xlsx(file_path, str_path_xlsx)


# =============================================================================
# =============================================================================
# Call function
# =============================================================================
print("1/4 Work Started.")
print(datetime.now())
Out_To_Excel()
print("2/3 Excel/csv Created.")
print(datetime.now())
# UserInput()
print("3/3 Input File updated.")
print(datetime.now())
print("Work Completed.")