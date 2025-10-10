import tkinter as tk
from tkinter import messagebox
import pandas as pd
import re
from io import StringIO


#### Imports and load the necessary files #####

try:
    df_matrix = pd.read_csv("matriz.csv", sep=";", encoding="latin1", low_memory=False)
    df_os = pd.read_csv("os.csv", sep=";", encoding="latin1", low_memory=False)
    bd_filters = pd.read_excel("planilha.xlsx", sheet_name="BD_FILTROS")
    stock= pd.read_excel("planilha.xlsx", sheet_name="Saldo Almoxarifado")
    itens_prices = pd.read_excel("planilha.xlsx", sheet_name="Valor das peças")
except ValueError:
    pass ##Intended for third-party testers

#### Except actually only works if you try to run the main.py in an IDE, any ######
#### attempts to run the .exe pyinstaller file will still result in crashing ######


def process_orders(input_text: str , separator_entry: str, output_text: str)-> None:
    orders_pattern = r"\b621\d{5}\b"
    orders = input_text.get("1.0", tk.END)
    orders = re.findall(orders_pattern, orders)

    separator = separator_entry.get()
    if separator == "":
        separator = ","

    new_orders = separator.join(orders)

    if not new_orders:
        messagebox.showwarning("Atenção", "Não existe nenhuma ordem a ser processada")
        return

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, new_orders)


def process_text(ptext_input: str, separator_entry: str, space_choice: bool, output_text: str)-> None:
    text = ptext_input.get("1.0", tk.END).strip()
    lines = text.split("\n")

    separator = separator_entry.get()
    if separator == "":
        separator = ", "

    new_text = ""
    last_is_space = False  # used to check for multiple blank spaces

    for line in lines:
        line = line.strip()
        for char in line:
            if char == " " and not space_choice:
                if not last_is_space:
                    new_text += separator
                    last_is_space = True
            else:
                new_text += char
                last_is_space = False

        new_text += separator

    if not text:
        messagebox.showwarning("Atenção", "Nenhum texto inserido")
        return
    elif new_text.endswith(separator):
        new_text = new_text[: -len(separator)]
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, new_text)


def increase_time(time: str, amount: int)->str:  # will be used to create the output_text in work_logs 
    hours = int(time[:2]) #first two characters (dont touch this if its passing the regex the convertion will be fine)
    minutes = int(time[-2:]) #last two chracters (same as above)
    minutes += amount 

    while minutes >= 60:
        hours += 1
        minutes -= 60

    return f"{hours:02d}:{minutes:02d}" 

def time_str_to_decimal(time_str: str):
    hours, minutes = map(int, time_str.split(":")) #Yes yes i know this shit could be inside increase_time 
    return hours + minutes / 60                 

