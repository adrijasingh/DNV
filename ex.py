import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import csv
#matplotlib.use('Agg')

# Define global paths
script_directory = os.getcwd()
user_inputs_path = os.path.join(script_directory, 'UserInputs.xlsx')
folder_name_Excel = "csv_folder"
folder_name_image = "Image"

def create_folder(folder_name):
    full_path = os.path.join(script_directory, folder_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

def set_axis_colors(ax, color):
    ax.spines['left'].set_color(color)
    ax.tick_params(axis='y', colors=color)
    ax.yaxis.label.set_color(color)

def generate_graph():
    try:
        df_inputs = pd.read_excel(user_inputs_path, sheet_name='Sheet1')
    except Exception as e:
        print(f"Error reading {user_inputs_path}: {e}")
        return

    x_column_name = 'time'

    for index, row in df_inputs.iterrows():
        chart_title = row['ChartTitle']
        x_min = row['XMin'] if not (np.isnan(row['XMin']) or np.isinf(row['XMin'])) else 0
        x_max = row['XMax']
        x_increment = row['XIncrement']
        excel_file_name = str(row['File'])
        excel_file_path = os.path.join(script_directory, folder_name_Excel, excel_file_name)

        try:
            df_data = pd.read_csv(excel_file_path,skiprows=1)
        except Exception as e:
            print(f"Error reading {excel_file_path}: {e}")
            continue

        parameters, legends, colors, mins, maxes, increments = [], [], [], [], [], []

        for i in range(1, 4):
            seq_num = row.get(f'Sequential{i}', None)
            legend = row.get(f'Legend{i}', '')

            if seq_num is not None and 0 < seq_num < len(df_data.columns):
                param = df_data.columns[int(seq_num)]
                parameters.append(param)
                legends.append(legend if legend else param)
                colors.append(row[f'Color{i}'])

                min_val = row[f'Min{i}']
                max_val = row[f'Max{i}']
                increment = row[f'Increment{i}']

                min_val = min_val if not (np.isnan(min_val) or np.isinf(min_val)) else df_data[param].min()
                max_val = max_val if not (np.isnan(max_val) or np.isinf(max_val)) else df_data[param].max()
                increment = increment if not (np.isnan(increment) or increment <= 0) else (max_val - min_val) / 15

                mins.append(min_val)
                maxes.append(max_val)
                increments.append(increment)

        fig, ax1 = plt.subplots(figsize=(10, 8))
        ax1.set_xlabel('Time (seconds)')
        ax1.set_xlim(x_min, x_max)
        ax1.set_xticks(np.arange(x_min, x_max + x_increment, x_increment))
        plt.title(chart_title)

        lines, labels = [], []

        ax2 = None
        ax3 = None

        for i, (param, legend) in enumerate(zip(parameters, legends)):
            color = colors[i]
            min_val = mins[i]
            max_val = maxes[i]
            increment = increments[i]
            y_ticks = np.arange(min_val, max_val + increment, increment)

            if i == 0:
                ax = ax1
            elif i == 1:
                ax2 = ax1.twinx()
                ax = ax2
            elif i == 2:
                ax3 = ax1.twinx()
                ax3.spines["right"].set_position(("outward", 60))
                ax = ax3

            line = ax.plot(df_data[x_column_name], df_data[param], color=color, label=legend)
            lines.extend(line)
            labels.append(legend)

            ax.set_ylabel(legend, color=color)
            ax.set_ylim(min_val, max_val)
            ax.set_yticks(y_ticks)
            set_axis_colors(ax, color)

        if ax2:
            ax2.spines['right'].set_position(('outward', 60))
            set_axis_colors(ax2, colors[1])
        if ax3:
            ax3.spines['right'].set_position(('outward', 120))
            set_axis_colors(ax3, colors[2])

        ax1.legend(lines, labels, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=len(parameters), borderaxespad=0.)
        fig.tight_layout()
        ax1.grid(True, which='major', axis='both', color='grey')

        file_name_without_extension = os.path.splitext(os.path.basename(excel_file_path))[0]
        file_image = "{}.png".format(chart_title)
        folder_path = os.path.join(script_directory, folder_name_image, file_name_without_extension)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        image_path = os.path.join(folder_path, file_image)
        count = 1
        while os.path.exists(image_path):
            file_image = "{}_{}.png".format(chart_title, count)
            image_path = os.path.join(folder_path, file_image)
            count += 1

        plt.savefig(image_path)
        plt.close()

generate_graph()