# src/main.py
#%%

# import sys 

# sys.path.append("src")
# from moises.interface.Frontend.gui import start_gui
# from moises.interface.Backend.logic import start_logic


from src.moises.interface.Frontend.gui import start_gui
from src.moises.interface.Backend.logic import start_logic


def main():
    # Inicializa la lógica del backend
    start_logic()

    # Inicia la interfaz gráfica
    start_gui()


if __name__ == "__main__":
    main()

# %%
