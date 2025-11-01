import pandas as pd
import pytest
from functions import get_equipment_and_plan, fetch_plans, get_equipment_items

@pytest.fixture
def mock_df_os():
    data = {'O.S': ['62112345', '62154321'],
            'MODELO': ['MODEL_A', 'MODEL_B'],
            'PLANO': ['PLAN1/PLAN2', 'PLAN3']}
    return pd.DataFrame(data)

@pytest.fixture
def mock_df_matrix():
    data = {'Chave': ['MODEL_A1N', 'MODEL_A2N', 'MODEL_B3N'],
            'no_ref_prog': [1, 2, 3],
            'fg_garantia': ['N', 'N', 'N'],
            'de_tp_manut': ['LUB', 'MEP', 'MEP'],
            'no_seq': [1, 2, 3],
            'de_operacao': ['OP1', 'OP2', 'OP3'],
            'de_tarefa': ['TASK1', 'TASK2', 'TASK3'],
            'de_sist_veic': ['SYS1', 'SYS2', 'SYS3'],
            'de_sub_sist': ['SUB1', 'SUB2', 'SUB3'],
            'de_compo': ['COMP1', 'COMP2', 'COMP3']}
    return pd.DataFrame(data)

@pytest.fixture
def mock_bd_filters():
    data = {'FROTA': [101, 102],
            'Cod. Sap': [123, 456]}
    return pd.DataFrame(data)

@pytest.fixture
def mock_stock():
    data = {'Material': [123, 456],
            'Utilização livre': [10, 20]}
    return pd.DataFrame(data)

@pytest.fixture
def mock_itens_prices():
    data = {'Material': [123, 456],
            'PLANO REAL': [9.99, 19.99],
            'Tipo da peça': ['FILTRO', 'OLEO'],
            'Texto breve material': ['FILTRO DE AR', 'OLEO DE MOTOR'],
            'Tipo de MRP': ['MRP1', 'MRP2'],
            'QNTD.': [1, 5]}
    return pd.DataFrame(data)


def test_get_equipment_and_plan_found(mock_df_os):
    equipment, plan = get_equipment_and_plan('62112345', mock_df_os)
    assert equipment == 'MODEL_A'
    assert plan == ['PLAN1', 'PLAN2']

def test_get_equipment_and_plan_not_found(mock_df_os):
    equipment, plan = get_equipment_and_plan('99999999', mock_df_os)
    assert not equipment
    assert not plan

def test_fetch_plans_found(mock_df_matrix):
    df = fetch_plans('MODEL_A', ['1', '2'], mock_df_matrix)
    assert not df.empty
    assert len(df) == 2

def test_fetch_plans_not_found(mock_df_matrix):
    df = fetch_plans('MODEL_C', ['4'], mock_df_matrix)
    assert df.empty

def test_get_equipment_items_found(mock_bd_filters, mock_stock, mock_itens_prices):
    df = get_equipment_items(101, mock_bd_filters, mock_stock, mock_itens_prices)
    assert not df.empty
    assert len(df) == 1
    assert df['Cod. Sap'].iloc[0] == 123

def test_get_equipment_items_not_found(mock_bd_filters, mock_stock, mock_itens_prices):
    with pytest.raises(ValueError, match="Por favor, insira uma frota válida"):
        get_equipment_items(999, mock_bd_filters, mock_stock, mock_itens_prices)

def test_get_equipment_items_no_choice(mock_bd_filters, mock_stock, mock_itens_prices):
    with pytest.raises(ValueError, match="Por favor, insira uma frota"):
        get_equipment_items(None, mock_bd_filters, mock_stock, mock_itens_prices)
