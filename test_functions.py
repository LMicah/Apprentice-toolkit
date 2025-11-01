import pandas as pd
from io import StringIO
from functions import split_tire_service, work_logs, get_equipment_and_plan, fetch_plans, get_equipment_items
import pytest

# Test data provided by the user
data1 = """N	S		15	15	1	11	Engraxar / Lubrificar	Lubrifcar os pontos de graxa (quinta-roda, catracas, rala, etc).	2400	Lab.Lub / Comboio	2402	Lubrificação	999396	Graxa
N	S		15	15	2	48	Calibrar	Calibrar pneus e verificar vazamentos.	700	Transmissão/Cubos Red.	773	Pneu	1	SERVIÇO
N	S		15	15	3	10	Reapertar	Reapertar porca dos parafusos da rodas, verificar faltantes e substituir se necessário.	700	Transmissão/Cubos Red.	774	Roda	1	SERVIÇO
N	S		15	15	4	16	Verificar / Testar	Conferir número de fogo, posição e pneu faltante conforme dados da ultima montagem em OS e verificar integridade dos pneus.	700	Transmissão/Cubos Red.	773	Pneu	1	SERVIÇO
N	S		15	15	5	56	Medir	Medir sulcos.	700	Transmissão/Cubos Red.	773	Pneu	1	SERVIÇO
N	S		15	15	6	81	Inspecionar 	Inspecionar região da pista com aro (roda) utilizando calibre de folga. Se encontrar folga abrir OS para tratativa.	700	Transmissão/Cubos Red.	774	Roda	1	SERVIÇO
N	S		15	15	7	11	Engraxar / Lubrificar	Verificar nível de óleo do sistema hidráulico.	1700	Estrutura / Chassis	1782	Tanque hidráulico	999655	Óleo lubrificante sistema hidráulico
N	S		45	45	8	4	Revisar	Abrir tampa de TODOS os cubos. Verificar o travamento da trava aranha e condição da graxa. Substituir se necessário.	700	Transmissão/Cubos Red.	750	Cubo de roda	999583	Tampa
N	S		45	45	9	16	Verificar / Testar	Verificar presença de folga de TODOS os cubos. Caso haja, remover rodado e verificar as condições do eixo/rolamento/cubo. Trocar trava/graxa/retentor.	700	Transmissão/Cubos Red.	750	Cubo de roda	1	SERVIÇO
N	S		45	45	10	16	Verificar / Testar	Verificar presença de vazamentos na tampa do cubo e na parte interna do flip de roda.	700	Transmissão/Cubos Red.	750	Cubo de roda	999583	Tampa
N	S		45	45	11	16	Verificar / Testar	MSS - Verificar a integridade (trincas, desgastes acentuados, danos críticos) dos espelhos da roda . Trocar se necessário.	700	Transmissão/Cubos Red.	774	Roda	999343	Espelho
N	S		45	45	12	1	Regular	MSS - Verificar desgaste dos pneus e regular convergência e reapertar parafusos.	700	Transmissão/Cubos Red.	773	Pneu	999505	Pneu - Peças
N	S		45	45	13	16	Verificar / Testar	MSS - Verificar a pressão, medir sulcos, conferir número de fogo e verificar emparelhamento dos pneus	700	Transmissão/Cubos Red.	773	Pneu	999505	Pneu - Peças
"""

data2 = """N	S		2500	2500	1	11	Engraxar / Lubrificar	Lubrificar o equipamento e verificar todos os níveis de oleo e fluidos	2400	Lab.Lub / Comboio	2402	Lubrificação	999396	Graxa
N	S		2500	2500	2	48	Calibrar	Calibrar pneus e verificar vazamentos	700	Transmissão/Cubos Red.	773	Pneu	1	SERVIÇO
N	S		2500	2500	3	10	Reapertar	Reapertar porca dos parafusos das rodas, verificar faltantes e substituir se necessário	700	Transmissão/Cubos Red.	774	Roda	1	SERVIÇO
N	S		2500	2500	4	16	Verificar / Testar	Conferir número de fogo, posição e pneu faltante conforme dados da ultima montagem em OS e verificar integridades dos pneus.	700	Transmissão/Cubos Red.	773	Pneu	1	SERVIÇO
N	S		2500	2500	5	56	Medir	Medir sulcos dos pneus	700	Transmissão/Cubos Red.	773	Pneu	1	SERVIÇO
N	S		2500	2500	6	11	Engraxar / Lubrificar	Verificar nível do óleo do motor e se necessário, remontar.	100	Motor	103	Subsistema lubrificação	999652	Óleo lubrificante motor
"""

data3 = """N	S	365	365	20	Lavar / Limpar	Lavagem do equipamento	4700	Lavagem Equipamento	4701	Lavagem Equipamento	1	SERVIÇO
N	S	365	365	117	Diagnostico	Testes e verificações (hidráulicos, elétricos, códigos de falha, teste de estanqueidade admissão e arrefecimento, teste de compressão do motor).	6000	Diagnóstico 	6000	Diagnóstico 	1	SERVIÇO
"""