def work_logs(service_order: str, interval: str, date: str, starting_time: str, ending_time: str, choice: str = ""):

    interval_quantity = 0
    intervals = None
    real_hours = 0
    real_minutes = 0
    available_time = 0
    output_text = ""
    date_pattern = r"^(\d{2})[\/]?(\d{2})[\/]?(\d{4})$"
    time_pattern = r"^(\d{2})[\:]?(\d{2})$"
    total_interval = []
    r_date = re.search(date_pattern, date.strip())
    s_time = re.search(time_pattern, starting_time.strip())
    e_time = re.search(time_pattern, ending_time.strip())


    if not service_order:
        messagebox.showwarning("Atenção", "Por favor, insira uma ordem de serviço")
        return
    service_order = service_order.strip()
    

    try:
        start, end = map(int, interval.split("-"))
        interval_quantity = abs(end - start) + 1
    except (ValueError, AttributeError):
        try:
            if " " in interval:
                intervalsx = interval.split()
                for intervalx in intervalsx:
                    if "-" in intervalx:  
                        s, e = intervalx.split("-")
                        for c in range(int(s), int(e) + 1):
                            total_interval.append(c)
                    else:
                        total_interval.append(int(intervalx))
            elif "\n" in interval:
                intervals = [
                    line.strip()
                    for line in interval.strip().split("\n")
                    if line.strip()
                ]
        except (ValueError, AttributeError):
            df = pd.read_csv(StringIO(interval), sep="\t", header=None, engine="python")
            df = df.reset_index()
            df["index"] = df["index"] + 1
            tire_service, general = split_tire_service(df)

            if choice == "tire_service":
                if not tire_service:
                    messagebox.showwarning("Atenção", "Essa ordem de serviço não possui serviços de borracharia.")
                    return
                else:
                    total_interval = [str(x) for x in tire_service]
            else:
                total_interval = [str(x) for x in general]

    if r_date:
        day   = r_date.group(1)
        month = r_date.group(2)
        year  = r_date.group(3)
        if "/" not in r_date.group(0):
            date = f"{day}/{month}/{year}"
    else:
        messagebox.showwarning("Atenção", "Por favor, insira uma data válida.")
        return

    
    if s_time and e_time:
        starting_hours   = int(s_time.group(1)) 
        starting_minutes = int(s_time.group(2))
        ending_hours     = int(e_time.group(1))
        ending_minutes   = int(e_time.group(2))
    else:
        messagebox.showwarning("Atenção", "Por favor, insira um intervalo de tempo válido.")
        return 

    
   
    real_hours = ending_hours - starting_hours
    real_minutes = ending_minutes - starting_minutes
    if intervals:
        available_time = (real_hours * 60 + real_minutes) / len(intervals)     #I will remake this entire monster later
        for idx, available_interval in enumerate(intervals):                   #3 months later: i will never remake this
            start_time = increase_time(starting_time, int(available_time * idx))
            end_time = increase_time(starting_time, int(available_time * (idx + 1)))
            total_hours = time_str_to_decimal(end_time) - time_str_to_decimal(start_time)
            formatted_total_hours = f"{total_hours:.2f}".replace(".", ",")

            output_text += f"{service_order}\t\t\t{available_interval}\t\t\t\t\t\t\t\t\t\t{date}\t{start_time}\t{date}\t{end_time}\t{formatted_total_hours}\n"
    elif total_interval:
        available_time = (real_hours * 60 + real_minutes) / len(total_interval)
        for idx, available_interval in enumerate(total_interval):
            start_time = increase_time(starting_time, int(available_time * idx))
            end_time = increase_time(starting_time, int(available_time * (idx + 1)))

            total_hours = time_str_to_decimal(end_time) - time_str_to_decimal(start_time)
            formatted_total_hours = f"{total_hours:.2f}".replace(".", ",")

            output_text += f"{service_order}\t\t\t{available_interval}\t\t\t\t\t\t\t\t\t\t{date}\t{start_time}\t{date}\t{end_time}\t{formatted_total_hours}\n"
    else:
        try:
            available_time = (real_hours * 60 + real_minutes) / interval_quantity
            for number in range(start, end + 1):
                start_time = increase_time(starting_time, int(available_time * (number - start)))
                end_time = increase_time(starting_time, int(available_time * (number - start + 1)))

                total_hours = time_str_to_decimal(end_time) - time_str_to_decimal(start_time)
                formatted_total_hours = f"{total_hours:.2f}".replace(".", ",")

                output_text += f"{service_order}\t\t\t{number}\t\t\t\t\t\t\t\t\t\t{date}\t{start_time}\t{date}\t{end_time}\t{formatted_total_hours}\n"
        except ZeroDivisionError:
            messagebox.showwarning("Atenção", "Insira um intervalo de sequência válido.")
            return
        
    if "-" in output_text:
        messagebox.showwarning("Atenção", "Conserte o horário inserido e pare de fazer cagada!.")
        return
    elif "0,00" in output_text:
        messagebox.showwarning("Atenção", "O tempo mínimo necessário para cada sequência é de um minuto, " \
        "por favor, aumente o intervalo de tempo ou diminua a quantidade de sequências.")
        return
    return output_text


