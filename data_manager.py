import pandas as pd

class DataManager:
    def __init__(self):
        try:
            self.df_matrix = pd.read_csv("matriz.csv", sep=";", encoding="latin1", low_memory=False)
            self.df_os = pd.read_csv("os.csv", sep=";", encoding="latin1", low_memory=False)
            self.bd_filters = pd.read_excel("planilha.xlsx", sheet_name="BD_FILTROS")
            self.stock = pd.read_excel("planilha.xlsx", sheet_name="Saldo Almoxarifado")
            self.itens_prices = pd.read_excel("planilha.xlsx", sheet_name="Valor das peças")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"One of the required data files was not found: {e}")
