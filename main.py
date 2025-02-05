# src/main.py
from Frontend.gui import start_gui
from Backend.logic import start_logic


def main():
    # Inicializa la lógica del backend
    start_logic()

    # Inicia la interfaz gráfica
    start_gui()


if __name__ == "__main__":
    main()
