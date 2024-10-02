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
        self.setWindowTitle("Visualizador de Datos Energéticos")
        self.setGeometry(100, 100, 1200, 800)

        # Cargar datos
        self.df = pd.read_csv('datos.csv')
        self.df['Año'] = pd.to_datetime(self.df['Año'], format='%Y')

        # Convertir unidades de energía (kbep a gigajulios, 1 kbep = 41.868 GJ)
        self.df['Cantidad_GJ'] = self.df['Cantidad'] * 41.868

        # Crear widgets
        self.create_widgets()

        # Crear layout
        self.create_layout()

    def create_widgets(self):
        # Filtros
        self.subsistema_combo = QComboBox()
        self.subsistema_combo.addItems(self.df['Subsistema'].unique())
        self.energetico_combo = QComboBox()
        self.energetico_combo.addItems(self.df['Energetico'].unique())
        self.variable_combo = QComboBox()
        self.update_variable_options()  # Actualizar las variables según subsistema y energético seleccionados

        # Selector de unidad de energía
        self.energy_unit_combo = QComboBox()
        self.energy_unit_combo.addItems(['kbep', 'Gigajulios'])

        # Lista de variables seleccionadas
        self.selected_vars_list = QListWidget()

        # Botones
        self.add_var_button = QPushButton("Añadir Variable")
        self.remove_var_button = QPushButton("Quitar Variable")
        self.plot_button = QPushButton("Graficar")
        self.predict_button = QPushButton("Predecir")

        # Campos para rangos
        self.x_min_input = QLineEdit()
        self.x_max_input = QLineEdit()
        self.y_min_input = QLineEdit()
        self.y_max_input = QLineEdit()

        # Campos para predicción
        self.prediction_years_input = QLineEdit()
        self.prediction_years_input.setPlaceholderText("Años de predicción")

        # Canvas para el gráfico
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        # Etiquetas para estadísticas
        self.stats_label = QLabel()

        # Conectar señales
        self.subsistema_combo.currentIndexChanged.connect(self.update_variable_options)
        self.energetico_combo.currentIndexChanged.connect(self.update_variable_options)
        self.energy_unit_combo.currentIndexChanged.connect(self.plot_data)

    def create_layout(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Layout izquierdo (controles)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Subsistema:"))
        left_layout.addWidget(self.subsistema_combo)
        left_layout.addWidget(QLabel("Energético:"))
        left_layout.addWidget(self.energetico_combo)
        left_layout.addWidget(QLabel("Variable:"))
        left_layout.addWidget(self.variable_combo)
        left_layout.addWidget(QLabel("Unidad de Energía:"))
        left_layout.addWidget(self.energy_unit_combo)
        left_layout.addWidget(self.add_var_button)
        left_layout.addWidget(QLabel("Variables Seleccionadas:"))
        left_layout.addWidget(self.selected_vars_list)
        left_layout.addWidget(self.remove_var_button)
        left_layout.addWidget(QLabel("Rango X (Año):"))
        left_layout.addWidget(self.x_min_input)
        left_layout.addWidget(self.x_max_input)
        left_layout.addWidget(QLabel("Rango Y:"))
        left_layout.addWidget(self.y_min_input)
        left_layout.addWidget(self.y_max_input)
        left_layout.addWidget(self.plot_button)
        left_layout.addWidget(QLabel("Años de predicción:"))
        left_layout.addWidget(self.prediction_years_input)
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
        filtered_df = self.df[(self.df['Subsistema'] == subsistema) & (self.df['Energetico'] == energetico)]
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
            data = self.df[(self.df['Subsistema'] == var[0]) &
                           (self.df['Energetico'] == var[1]) &
                           (self.df['Variable'] == var[2])]

            if energy_unit == 'Gigajulios':
                self.ax.plot(data['Año'], data['Cantidad_GJ'], label=f"{var[1]} - {var[2]}")
            else:
                self.ax.plot(data['Año'], data['Cantidad'], label=f"{var[1]} - {var[2]}")

        self.ax.set_xlabel('Año')
        self.ax.set_ylabel('Cantidad (kbep)' if energy_unit == 'kbep' else 'Cantidad (Gigajulios)')
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
        stats_text = "Estadísticas:\n"

        if self.selected_vars_list.count() > 1:
            # Preparar datos para correlación
            data_list = []
            for i in range(self.selected_vars_list.count()):
                var = self.selected_vars_list.item(i).text().split(" - ")
                data = self.df[(self.df['Subsistema'] == var[0]) &
                               (self.df['Energetico'] == var[1]) &
                               (self.df['Variable'] == var[2])]
                if self.energy_unit_combo.currentText() == 'Gigajulios':
                    data_list.append(data['Cantidad_GJ'].values)
                else:
                    data_list.append(data['Cantidad'].values)

            # Asegurar que todas las listas tengan la misma longitud
            min_length = min(len(l) for l in data_list)
            data_list = [l[:min_length] for l in data_list]

            if len(data_list) > 1 and min_length > 1:
                corr_matrix = np.corrcoef(data_list)
                stats_text += f"Correlación: {corr_matrix[0][1]:.2f}\n"
            else:
                stats_text += "No hay suficientes datos para calcular la correlación.\n"

        self.stats_label.setText(stats_text)

    def predict_data(self):
        self.ax.clear()
        energy_unit = self.energy_unit_combo.currentText()
        prediction_years = int(self.prediction_years_input.text())

        for i in range(self.selected_vars_list.count()):
            var = self.selected_vars_list.item(i).text().split(" - ")
            data = self.df[(self.df['Subsistema'] == var[0]) &
                           (self.df['Energetico'] == var[1]) &
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
        self.ax.set_ylabel('Cantidad (kbep)' if energy_unit == 'kbep' else 'Cantidad (Gigajulios)')
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