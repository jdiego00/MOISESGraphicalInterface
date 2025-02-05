import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

# Definir los alcances de la API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# ID del Spreadsheet y el rango de la hoja que deseas leer
SPREADSHEET_ID = "1FpUP2Inv1lmH4M1JYst3SBC19xv0P8GFyWvcJEMdFzY"
RANGE_NAME = "Data!A1:AO2749"

def clean_number(value):
    """Limpia y convierte strings numéricos a float y los transforma en positivos."""
    if pd.isna(value) or value == '-':
        return None
    if isinstance(value, (int, float)):
        return abs(float(value))
    if isinstance(value, str):
        # Reemplazar comas por puntos si existen
        value = value.replace(',', '.')
        
        # Si tiene múltiples puntos, asumimos que es formato de miles
        if value.count('.') > 1:
            parts = value.rsplit('.', 1)  # Divide desde la derecha, conservando el último punto
            value = parts[0].replace('.', '') + '.' + parts[1]  # Elimina puntos intermedios
        
        try:
            return abs(float(value))
        except ValueError:
            print(f"No se pudo convertir el valor: {value}")
            return None
    return None

def transform_google_sheet_data_to_df(values):
    # Asumimos que la primera fila de la matriz es el encabezado
    headers = values[0]
    data_rows = values[1:]

    # Crear un DataFrame con los datos de Google Sheets
    df = pd.DataFrame(data_rows, columns=headers)

    # Identificar las columnas que son años
    year_columns = [col for col in df.columns if str(col).isdigit()]

    # Identificar las columnas que no son años (metadata)
    metadata_columns = [col for col in df.columns if col not in year_columns]

    # Crear el nuevo DataFrame transformado
    rows_list = []
    for _, row in df.iterrows():
        metadata = row[metadata_columns].to_dict()
        for year in year_columns:
            value = row[year]
            cleaned_value = clean_number(value)
            if cleaned_value is not None:
                new_row = {
                    'Subsistema': metadata.get('Subsystem', ''),
                    'Energetico': metadata.get('Energy type', ''),
                    'Variable': metadata.get('Variable', ''),
                    'UnidadDeMedida': metadata.get('Unit', ''),
                    'Año': year,
                    'Cantidad': cleaned_value
                }
                rows_list.append(new_row)
    
    transformed_df = pd.DataFrame(rows_list)

    # Eliminar filas incompletas en las columnas especificadas
    transformed_df = transformed_df.dropna(subset=['Subsistema', 'Energetico', 'Variable', 'UnidadDeMedida', 'Año', 'Cantidad'])

    # Ordenar por Subsistema, Energetico, Variable y Año
    transformed_df = transformed_df.sort_values(['Subsistema', 'Energetico', 'Variable', 'Año'])
    return transformed_df

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get("values", [])

        if not values:
            print("No se encontraron datos en la hoja.")
            return

        # Transformar la matriz de Google Sheets al formato deseado
        transformed_df = transform_google_sheet_data_to_df(values)
        print("Transformación completada. Primeras filas del resultado:")
        print(transformed_df.head())

        # Guardar en un archivo CSV si es necesario
        transformed_df.to_csv("data.csv", index=False)
        df = pd.read_csv('data.csv')

        # Eliminar filas con datos incompletos
        df_cleaned = df.dropna()

        # Guardar el DataFrame limpio en un nuevo archivo CSV
        df_cleaned.to_csv('data.csv', index=False)

    except HttpError as error:
        print(f"Ocurrió un error: {error}")

def start_logic():
    main()