def search_orders(search_input: str, search_output: str, number_of_lines: str)-> None:
    text = search_input.get("1.0", tk.END).replace("\n", " ")
    pattern = r"\b621\d{5}\b"
    found = re.findall(pattern, text)

    search_output.delete("1.0", tk.END)

    if found:
        result = " ".join(found)
        search_output.insert(tk.END, result)
        number_of_lines.config(text= f"Quantidade de ordens encontradas: {len(found)}")
    else:
        messagebox.showwarning("Atenção", "Nenhuma ordem encontrada")
        return

def get_equipment_items(choice: int, bd_filters=bd_filters, stock=stock, itens_prices=itens_prices)-> pd.DataFrame:
    #DISCLAIMER: DF STANDS FOR DATA FRAME AND PD FOR PANDAS 

    if not choice:
        messagebox.showwarning("Atenção", "Por favor, insira uma frota")
        return
    
    bd_filters = bd_filters.set_index("FROTA")        #↧
    stock = stock.set_index("Material")               # Sets the correct index
    itens_prices = itens_prices.set_index("Material") #↥

    try:
        equipment_items = bd_filters.loc[choice]         #Gets only the rows that matches with the choice var 
    except KeyError:
        messagebox.showwarning("Atenção", "Por favor, insira uma frota válida")  
        return                                                   
    equipment_items = equipment_items.reset_index() 


    final_df = pd.merge( ## Merges both dataframes
        equipment_items, #first df
        itens_prices, #second df
        left_on="Cod. Sap", #which column with same data to use from the first df
        right_on="Material", #which column with same data to use from the second df
        how="left" #looks for matchson the second dataframe using the specified columns
    )


    stock_quantity = stock[["Utilização livre"]] #gets the available stock column so we can merge (.join) it 
    final_df = final_df.set_index(["Cod. Sap"])  #Sets the final_df index with the "Cod. Sap" column to make the join possible
    final_df = final_df.join(stock_quantity, how="left") #joins stock_quantity to the right of final_df
    final_df = final_df.reset_index() #resets the final_df index so we can use the "Cod. Sap" column in the desired_columns


                    #The only columns we need from the final_df
    desired_columns = ["PLANO REAL", "Tipo da peça", 
                       "Cod. Sap", "Texto breve material",
                       "Tipo de MRP",  "QNTD.",]
    
    final_df = final_df[desired_columns] #Filtering so the final_df contains only the desired_columns


    for column in final_df.columns: #will clean missplaced "\n's"
        if final_df[column].dtype == "object":
            final_df[column] = final_df[column].astype(str).str.replace("\n", "")

    final_df["QNTD."] = final_df["QNTD."].fillna(0).astype(int)
    return final_df



def copy_text(widget, window)-> None: #This allows the user to copy the output text, used in all frames
    text = widget.get("1.0", tk.END).strip()
    if text:
        window.clipboard_clear()
        window.clipboard_append(text)
        window.update()
    else:
        messagebox.showwarning("Atenção", "Nada a ser copiado")
        return

def get_equipment_and_plan(os_number: str)-> tuple:
    os_number_str = str(os_number).strip()
    os_line = df_os[df_os["O.S"].astype(str).str.strip() == os_number_str]

    if os_line.empty:
        return False, False

    equipment = str(os_line.iloc[0]["MODELO"]).strip()
    plan = str(os_line.iloc[0]["PLANO"]).strip()

    plan_list = plan.split("/")

    return equipment, plan_list

