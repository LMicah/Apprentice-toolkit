import pandas as pd

class DataManager:
    """A class to manage loading and accessing application data."""
    def __init__(self):
        self.df_matrix = None
        self.df_os = None
        self.bd_filters = None
        self.stock = None
        self.itens_prices = None
        self.load_data()

    def load_data(self):
        """Loads all the necessary data files into pandas DataFrames."""
        try:
            self.df_matrix = pd.read_csv("matriz.csv", sep=";", encoding="latin1", low_memory=False)
            self.df_os = pd.read_csv("os.csv", sep=";", encoding="latin1", low_memory=False)
            self.bd_filters = pd.read_excel("planilha.xlsx", sheet_name="BD_FILTROS")
            self.stock = pd.read_excel("planilha.xlsx", sheet_name="Saldo Almoxarifado")
            self.itens_prices = pd.read_excel("planilha.xlsx", sheet_name="Valor das peças")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error loading data file: {e}. Please ensure all required files are present.")
