import pandas as pd
from io import StringIO
from functions import split_tire_service

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
N	S	365	365	6	Desmontar	Retirar o elevador da colhedora (recurso especial com Munck)\n	4300	Elevador	4301	Estrutura	1	SERVIÇO
N	S	365	365	6	Desmontar	Desmontar rolos de alimentação e transporte\n	4350	Trem de rolos	4353	Rolos	1	SERVIÇO
N	S	365	365	16	Verificar / Testar	Encavaletar o equipamento no box\n	1700	Estrutura / Chassis	1780	Estrutura	1	SERVIÇO
N	S	365	365	6	Desmontar	Desmontar truck (recurso especial com Munck) - Rodante\n	2000	Rodante	2008	Truck	1	SERVIÇO
N	S	365	365	16	Verificar / Testar	Verificar trincas no eixo através do Líquido Penetrante - Rodante\n	2000	Rodante	2032	Eixo Tranversal Truck	1	SERVIÇO
N	S	365	365	4	Revisar	Realizar regulagem de válvulas do motor\n	100	Motor	126	Bloco e cabeçote	999609	Valvula
N	S	365	365	75	Drenar	Remover e armazenar o líquido de arrefecimento do motor\n	200	Arrefecimento	247	Circuito de água	1	SERVIÇO
N	S	365	365	20	Lavar / Limpar	Realizar higienização dos radiadores\n	200	Arrefecimento	252	Quadro / estrutura	999532	Radiador
N	S	365	365	14	Trocar	Repor o líquido de arrefecimento (trocar se necessário) e realizar sangria do sistema\n	200	Arrefecimento	247	Circuito de água	999124	Aditivo
N	S	365	365	14	Trocar	Trocar terminais (Conector) - Faróis\n	4100	Cabine 	4102	Iluminação	1	SERVIÇO
N	S	365	365	16	Verificar / Testar	Verificar interruptores de posição - Alavanca Multifuncional\n	4100	Cabine 	4101	Painel de instrumentos 	1	SERVIÇO
N	S	365	365	100	Testar	Verificar interruptores de comando - Alavanca Multifuncional\n	4100	Cabine 	4101	Painel de instrumentos 	1	SERVIÇO
N	S	365	365	75	Drenar	Recolher o gás do sistema - Ar Condicionado\n	4100	Cabine 	4105	Ar condicionado	1	SERVIÇO
N	S	365	365	14	Trocar	Trocar mangueiras do compressor - Ar Condicionado\n	4100	Cabine 	4105	Ar condicionado	999445	Mangueira
N	S	365	365	20	Lavar / Limpar	Desmontar e limpar dutos, caixas e filtros - Ar Condicionado\n	4100	Cabine 	4105	Ar condicionado	1	SERVIÇO
N	S	365	365	16	Verificar / Testar	Fazer vácuo, aplicar o gás, testar a pressão - Ar Condicionado\n	4100	Cabine 	4105	Ar condicionado	1	SERVIÇO
N	S	365	365	16	Verificar / Testar	Verificar esguicho de água - Limpador de Parabrisa\n	4100	Cabine 	4107	Estrutura	999432	Limpador
N	S	365	365	6	Desmontar	Desmontar o corte de pontas\n	4150	Despontador/Triturador	4151	Estrutura	1	SERVIÇO
N	S	365	365	16	Verificar / Testar	Verificar espaçamento do divisor de linha (H)\n	4200	Divisor de linha	4201	Estrutura	1	SERVIÇO
N	S	365	365	6	Desmontar	Desmontar divisores de linha\n	4200	Divisor de linha	4201	Estrutura	1	SERVIÇO
N	S	365	365	80	Reparar	Reparar helicoides dos divisores de linha\n	4200	Divisor de linha	4201	Estrutura	1	SERVIÇO
N	S	365	365	80	Reparar	Reparar sapatas dos divisores de linha\n	4200	Divisor de linha	4201	Estrutura	999351	Estrutura
N	S	365	365	4	Revisar	Fazer embuchamento dos divisores de linha\n	4200	Divisor de linha	4201	Estrutura	1	SERVIÇO
N	S	365	365	14	Trocar	Trocar rolamentos dos divisores de linha\n	4200	Divisor de linha	4205	Mancais e acoplamentos	999554	Rolamento
N	S	365	365	4	Revisar	Fazer embuchamento das facas laterais dos divisores de linha\n	4200	Divisor de linha	4201	Estrutura	999322	Bucha
N	S	365	365	5	Montar	Montar divisores de linha\n	4200	Divisor de linha	4201	Estrutura	1	SERVIÇO
N	S	365	365	4	Revisar	Fazer embuchamento do corte de pontas\n	4150	Despontador/Triturador	4151	Estrutura	1	SERVIÇO
"""

def test_split_tire_service_data1():
    df = pd.read_csv(StringIO(data1), sep='\\t', header=None, engine='python')
    df = df.reset_index()
    df["index"] = df["index"] + 1
    tire_services, general_services = split_tire_service(df)
    expected_tire_services = [2, 3, 4, 5, 6, 11, 12, 13]
    assert sorted(tire_services) == sorted(expected_tire_services)

def test_split_tire_service_data2():
    df = pd.read_csv(StringIO(data2), sep='\\t', header=None, engine='python')
    df = df.reset_index()
    df["index"] = df["index"] + 1
    tire_services, general_services = split_tire_service(df)
    expected_tire_services = [2, 3, 4, 5]
    assert sorted(tire_services) == sorted(expected_tire_services)

def test_split_tire_service_data3():
    df = pd.read_csv(StringIO(data3), sep='\\t', header=None, engine='python')
    df = df.reset_index()
    df["index"] = df["index"] + 1
    tire_services, general_services = split_tire_service(df)
    expected_tire_services = []
    assert sorted(tire_services) == sorted(expected_tire_services)
