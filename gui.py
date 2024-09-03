import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog,
                             QMessageBox, QDialog, QDialogButtonBox, QLineEdit)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import numpy as np
import x
import ex

class PlotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.df1 = None
        self.df2 = None
        self.y1min = None
        self.y1max = None
        self.y2min = None
        self.y2max = None
        self.y3min = None
        self.y3max = None
        self.xmin = None
        self.xmax = None
        self.x_interval = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Advanced Plot Generator')
        self.setWindowIcon(QIcon('/mnt/data/image.png'))
        self.setGeometry(100, 100, 800, 600)

        vbox = QVBoxLayout()

        # Set background color for the window
        self.setStyleSheet("background-color: #f0f0f0;")

        # DNV GL logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap('C:\\Users\\Adrija\\Desktop\\dnvproject\\logo.png')
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.logo_label)

        # Load CSV buttons
        self.load_button1 = QPushButton('Load CSV File 1', self)
        self.load_button1.setIcon(QIcon('path_to_your_load_icon.png'))
        self.load_button1.setStyleSheet("background-color: #4CAF50; color: white;")
        self.load_button1.clicked.connect(lambda: self.load_csv(1))
        vbox.addWidget(self.load_button1)

        self.load_button2 = QPushButton('Load CSV File 2', self)
        self.load_button2.setIcon(QIcon('path_to_your_load_icon.png'))
        self.load_button2.setStyleSheet("background-color: #4CAF50; color: white;")
        self.load_button2.clicked.connect(lambda: self.load_csv(2))
        vbox.addWidget(self.load_button2)

        # File selection for columns
        self.file_combo_a = QComboBox(self)
        self.file_combo_a.addItems(['File 1', 'File 2'])
        vbox.addWidget(QLabel('Select file for y1:'))
        vbox.addWidget(self.file_combo_a)

        self.file_combo_b = QComboBox(self)
        self.file_combo_b.addItems(['File 1', 'File 2'])
        vbox.addWidget(QLabel('Select file for y2:'))
        vbox.addWidget(self.file_combo_b)

        self.file_combo_c = QComboBox(self)
        self.file_combo_c.addItems(['File 1', 'File 2'])
        vbox.addWidget(QLabel('Select file for y3:'))
        vbox.addWidget(self.file_combo_c)

        # Column selection ComboBoxes
        self.combo_a = QComboBox(self)
        self.combo_b = QComboBox(self)
        self.combo_c = QComboBox(self)
        vbox.addWidget(QLabel('Y1:'))
        vbox.addWidget(self.combo_a)
        vbox.addWidget(QLabel('Y2:'))
        vbox.addWidget(self.combo_b)
        vbox.addWidget(QLabel('Y3:'))
        vbox.addWidget(self.combo_c)

        # Title input
        self.label_t = QLabel('Title:')
        self.entry_t = QLineEdit(self)
        vbox.addWidget(self.label_t)
        vbox.addWidget(self.entry_t)

        # Generate Plot button
        self.plot_button = QPushButton('Generate Plot', self)
        self.plot_button.setIcon(QIcon('path_to_your_plot_icon.png'))
        self.plot_button.setStyleSheet("background-color: #008CBA; color: white;")
        self.plot_button.clicked.connect(self.generate_plot)
        vbox.addWidget(self.plot_button)

        # Custom limits button
        self.custom_limits_button = QPushButton('Set Custom Limits', self)
        self.custom_limits_button.setStyleSheet("background-color: #f39c12; color: white;")
        self.custom_limits_button.clicked.connect(self.set_custom_limits)
        self.custom_limits_button.setEnabled(False)
        vbox.addWidget(self.custom_limits_button)

        self.x_button = QPushButton('Run Dynamic(main).py', self)
        self.x_button.setStyleSheet("background-color: #e74c3c; color: white;")
        self.x_button.clicked.connect(self.run_custom_function)
        vbox.addWidget(self.x_button)

        self.ex_button = QPushButton('Run CreateImage', self)
        self.ex_button.setStyleSheet("background-color: #77c3ec; color: white;")
        self.ex_button.clicked.connect(self.run_custom_function)
        vbox.addWidget(self.ex_button)

        self.setLayout(vbox)

    def load_csv(self, file_number):
        file_path = QFileDialog.getOpenFileName(self, f'Open CSV File {file_number}', '', 'CSV files (*.csv)')[0]
        if file_path:
            if file_number == 1:
                self.df1 = pd.read_csv(file_path)
                self.df1 = self.df1.drop(index=[0, 1])
            else:
                self.df2 = pd.read_csv(file_path)
                self.df2 = self.df2.drop(index=[0, 1])

            self.update_column_combos()
            QMessageBox.information(self, "Success", f"CSV file {file_number} loaded and processed.")
            self.custom_limits_button.setEnabled(True)
        else:
            QMessageBox.warning(self, "Error", "Failed to load CSV file.")

    def update_column_combos(self):
        columns1 = self.df1.columns.tolist() if self.df1 is not None else []
        columns2 = self.df2.columns.tolist() if self.df2 is not None else []

        for combo in [self.combo_a, self.combo_b, self.combo_c]:
            combo.clear()
            if self.file_combo_a.currentText() == 'File 1':
                combo.addItems(columns1)
            else:
                combo.addItems(columns2)

    def generate_plot(self):
        if self.df1 is None and self.df2 is None:
            QMessageBox.warning(self, "Error", "Please load at least one CSV file.")
            return
        self.combo_a.clearFocus()
        self.combo_b.clearFocus()
        self.combo_c.clearFocus()
        try:
            a_col = self.combo_a.currentText()
            b_col = self.combo_b.currentText()
            c_col = self.combo_c.currentText() if self.combo_c.isEnabled() else None
            a_file = self.file_combo_a.currentText()
            b_file = self.file_combo_b.currentText()
            c_file = self.file_combo_c.currentText() if c_col else None

            # Validate columns
            if a_col == "Time(s)" or not a_col:
                a_col = None
            if b_col == "Time(s)" or not b_col:
                b_col = None
            if c_col == "Time(s)" or not c_col:
                c_col = None

            if a_col is None and b_col is None and c_col is None:
                QMessageBox.warning(self, "Error", "No valid columns selected for plotting.")
                return

            # Determine the correct DataFrame for each column
            df_a = self.df1 if a_file == 'File 1' else self.df2
            df_b = self.df1 if b_file == 'File 1' else self.df2
            df_c = self.df1 if c_file == 'File 1' else self.df2 if c_col else None

            fig, ax1 = plt.subplots(figsize=(12, 6))
            if self.xmin and self.xmax:
                xmin = float(self.xmin)
                xmax = float(self.xmax)
                ax1.set_xlim(xmin, xmax)
            else:
                xmin, xmax = None, None

            handles, labels = [], []

            def filter_data(df, column):
                if xmin is not None and xmax is not None:
                    return df[(df.index >= xmin) & (df.index <= xmax)][column]
                return df[column]

            # Plot each valid column
            if a_col:
                data_a = filter_data(df_a, a_col)

                ax1.set_ylabel(f'{a_col}', color='tab:blue')
                line1, = ax1.plot(df_a.index, df_a[a_col], color='tab:blue', linestyle='-')
                handles.append(line1)
                labels.append(f'{a_col}')
                ax1.tick_params(axis='y', labelcolor='tab:blue')
                if self.y1min and self.y1max:
                    ax1.set_ylim(float(self.y1min), float(self.y1max))
                else:
                    ax1.set_ylim(data_a.min() * 0.8, data_a.max() * 1.2)

            if b_col:
                ax2 = ax1.twinx()
                ax2.set_ylabel(f'{b_col}', color='tab:orange')
                data_b = filter_data(df_b, b_col)

                line2, = ax2.plot(df_b.index, df_b[b_col], color='tab:orange', linestyle='-')
                handles.append(line2)
                labels.append(f'{b_col}')
                ax2.tick_params(axis='y', labelcolor='tab:orange')
                if self.y2min and self.y2max:
                    ax2.set_ylim(float(self.y2min), float(self.y2max))
                else:
                    ax2.set_ylim(data_b.min() * 0.5, data_b.max() * 2.5)

            if c_col:
                ax3 = ax1.twinx()
                ax3.spines['right'].set_position(('outward', 60))
                ax3.set_ylabel(f'{c_col}', color='tab:green')
                data_c = filter_data(df_c, c_col)

                line3, = ax3.plot(df_c.index, df_c[c_col], color='tab:green', linestyle='-')
                handles.append(line3)
                labels.append(f'{c_col}')
                ax3.tick_params(axis='y', labelcolor='tab:green')
                if self.y3min and self.y3max:
                    ax3.set_ylim(float(self.y3min), float(self.y3max))
                else:
                    ax3.set_ylim(data_c.min() * 0.7, data_c.max() * 2)

            title = self.entry_t.text() if self.entry_t.text() else "Graph"
            plt.title(title)
            plt.grid(True)
            if self.x_interval:
                plt.gca().xaxis.set_major_locator(plt.MultipleLocator(float(self.x_interval)))
            ax1.set_xlabel('Time')
            #ax1.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.5, -0.1), ncol=3)

            def cursor_annotation(event):
                if event.inaxes is not None:
                    x = event.xdata
                    # Initialize annotation text with x coordinate
                    annotation_text = f'x={x:.2f}'

                    for line in handles:
                        # Check if the cursor is within the line
                        contains, _ = line.contains(event)
                        if contains:
                            # Find the y value at the given x coordinate
                            xdata = line.get_xdata()
                            ydata = line.get_ydata()

                            # Interpolating y value for the given x
                            if len(xdata) > 1 and xdata[0] != xdata[-1]:
                                y_interp = np.interp(x, xdata, ydata)
                                annotation_text = f'{line.get_label()}: x={x:.2f}, y={y_interp}'
                                break  # Stop after finding the first line

                    plt.gca().set_title(annotation_text, fontsize=10)
                    plt.draw()

            fig.canvas.mpl_connect('motion_notify_event', cursor_annotation)

            plt.legend(handles, labels, loc='upper right')
            footnotes = []
            if a_col:
                footnotes.append(f'{a_col} Max: {data_a.max()}, Min: {data_a.min()}')
            if b_col:
                footnotes.append(f'{b_col} Max: {data_b.max()}, Min: {data_b.min()}')
            if c_col:
                footnotes.append(f'{c_col} Max: {data_c.max()}, Min: {data_c.min()}')

            plt.figtext(0.99, 0.01, '\n'.join(footnotes), horizontalalignment='right', fontsize=10)
            plt.show()

        except Exception as e:
            print("Error generating plot:", e)
            QMessageBox.critical(self, "Error", f"An error occurred while generating the plot:\n{str(e)}")

    def set_custom_limits(self):
        dialog = CustomLimitsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
                self.xmin, self.xmax, self.x_interval, self.y1min, self.y1max, self.y2min, self.y2max, self.y3min, self.y3max = (
                    dialog.xmin, dialog.xmax, dialog.x_interval, dialog.y1min, dialog.y1max, dialog.y2min, dialog.y2max,
                    dialog.y3min, dialog.y3max)

    def run_custom_function(self):
        try:
            # Placeholder function for custom logic from x
            self.custom_logic_from_x()
            QMessageBox.information(self, "Success", "Custom function from x executed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while the custom function: {str(e)}")

    def custom_logic_from_x(self):
        # Add your custom functionality from x here
        x.Out_To_Excel()
        x.report()
        # x.UserInput()# Example function call from x
    def run_create_image(self):
        ex.generate_graph()