def fetch_plans(equipment: str, plans: str)-> pd.DataFrame:
    # Make sure the plans are integers
    df_matrix["no_ref_prog"] = pd.to_numeric(df_matrix["no_ref_prog"], errors="coerce")
    plans = [int(str(p).strip()) for p in plans]
    print(plans)

    # Filter by equipment
    keys = [f"{equipment}{p}N" for p in plans]
    df_equipment = df_matrix[df_matrix["Chave"].isin(keys)]


    if df_equipment.empty:
        return pd.DataFrame()

    # Exclude unwanted plans 
    mask_blacklist = df_equipment["de_tp_manut"].str.upper().str.contains(
        "INSPEÇÃO|INS |HIBERNAÇÃO|ATIVAÇÃO DA HIBERNAÇÃO", case= False, na=False
    )

    filtered_df = df_equipment[
        (df_equipment["no_ref_prog"].isin(plans)) &
        (df_equipment["fg_garantia"] == "N") &
        (~mask_blacklist)
    ][["no_seq", "de_operacao", "de_tarefa", "de_sist_veic", "de_sub_sist", "de_compo"]]

    # Remove duplicates and generates a new sequence
    filtered_df = filtered_df.drop_duplicates(subset=["de_operacao", "de_sist_veic", "de_sub_sist", "de_compo"])
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df["no_seq"] = range(1, len(filtered_df)+1)
    print(filtered_df)
    return filtered_df

def split_tire_service(df: pd) -> tuple: #mechanical_service actually means "any other service", too lazy to change it tho
    if 10 not in df.columns: #DO NOT FUCKING TOUCH THIS
        for i in range(11):
            if i not in df.columns:
                df[i] = ""

    df[10] = df[10].astype(str)
    df[6] = df[6].astype(str)

    column_2_is_nan = df[2].isna().all()
    if column_2_is_nan:
        df.drop(2, axis=1, inplace=True)
        df[10] = df[10].astype(str)
        df[6] = df[6].astype(str)
        df.rename(columns={10:14, 12:10, 6:2, 8:6, 7:8}, inplace=True)

    tire_service_mask = (
    (df[6].str.contains("Verificar integridade das rodas", case=False, na=False))|
    (df[10].str.strip().isin(["Roda", "Pneu"])) & 
    (~df[6].str.contains("Verificar integridade|Verificar a integridade|suspensões|Sistema de freio", case=False, na=False))&
    (~df[6].str.contains("Quando houver espaçador, retirar rodas", case=False, na=False))|
    (df[6].str.contains("pneus|pneu|verificar torque das porcas das rodas.", case=False, na=False)) &
    (~df[6].str.contains("pneum", case=False, na=False))|
    (df[6].str.contains("borracharia", case=False, na=False)) & 
    (~df[6].str.contains("Verificar integridade|Verificar a integridade", case=False, na=False))
    )
    
    pending_service_mask= ( #filters for pending services so we can save up resources 
    df[0].str.strip() == "N"
    )

    tire_service = df[tire_service_mask & pending_service_mask].copy()
    general = df[(~tire_service_mask) & pending_service_mask].copy()

    tire_service = tire_service["index"].tolist()
    general = general["index"].tolist()
    
    return tire_service, general

def split_auto_tire_service(df: pd)-> tuple: #Same as above but works for auto logs generation
    df["de_sub_sist"] = df["de_sub_sist"].astype(str)
    df["de_tarefa"] = df["de_tarefa"].astype(str)
    tire_service_mask = (
    (df["de_sub_sist"].str.strip().isin(["Roda", "Pneu"])) & 
    (~df["de_tarefa"].str.contains("Verificar integridade|Verificar a integridade", case=False, na=False))&
    (~df["de_tarefa"].str.contains("Quando houver espaçador, retirar rodas", case=False, na=False))|
    (df["de_tarefa"].str.contains("pneus|pneu", case=False, na=False)) &
    (~df["de_tarefa"].str.contains("pneum", case=False, na=False))|
    (df["de_tarefa"].str.contains("borracharia", case=False, na=False)) & 
    (~df["de_tarefa"].str.contains("Verificar integridade|Verificar a integridade", case=False, na=False))
    )
    
    tire_service = df[tire_service_mask].copy()
    general = df[~tire_service_mask].copy()
    
    tire_service = tire_service["no_seq"].tolist()
    general = general["no_seq"].tolist()
    
    return tire_service, general