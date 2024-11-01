import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QListWidget, QLabel, QLineEdit
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import stats
from sklearn.linear_model import LinearRegression

class DataVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Energy Data Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self.df = pd.read_csv('data.csv')
        self.df['Año'] = pd.to_datetime(self.df['Año'], format='%Y')

        # Convertir unidades de energía (kbep a gigajulios, 1 kbep = 41.868 GJ)
        self.df['Cantidad_GJ'] = self.df['Cantidad'] * 41.868

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        font_size_style = """
        QComboBox, QPushButton, QListWidget, QLabel, QLineEdit {
            font-size: 18px;
        }
    """
        # Filtros
        self.subsistema_combo = QComboBox()
        self.subsistema_combo.addItems(self.df['Subsystem'].unique())
        self.subsistema_combo.setStyleSheet(font_size_style)

        self.energetico_combo = QComboBox()
        self.energetico_combo.addItems(self.df['Energetic'].unique())
        self.energetico_combo.setStyleSheet(font_size_style)

        self.variable_combo = QComboBox()
        self.update_variable_options()  # Actualizar las variables según subsistema y energético seleccionados
        self.variable_combo.setStyleSheet(font_size_style)


        # Selector de unidad de energía
         # Selector de unidad de energía
        self.energy_unit_combo = QComboBox()
        self.energy_unit_combo.addItems(['kboe', 'Gigajoules '])
        self.energy_unit_combo.setStyleSheet(font_size_style)

        self.selected_vars_list = QListWidget()
        self.selected_vars_list.setStyleSheet(font_size_style)

        self.add_var_button = QPushButton("Add Variable")
        self.add_var_button.setStyleSheet(font_size_style)
        
        self.remove_var_button = QPushButton("Remove Variable")
        self.remove_var_button.setStyleSheet(font_size_style)
        
        self.plot_button = QPushButton("Graph data")
        self.plot_button.setStyleSheet(font_size_style)
        
        self.predict_button = QPushButton("Predict")
        self.predict_button.setStyleSheet(font_size_style)

        # Campos para rangos
        self.x_min_input = QLineEdit()
        self.x_min_input.setStyleSheet(font_size_style)
        
        self.x_max_input = QLineEdit()
        self.x_max_input.setStyleSheet(font_size_style)
        
        self.y_min_input = QLineEdit()
        self.y_min_input.setStyleSheet(font_size_style)
        
        self.y_max_input = QLineEdit()
        self.y_max_input.setStyleSheet(font_size_style)

        # Campos para predicción
        self.prediction_years_input = QLineEdit()
        self.prediction_years_input.setPlaceholderText("years of prediction")
        self.prediction_years_input.setStyleSheet(font_size_style)

        # Canvas para el gráfico
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        # Etiquetas para estadísticas
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(font_size_style)

        # Conectar señales
        self.subsistema_combo.currentIndexChanged.connect(self.update_variable_options)
        self.energetico_combo.currentIndexChanged.connect(self.update_variable_options)
        self.energy_unit_combo.currentIndexChanged.connect(self.plot_data)

    def create_layout(self):
        font_size_style = """
        QComboBox, QPushButton, QListWidget, QLabel, QLineEdit {
            font-size: 16px;
        }
    """

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Layout izquierdo (controles)
        left_layout = QVBoxLayout()
        
        subsistema_label = QLabel("Subsystem:")
        subsistema_label.setStyleSheet(font_size_style)
        left_layout.addWidget(subsistema_label)
        left_layout.addWidget(self.subsistema_combo)
        
        energetico_label = QLabel("Energy Type:")
        energetico_label.setStyleSheet(font_size_style)
        left_layout.addWidget(energetico_label)
        left_layout.addWidget(self.energetico_combo)
        
        variable_label = QLabel("Variable:")
        variable_label.setStyleSheet(font_size_style)
        left_layout.addWidget(variable_label)
        left_layout.addWidget(self.variable_combo)
        
        unidad_energia_label = QLabel("Unit of energy:")
        unidad_energia_label.setStyleSheet(font_size_style)
        left_layout.addWidget(unidad_energia_label)
        left_layout.addWidget(self.energy_unit_combo)
        
        self.add_var_button.setStyleSheet(font_size_style)
        left_layout.addWidget(self.add_var_button)
        
        variables_seleccionadas_label = QLabel("Selected variables:")
        variables_seleccionadas_label.setStyleSheet(font_size_style)
        left_layout.addWidget(variables_seleccionadas_label)
        left_layout.addWidget(self.selected_vars_list)
        
        self.remove_var_button.setStyleSheet(font_size_style)
        left_layout.addWidget(self.remove_var_button)
        
        rango_x_label = QLabel("Range X (Year):")
        rango_x_label.setStyleSheet(font_size_style)
        left_layout.addWidget(rango_x_label)
        left_layout.addWidget(self.x_min_input)
        left_layout.addWidget(self.x_max_input)
        
        rango_y_label = QLabel("Rango Y:")
        rango_y_label.setStyleSheet(font_size_style)
        left_layout.addWidget(rango_y_label)
        left_layout.addWidget(self.y_min_input)
        left_layout.addWidget(self.y_max_input)
        
        self.plot_button.setStyleSheet(font_size_style)
        left_layout.addWidget(self.plot_button)
        
        prediccion_label = QLabel("Years of prediction:")
        prediccion_label.setStyleSheet(font_size_style)
        left_layout.addWidget(prediccion_label)
        left_layout.addWidget(self.prediction_years_input)
        
        self.predict_button.setStyleSheet(font_size_style)
        left_layout.addWidget(self.predict_button)
        
        left_layout.addStretch()

        # Layout derecho (gráfico y estadísticas)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.canvas)
        right_layout.addWidget(self.stats_label)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Conectar señales
        self.add_var_button.clicked.connect(self.add_variable)
        self.remove_var_button.clicked.connect(self.remove_variable)
        self.plot_button.clicked.connect(self.plot_data)
        self.predict_button.clicked.connect(self.predict_data)

    def update_variable_options(self):
        subsistema = self.subsistema_combo.currentText()
        energetico = self.energetico_combo.currentText()
        filtered_df = self.df[(self.df['Subsystem'] == subsistema) & (self.df['Energetic'] == energetico)]
        available_variables = filtered_df['Variable'].unique()
        self.variable_combo.clear()
        self.variable_combo.addItems(available_variables)

    def add_variable(self):
        subsistema = self.subsistema_combo.currentText()
        energetico = self.energetico_combo.currentText()
        variable = self.variable_combo.currentText()
        self.selected_vars_list.addItem(f"{subsistema} - {energetico} - {variable}")

    def remove_variable(self):
        current_item = self.selected_vars_list.currentItem()
        if current_item:
            self.selected_vars_list.takeItem(self.selected_vars_list.row(current_item))

    def plot_data(self):
        self.ax.clear()
        energy_unit = self.energy_unit_combo.currentText()

        for i in range(self.selected_vars_list.count()):
            var = self.selected_vars_list.item(i).text().split(" - ")
            data = self.df[(self.df['Subsystem'] == var[0]) &
                           (self.df['Energetic'] == var[1]) &
                           (self.df['Variable'] == var[2])]

            if energy_unit == 'Gigajulios':
                self.ax.plot(data['Año'], data['Cantidad_GJ'], label=f"{var[1]} - {var[2]}")
            else:
                self.ax.plot(data['Año'], data['Cantidad'], label=f"{var[1]} - {var[2]}")

        self.ax.set_xlabel('year')
        self.ax.set_ylabel('Quantity (kboe)' if energy_unit == 'kboe' else 'Quantity (GigaJoules)')
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)  # Leyenda en la parte superior
        self.ax.grid(True)

        # Ajustar rangos si se especifican
        if self.x_min_input.text() and self.x_max_input.text():
            self.ax.set_xlim(pd.to_datetime(self.x_min_input.text()),
                             pd.to_datetime(self.x_max_input.text()))
        if self.y_min_input.text() and self.y_max_input.text():
            self.ax.set_ylim(float(self.y_min_input.text()),
                             float(self.y_max_input.text()))

        self.canvas.draw()

        # Calcular y mostrar estadísticas
        self.calculate_stats()

    def calculate_stats(self):
        stats_text = "<b>Statistics:</b><br>"

        if self.selected_vars_list.count() > 1:
            # Preparar datos para correlación
            data_list = []
            var_names = []
            for i in range(self.selected_vars_list.count()):
                var = self.selected_vars_list.item(i).text().split(" - ")
                data = self.df[(self.df['Subsystem'] == var[0]) &
                               (self.df['Energetic'] == var[1]) &
                               (self.df['Variable'] == var[2])]
                if self.energy_unit_combo.currentText() == 'Gigajulios':
                    data_list.append(data['Cantidad_GJ'].values)
                else:
                    data_list.append(data['Cantidad'].values)
                var_names.append(f"{var[1]} - {var[2]}")

            # Asegurar que todas las listas tengan la misma longitud
            min_length = min(len(l) for l in data_list)
            data_list = [l[:min_length] for l in data_list]

            if len(data_list) == 2 and min_length > 1:
                corr_matrix = np.corrcoef(data_list)
                stats_text += f"Correlation: {corr_matrix[0][1]:.2f}<br>"
            elif len(data_list) > 2 and min_length > 1:
                corr_matrix = np.corrcoef(data_list)
                stats_text += "<b>Correlation Matrix:</b><br>"
                df_corr = pd.DataFrame(corr_matrix, index=var_names, columns=var_names)
                stats_text += df_corr.to_html().replace('<table border="1" class="dataframe">', '<table border="1" class="dataframe" style="border-collapse: collapse; width: 100%;">')
            else:
                stats_text += "Not enough data to make a correlation.<br>"

        self.stats_label.setText(stats_text)

    def predict_data(self):
        self.ax.clear()
        energy_unit = self.energy_unit_combo.currentText()
        prediction_years = int(self.prediction_years_input.text())

        for i in range(self.selected_vars_list.count()):
            var = self.selected_vars_list.item(i).text().split(" - ")
            data = self.df[(self.df['Subsystem'] == var[0]) &
                           (self.df['Energetic'] == var[1]) &
                           (self.df['Variable'] == var[2])]

            if energy_unit == 'Gigajulios':
                y = data['Cantidad_GJ'].values
            else:
                y = data['Cantidad'].values

            X = np.array(data['Año'].map(pd.Timestamp.toordinal)).reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y)

            future_years = pd.date_range(data['Año'].max(), periods=prediction_years + 1, freq='Y')
            future_X = np.array(future_years.map(pd.Timestamp.toordinal)).reshape(-1, 1)
            future_y = model.predict(future_X)

            self.ax.plot(data['Año'], y, label=f"{var[1]} - {var[2]}")
            self.ax.plot(future_years, future_y, '--', label=f"Predicción {var[1]} - {var[2]}")

        self.ax.set_xlabel('Año')
        self.ax.set_ylabel('Cantidad (kboe)' if energy_unit == 'kboe' else 'Cantidad (Gigajulios)')
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)  # Leyenda en la parte superior
        self.ax.grid(True)

        # Ajustar rangos si se especifican
        if self.x_min_input.text() and self.x_max_input.text():
            self.ax.set_xlim(pd.to_datetime(self.x_min_input.text()),
                             pd.to_datetime(self.x_max_input.text()))
        if self.y_min_input.text() and self.y_max_input.text():
            self.ax.set_ylim(float(self.y_min_input.text()),
                             float(self.y_max_input.text()))

        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DataVisualizerApp()
    ex.show()
    sys.exit(app.exec_())