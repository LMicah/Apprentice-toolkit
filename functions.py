import tkinter as tk
from tkinter import messagebox
import pandas as pd
import re
import json
df_matrix = pd.read_csv("matriz.csv", sep=";", encoding="latin1", low_memory=False)
df_os = pd.read_csv("os.csv", sep=";", encoding="latin1", low_memory=False)

def process_orders(input_text, separator_entry, output_text):
    orders = input_text.get("1.0", tk.END)
    orders = "".join(orders.split()).replace(",", "")

    separator = separator_entry.get()
    if separator == "":
        separator = ","

    count = 0 
    new_orders = ""
    for char in orders: #Could (and should) be replaced with a regex, will think about it later.
        if count < 8:
            new_orders += char
            count += 1
        else:
            new_orders += f"{separator}{char}"
            count = 1

    if not new_orders:
        messagebox.showwarning("Atenção", "Não existe nenhuma ordem a ser processada")

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, new_orders)


def process_text(ptext_input, separator_entry, space_choice, output_text):
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
    elif new_text.endswith(separator):
        new_text = new_text[: -len(separator)]
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, new_text)


def increase_time(time, amount):  # will be used to create the output_text in work_logs 
    hours = int(time[:2]) #first two characters (dont touch this if its passing the regex the convertion will be fine)
    minutes = int(time[-2:]) #last two chracters (same as above)
    minutes += amount 

    while minutes >= 60:
        hours += 1
        minutes -= 60

    return f"{hours:02d}:{minutes:02d}" 

def time_str_to_decimal(time_str):
    hours, minutes = map(int, time_str.split(":")) #Yes yes i know this shit could be inside increase_time 
    return hours + minutes / 60                 

def work_logs(service_order, interval, date, starting_time, ending_time):
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
        return "Por favor, insira uma ordem de serviço"
    service_order = service_order.strip()

    try:
        start, end = map(int, interval.split("-"))
        interval_quantity = abs(end - start) + 1
    except ValueError:
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
        else:
            messagebox.showwarning("Atenção", "Insira um intervalo de sequência válido.")

    
    if r_date:
        day   = r_date.group(1)
        month = r_date.group(2)
        year  = r_date.group(3)
        if "/" not in r_date.group(0):
            date = f"{day}/{month}/{year}"
    else:
        return "Por favor, insira uma data válida."

    
    if s_time and e_time:
        starting_hours   = int(s_time.group(1)) 
        starting_minutes = int(s_time.group(2))
        ending_hours     = int(e_time.group(1))
        ending_minutes   = int(e_time.group(2))
    else:
        return "Por favor, insira um intervalo de tempo válido."

    
    real_hours = ending_hours - starting_hours
    real_minutes = ending_minutes - starting_minutes
    if intervals:
        available_time = (real_hours * 60 + real_minutes) / len(intervals)
        for idx, available_interval in enumerate(intervals):
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
    return output_text

def search_orders(search_input, search_output, number_of_lines):
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

def filters_and_equipments(search_input, search_output):
    equipment = search_input
    with open("info.json", encoding="utf-8") as file:
        fleet_data = json.load(file)
        dumpado = json.dumps(fleet_data, indent=4, ensure_ascii=False)
        if equipment == fleet_data[equipment]:
            ... 

def copy_text(widget, window): #This allows the user to copy the output text, used in all frames
    text = widget.get("1.0", tk.END).strip()
    if text:
        window.clipboard_clear()
        window.clipboard_append(text)
        window.update()
    else:
        messagebox.showwarning("Atenção", "Nada a ser copiado")
    

def get_equipment_and_plan(os_number):
    os_number_str = str(os_number).strip()
    os_line = df_os[df_os["O.S"].astype(str).str.strip() == os_number_str]

    if os_line.empty:
        return False, False

    equipment = str(os_line.iloc[0]["MODELO"]).strip()
    plan_str = str(os_line.iloc[0]["PLANO"]).strip()

    # handle multiple plans like "250/50"
    try:
        plan = max(int(p) for p in plan_str.replace(" ", "").split("/") if p.isdigit())
    except ValueError:
        plan = None

    return equipment, plan

def fetch_plans(equipment, plan):
    # Ensure integers
    df_matrix["no_ref_prog"] = pd.to_numeric(df_matrix["no_ref_prog"], errors="coerce")
    plan = int(plan)

    # Filter by equipment
    equipment_key = equipment.split()[0] + " " + equipment.split()[1]
    df_equipment = df_matrix[df_matrix["Chave"].str.contains(equipment_key, case=False, na=False)]

    if df_equipment.empty:
        return pd.DataFrame()

    # Get divisors
    valid_plans = [d for d in df_equipment["no_ref_prog"].unique() if plan % d == 0]

    # Exclude unwanted plans (checks case-insensitively)
    mask_blacklist = df_equipment["de_tp_manut"].str.upper().str.contains(
        "INSPEÇÃO|INS |HIBERNAÇÃO|ATIVAÇÃO DA HIBERNAÇÃO", na=False
    )

    # Filter by model, divisors and excluding blacklist
    filtered_df = df_equipment[
        (df_equipment["no_ref_prog"].isin(valid_plans)) &
        (df_equipment["fg_garantia"] == "N") &
        (~mask_blacklist)
    ][["no_seq", "de_operacao", "de_tarefa", "de_sist_veic", "de_sub_sist", "de_compo"]]

    # Remove duplicates and generates a new sequence
    filtered_df = filtered_df.drop_duplicates(subset=["de_operacao", "de_sist_veic", "de_sub_sist"])
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df["no_seq"] = range(1, len(filtered_df)+1)
    print(filtered_df)
    return filtered_df

def split_tire_service(df): #mechanical_service actually means "any other service", too lazy to change it tho
    #Filters for tire service
    tire_service_mask = (
    df["de_sub_sist"].str.strip().isin(["Roda", "Pneu"]) |
    df["de_tarefa"].str.contains("borracharia", case=False, na=False)
    )
    
    #Splits tire services from mechanical services
    tire_service = df[tire_service_mask].copy()
    mechanical_service = df[~tire_service_mask].copy()
    
    #Creates a list containing both services sequencies
    tire_service = tire_service["no_seq"].tolist()
    mechanical_service = mechanical_service["no_seq"].tolist()
    
    return tire_service, mechanical_service