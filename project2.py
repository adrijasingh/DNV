import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QFileDialog, QMessageBox, QInputDialog, QListWidget,
    QAbstractItemView, QDialog, QHBoxLayout, QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtCore import Qt


class KeySelectionDialog(QDialog):
    def __init__(self, keys, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Keys")
        self.selected_keys = []
        self.keys = keys
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        instruction = QLabel("Select keys:")
        layout.addWidget(instruction)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        for idx, key in enumerate(self.keys):
            self.list_widget.addItem(f"{idx}: {key}")
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(submit_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def submit(self):
        selected_items = self.list_widget.selectedItems()
        if len(selected_items) == 0:
            QMessageBox.warning(self, "Selection Error", "Please select at least one key.")
            return
        self.selected_keys = [int(item.text().split(":")[0]) for item in selected_items]
        self.accept()


class ColumnSelectionDialog(QDialog):
    def __init__(self, keys, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Columns to Display")
        self.selected_columns = []
        self.keys = keys
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        instruction = QLabel("Select columns to display:")
        layout.addWidget(instruction)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        for idx, key in enumerate(self.keys):
            self.list_widget.addItem(f"{idx}: {key}")
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(submit_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def submit(self):
        selected_items = self.list_widget.selectedItems()
        self.selected_columns = [int(item.text().split(":")[0]) for item in selected_items]
        self.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Key and Value Selector")
        self.resize(800, 600)
        self.data = None
        self.key = []
        self.value = []
        self.keys_used = []
        self.selected_columns = []
        self.filtered_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Load CSV Button
        self.load_button = QPushButton("Load CSV File")
        self.load_button.clicked.connect(self.load_csv)
        layout.addWidget(self.load_button)
        # Label to show loaded file
        self.file_label = QLabel("No file loaded.")
        layout.addWidget(self.file_label)
        # Button to select keys
        self.select_key_button = QPushButton("Select Keys")
        self.select_key_button.clicked.connect(self.select_keys)
        self.select_key_button.setEnabled(False)
        layout.addWidget(self.select_key_button)
        # Label to show selected keys
        self.selected_keys_label = QLabel("No keys selected.")
        layout.addWidget(self.selected_keys_label)
        # Button to select columns to display
        self.select_columns_button = QPushButton("Select Columns to Display")
        self.select_columns_button.clicked.connect(self.select_columns_to_display)
        self.select_columns_button.setEnabled(False)
        layout.addWidget(self.select_columns_button)
        # Button for sorting
        self.sort_button = QPushButton("Sort Data", self)
        self.sort_button.clicked.connect(self.sort_data)
        layout.addWidget(self.sort_button)
        # Table to display final data
        self.table = QTableWidget()
        layout.addWidget(self.table)
        # Button to save to CSV
        self.save_button = QPushButton("Save to CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def load_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "",
                                                   "CSV Files (.csv);;All Files ()", options=options)
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.file_label.setText(f"Loaded File: {file_path}")
                self.process_columns()
                self.select_key_button.setEnabled(True)
                self.select_columns_button.setEnabled(False)
                self.selected_keys_label.setText("No keys selected.")
                self.table.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV file.\n{str(e)}")
                self.file_label.setText("No file loaded.")
                self.select_key_button.setEnabled(False)

    def process_columns(self):
        X = self.data.columns.tolist()
        self.key = [X[i] for i in range(0, len(X), 2)]
        self.value = [X[i] for i in range(1, len(X), 2)]
        # Ensure key and value lists are of same length
        min_length = min(len(self.key), len(self.value))
        self.key = self.key[:min_length]
        self.value = self.value[:min_length]

    def select_keys(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a CSV file first.")
            return

        dialog = KeySelectionDialog(self.key, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_indices = dialog.selected_keys
            self.keys_used = [(self.key[idx], self.value[idx]) for idx in selected_indices]
            self.selected_columns = self.keys_used.copy()
            keys_display = ", ".join([f"{k}" for k, _ in self.keys_used])
            self.selected_keys_label.setText(f"Selected Keys: {keys_display}")
            self.generate_superkey()
            self.select_columns_button.setEnabled(True)
            self.save_button.setEnabled(True)

    def generate_superkey(self):
        if not self.keys_used:
            QMessageBox.warning(self, "No Keys", "No keys selected.")
            return

        # Create the superkey by combining selected key columns
        selected_key_columns = [k for k, _ in self.keys_used]
        self.filtered_data = self.data.copy()
        self.filtered_data['superkey'] = self.filtered_data[selected_key_columns].astype(str).agg('_'.join, axis=1)

        # Generate supervalue by concatenating the value columns corresponding to selected keys
        selected_value_columns = [v for _, v in self.keys_used]
        self.filtered_data['supervalue'] = self.filtered_data[selected_value_columns].astype(str).agg('_'.join, axis=1)

        # Drop the superkey column (it's only used for internal processing)
        self.filtered_data.drop(columns='superkey', inplace=True)

        unique_superkeys = self.filtered_data['supervalue'].nunique()
        QMessageBox.information(self, "Superkeys Generated",
                                f"Total Unique Superkeys: {unique_superkeys}")

    def select_columns_to_display(self):
        if self.filtered_data is None:
            QMessageBox.warning(self, "No Superkey", "Superkey has not been generated.")
            return

        dialog = ColumnSelectionDialog(self.key, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_indices = dialog.selected_columns
            self.selected_columns = [(self.key[idx], self.value[idx]) for idx in selected_indices]
            if not self.selected_columns:
                QMessageBox.warning(self, "No Columns", "No columns selected to display.")
                return
            self.display_table()

    def display_table(self):
        # Extract columns that correspond to the selected keys
        columns_to_display = [v_col for _, v_col in self.selected_columns]

        # Initialize a DataFrame to hold the table data
        table_data = pd.DataFrame(index=self.filtered_data.index)

        # Populate the table with values dependent on both the superkey and selected columns
        for key_name, value_col in self.selected_columns:
            if value_col in self.filtered_data.columns:
                table_data[key_name] = self.filtered_data[value_col]

        # Add the supervalue column as the first column
        table_data.insert(0, 'Supervalue', self.filtered_data['supervalue'])

        # Display the table in QTableWidget
        self.populate_table_widget(table_data)

    def sort_data(self):
        # Ensure the table has data to sort
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "Please load data and generate superkeys before sorting.")
            return

        # Prompt for the column to sort
        column_names = ['Supervalue'] + [k for k, _ in self.selected_columns]
        column_index, ok = QInputDialog.getItem(self, "Select Column to Sort", "Column:", column_names, 0, False)
        if not ok:
            return

        # Prompt for sorting order (Min/Max)
        order, ok = QInputDialog.getItem(self, "Select Sort Order", "Order:", ["Min", "Max"], 0, False)
        if not ok:
            return

        # Convert the selected column name to its corresponding DataFrame column
        if column_index == 'Supervalue':
            sort_column = 'supervalue'
        else:
            sort_column = self.selected_columns[column_names.index(column_index) - 1][
                1]  # Adjust index for actual column

        # Sort the DataFrame based on the selected column and order
        if order == "Min":
            self.filtered_data.sort_values(by=sort_column, ascending=True, inplace=True)  # Ascending order
        elif order == "Max":
            self.filtered_data.sort_values(by=sort_column, ascending=False, inplace=True)  # Descending order

        # Refresh the displayed table to reflect the sorted data
        self.display_table()

    def populate_table_widget(self, data):
        self.table.clear()
        self.table.setRowCount(data.shape[0])
        self.table.setColumnCount(data.shape[1])
        self.table.setHorizontalHeaderLabels(data.columns)

        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(data.iat[i, j])))
        supervalue_column_index = data.columns.get_loc('Supervalue')
        self.table.setColumnWidth(supervalue_column_index, 300)

    def save_to_csv(self):
        # Extract data from the table to a pandas DataFrame
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()

        if row_count == 0 or col_count == 0:
            QMessageBox.warning(self, "No Data", "No data available to save.")
            return

        # Create a DataFrame from the table's displayed data
        table_data = []
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(col_count)]

        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.table.item(row, col)
                row_data.append(item.text() if item is not None else "")
            table_data.append(row_data)

        # Convert to DataFrame
        df = pd.DataFrame(table_data, columns=headers)

        # Save the DataFrame to a CSV file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            try:
                df.to_csv(file_path, index=False)
                QMessageBox.information(self, "File Saved", f"Data successfully saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save CSV file.\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