def test_split_tire_service_data1():
    df = pd.read_csv(StringIO(data1), sep='\t', header=None, engine='python')
    df = df.reset_index()
    df["index"] = df["index"] + 1
    tire_services, general_services = split_tire_service(df)
    expected_tire_services = [2, 3, 4, 5, 6, 11, 12, 13]
    assert sorted(tire_services) == sorted(expected_tire_services)

def test_split_tire_service_data2():
    df = pd.read_csv(StringIO(data2), sep='\t', header=None, engine='python')
    df = df.reset_index()
    df["index"] = df["index"] + 1
    tire_services, general_services = split_tire_service(df)
    expected_tire_services = [2, 3, 4, 5]
    assert sorted(tire_services) == sorted(expected_tire_services)

def test_split_tire_service_data3():
    df = pd.read_csv(StringIO(data3), sep='\t', header=None, engine='python')
    df = df.reset_index()
    df["index"] = df["index"] + 1
    tire_services, general_services = split_tire_service(df)
    expected_tire_services = []
    assert sorted(tire_services) == sorted(expected_tire_services)


def test_work_logs_success():
    expected_output = (
        "62112345\t\t\t1\t\t\t\t\t\t\t\t\t\t01/01/2025\t08:00\t01/01/2025\t08:12\t0,20\n"
        "62112345\t\t\t2\t\t\t\t\t\t\t\t\t\t01/01/2025\t08:12\t01/01/2025\t08:24\t0,20\n"
        "62112345\t\t\t3\t\t\t\t\t\t\t\t\t\t01/01/2025\t08:24\t01/01/2025\t08:36\t0,20\n"
        "62112345\t\t\t4\t\t\t\t\t\t\t\t\t\t01/01/2025\t08:36\t01/01/2025\t08:48\t0,20\n"
        "62112345\t\t\t5\t\t\t\t\t\t\t\t\t\t01/01/2025\t08:48\t01/01/2025\t09:00\t0,20\n"
    )
    result = work_logs("62112345", "1-5", "01/01/2025", "08:00", "09:00")
    assert result == expected_output


def test_work_logs_no_service_order():
    with pytest.raises(ValueError, match="Por favor, insira uma ordem de serviço"):
        work_logs("", "1-5", "01/01/2025", "08:00", "09:00")

def test_work_logs_invalid_date():
    with pytest.raises(ValueError, match="Por favor, insira uma data válida."):
        work_logs("62112345", "1-5", "invalid-date", "08:00", "09:00")

def test_work_logs_invalid_time():
    with pytest.raises(ValueError, match="Por favor, insira um intervalo de tempo válido."):
        work_logs("62112345", "1-5", "01/01/2025", "invalid-time", "09:00")

def test_get_equipment_and_plan():
    data = {'O.S': ['123456'], 'MODELO': ['TEST-MODEL'], 'PLANO': ['PLAN-A/PLAN-B']}
    df_os = pd.DataFrame(data)
    equipment, plan = get_equipment_and_plan("123456", df_os)
    assert equipment == "TEST-MODEL"
    assert plan == ["PLAN-A", "PLAN-B"]

def test_fetch_plans():
    data = {
        'Chave': ['TEST-EQUIP10N', 'TEST-EQUIP20N'],
        'no_ref_prog': [10, 20],
        'fg_garantia': ['N', 'N'],
        'de_tp_manut': ['LUB', 'MECHANICAL'],
        'no_seq': [1, 2],
        'de_operacao': ['op1', 'op2'],
        'de_tarefa': ['task1', 'task2'],
        'de_sist_veic': ['sys1', 'sys2'],
        'de_sub_sist': ['sub1', 'sub2'],
        'de_compo': ['comp1', 'comp2']
    }
    df_matrix = pd.DataFrame(data)
    df = fetch_plans("TEST-EQUIP", ["10"], df_matrix)
    assert len(df) == 1
    assert df.iloc[0]['no_seq'] == 1

def test_get_equipment_items():
    bd_filters_data = {'FROTA': [123], 'Cod. Sap': ['SAP123'], 'PLANO REAL': ['plan'], 'Tipo da peça': ['filter'], 'Texto breve material': ['material'], 'Tipo de MRP': ['mrp'], 'QNTD.': [1]}
    stock_data = {'Material': ['SAP123'], 'Utilização livre': [10]}
    itens_prices_data = {'Material': ['SAP123'], 'Valor': [99.99]}

    bd_filters = pd.DataFrame(bd_filters_data)
    stock = pd.DataFrame(stock_data)
    itens_prices = pd.DataFrame(itens_prices_data)

    # Correctly structure the equipment_items DataFrame
    equipment_items = bd_filters[bd_filters['FROTA'] == 123]

    df = get_equipment_items(123, bd_filters, stock, itens_prices)
    assert len(df) == 1
    assert df.iloc[0]['Cod. Sap'] == 'SAP123'