class CustomLimitsDialog(QDialog):
    def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle('Custom Limits')
            self.setModal(True)

            layout = QVBoxLayout()
            self.xmin = QLineEdit(self)
            self.xmax = QLineEdit(self)
            self.x_interval = QLineEdit(self)
            self.y1min = QLineEdit(self)
            self.y1max = QLineEdit(self)
            self.y2min = QLineEdit(self)
            self.y2max = QLineEdit(self)
            self.y3min = QLineEdit(self)
            self.y3max = QLineEdit(self)

            layout.addWidget(QLabel('X-axis Min:'))
            layout.addWidget(self.xmin)
            layout.addWidget(QLabel('X-axis Max:'))
            layout.addWidget(self.xmax)
            layout.addWidget(QLabel('X-axis Interval:'))
            layout.addWidget(self.x_interval)
            layout.addWidget(QLabel('Y1 Min:'))
            layout.addWidget(self.y1min)
            layout.addWidget(QLabel('Y1 Max:'))
            layout.addWidget(self.y1max)
            layout.addWidget(QLabel('Y2 Min:'))
            layout.addWidget(self.y2min)
            layout.addWidget(QLabel('Y2 Max:'))
            layout.addWidget(self.y2max)
            layout.addWidget(QLabel('Y3 Min:'))
            layout.addWidget(self.y3min)
            layout.addWidget(QLabel('Y3 Max:'))
            layout.addWidget(self.y3max)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

            self.setLayout(layout)

    def accept(self):
            self.xmin = self.xmin.text() or None
            self.xmax = self.xmax.text() or None
            self.x_interval = self.x_interval.text() or None
            self.y1min = self.y1min.text() or None
            self.y1max = self.y1max.text() or None
            self.y2min = self.y2min.text() or None
            self.y2max = self.y2max.text() or None
            self.y3min = self.y3min.text() or None
            self.y3max = self.y3max.text() or None
            super().accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlotApp()
    ex.show()
    sys.exit(app.exec_())