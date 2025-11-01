import tkinter as tk
from tkinter import messagebox
import pandas as pd
import re
from io import StringIO


# --- Global Data Loading ---
# NOTE: Loading dataframes globally is generally not recommended as it creates hidden dependencies
# and makes functions harder to test independently. This section is kept for compatibility with the
# original project structure, but a refactor to pass dataframes as arguments or use a dedicated
# data loading class would be a significant improvement.
# I will do my best to refactor this in a more secure/clean way later, i just need the time to do so.

try:
    # Attempt to load CSV and Excel files required by various functions.
    df_matrix = pd.read_csv("matriz.csv", sep=";", encoding="latin1", low_memory=False)
    df_os = pd.read_csv("os.csv", sep=";", encoding="latin1", low_memory=False)
    bd_filters = pd.read_excel("planilha.xlsx", sheet_name="BD_FILTROS")
    stock = pd.read_excel("planilha.xlsx", sheet_name="Saldo Almoxarifado")
    itens_prices = pd.read_excel("planilha.xlsx", sheet_name="Valor das peças")
except FileNotFoundError:
    # This pass is intended to allow the application to run in environments where
    # these specific data files are not present (e.g., for third-party testing).
    # However, functions depending on these dataframes will fail if called.
    pass


def process_orders(input_text: tk.Text, separator_entry: tk.Entry, output_text: tk.Text) -> None:
    """
    Finds all valid service order numbers from an input widget, joins them with a
    specified separator, and displays the result in an output widget.

    A valid service order is defined by the regex pattern `\\b621\\d{5}\\b`.

    Args:
        input_text (tk.Text): The Tkinter Text widget containing the raw text with service orders.
        separator_entry (tk.Entry): The Tkinter Entry widget for the desired separator.
                                      If empty, a comma "," is used by default.
        output_text (tk.Text): The Tkinter Text widget where the formatted string of
                               service orders will be displayed.
    """
    # Define the regex pattern for a valid service order (starts with 621 followed by 5 digits).
    orders_pattern = r"\b621\d{5}\b"

    # Get text from the input widget and find all matching orders.
    text_content = input_text.get("1.0", tk.END)
    orders = re.findall(orders_pattern, text_content)

    # Get the user-defined separator, defaulting to "," if empty.
    separator = separator_entry.get()
    if not separator:
        separator = ","

    # Join the found orders into a single string.
    new_orders = separator.join(orders)

    # If no orders were found, show a warning and exit.
    if not new_orders:
        messagebox.showwarning("Atenção", "Não existe nenhuma ordem a ser processada")
        return

    # Clear the output widget and insert the processed orders.
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, new_orders)


def process_text(ptext_input: tk.Text, separator_entry: tk.Entry, space_choice: bool, output_text: tk.Text) -> None:
    """
    Processes a block of text by joining its content with a specified separator.
    It can either replace all whitespace with the separator or only newlines,
    based on the `space_choice` flag.

    Args:
        ptext_input (tk.Text): The Tkinter Text widget with the text to process.
        separator_entry (tk.Entry): The Tkinter Entry widget for the separator.
                                      Defaults to ", " if empty.
        space_choice (bool): If True, preserves spaces within lines and only replaces
                             newlines with the separator. If False, replaces all
                             whitespace (spaces and newlines) with the separator.
        output_text (tk.Text): The Tkinter Text widget to display the result.
    """
    text = ptext_input.get("1.0", tk.END).strip()
    lines = text.split("\n")

    separator = separator_entry.get()
    if separator == "":
        separator = ", "

    new_text = ""
    last_is_space = False  # Flag to prevent multiple separators for consecutive spaces.

    for line in lines:
        line = line.strip()
        for char in line:
            # If space replacement is enabled and the character is a space...
            if char == " " and not space_choice:
                # Add separator only if the previous character wasn't also a space.
                if not last_is_space:
                    new_text += separator
                    last_is_space = True
            else:
                new_text += char
                last_is_space = False

        # Add a separator after each processed line (which originally was a newline).
        new_text += separator

    if not text:
        messagebox.showwarning("Atenção", "Nenhum texto inserido")
        return

    # Clean up any trailing separator at the end of the final string.
    if new_text.endswith(separator):
        new_text = new_text[: -len(separator)]

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, new_text)


def increase_time(time_str: str, minutes_to_add: int) -> str:
    """
    Increments a time string (HH:MM) by a given number of minutes.

    Args:
        time_str (str): The initial time in "HH:MM" format.
        minutes_to_add (int): The number of minutes to add to the time.

    Returns:
        str: The new time in "HH:MM" format.
    """
    hours = int(time_str[:2])
    minutes = int(time_str[-2:])
    minutes += minutes_to_add

    # Handle minute overflow by converting to hours.
    while minutes >= 60:
        hours += 1
        minutes -= 60

    return f"{hours:02d}:{minutes:02d}"


def time_str_to_decimal(time_str: str) -> float:
    """
    Converts a time string (HH:MM) into a decimal representation of hours.
    Example: "01:30" becomes 1.5.

    Args:
        time_str (str): The time string to convert.

    Returns:
        float: The decimal representation of the hours.
    """
    hours, minutes = map(int, time_str.split(":"))
    return hours + minutes / 60


def work_logs(service_order: str, interval_str: str, date: str, starting_time: str, ending_time: str, choice: str = "") -> str:
    """
    Generates formatted work log entries for a given time period and sequence intervals.

    The function parses sequence intervals from various formats (e.g., "1-5", "1 2 3",
    or newline-separated values). It then divides the total time available equally
    among the sequences and generates a tab-separated string for each log entry.

    Args:
        service_order (str): The service order number.
        interval_str (str): A string containing sequence numbers. Can be a range ("1-5"),
                            space-separated ("1 2 3"), or newline-separated.
        date (str): The date for the logs, expected in "dd/mm/yyyy" format.
        starting_time (str): The start time for the logs, in "hh:mm" format.
        ending_time (str): The end time for the logs, in "hh:mm" format.
        choice (str, optional): An optional flag, typically "tire_service", to handle
                                specific processing logic if needed. Defaults to "".

    Returns:
        str: A formatted string containing all generated work log entries, separated by newlines,
             or None if an error occurs.
    """
    # --- Input Validation and Sanitization ---
    date_pattern = r"^(\d{2})[\/]?(\d{2})[\/]?(\d{4})$"
    time_pattern = r"^(\d{2})[\:]?(\d{2})$"

    if not service_order:
        messagebox.showwarning("Atenção", "Por favor, insira uma ordem de serviço")
        return

    service_order = service_order.strip()

    r_date = re.search(date_pattern, date.strip())
    s_time = re.search(time_pattern, starting_time.strip())
    e_time = re.search(time_pattern, ending_time.strip())

    if not r_date:
        messagebox.showwarning("Atenção", "Por favor, insira uma data válida.")
        return
    if not s_time or not e_time:
        messagebox.showwarning("Atenção", "Por favor, insira um intervalo de tempo válido.")
        return

    # Reformat date to ensure it has slashes for consistency.
    day, month, year = r_date.groups()
    date = f"{day}/{month}/{year}"

    # --- Interval Parsing ---
    total_interval = []
    interval_str = interval_str.replace('"', '')
    try:
        # Case 1: Simple range format, e.g., "1-5"
        start, end = map(int, interval_str.split("-"))
        total_interval = list(range(start, end + 1))
    except (ValueError, AttributeError):
        # Case 2: Space or newline separated values, possibly with ranges mixed in.
        try:
            cleaned_interval_str = interval_str.strip()
            if " " in cleaned_interval_str or "\n" in cleaned_interval_str:
                items = re.split(r'[\s\n]+', cleaned_interval_str)
                for item in items:
                    if "-" in item:
                        s, e = map(int, item.split("-"))
                        total_interval.extend(list(range(s, e + 1)))
                    elif item:
                        total_interval.append(int(item))
            else:
                messagebox.showwarning("Atenção", "Insira um intervalo de sequência válido.")
                return
        #Case 3: interval copied and pasted from an external software, in the following pattern:
        #N	S		15	15	1	11	Engraxar / Lubrificar	Lubrifcar os pontos de graxa (quinta-roda, catracas, rala, etc).
        # 2400	Lab.Lub / Comboio	2402	Lubrificação	999396	Graxa
        except ValueError:
            df = pd.read_csv(StringIO(interval_str), sep="\t", header=None, engine="python")
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

    if not total_interval:
        messagebox.showwarning("Atenção", "Nenhuma sequência válida encontrada no intervalo.")
        return

    # --- Time Calculation ---
    starting_hours, starting_minutes = map(int, s_time.groups())
    ending_hours, ending_minutes = map(int, e_time.groups())

    total_minutes_available = (ending_hours - starting_hours) * 60 + (ending_minutes - starting_minutes)

    if total_minutes_available < 0:
        messagebox.showwarning("Atenção", "Conserte o horário inserido e pare de fazer cagada!.")
        return

    try:
        time_per_interval = total_minutes_available / len(total_interval)
    except ZeroDivisionError:
        messagebox.showwarning("Atenção", "O intervalo de sequências não pode estar vazio.")
        return

    if time_per_interval < 1:
        messagebox.showwarning("Atenção", "O tempo mínimo necessário para cada sequência é de um minuto, " \
      "por favor, aumente o intervalo de tempo ou diminua a quantidade de sequências.")
        return

    # --- Log Generation ---
    output_text = ""
    for idx, interval_num in enumerate(total_interval):
        start_offset = int(time_per_interval * idx)
        end_offset = int(time_per_interval * (idx + 1))

        log_start_time = increase_time(starting_time, start_offset)
        log_end_time = increase_time(starting_time, end_offset)

        total_hours = time_str_to_decimal(log_end_time) - time_str_to_decimal(log_start_time)
        formatted_total_hours = f"{total_hours:.2f}".replace(".", ",")

        output_text += f"{service_order}\t\t\t{interval_num}\t\t\t\t\t\t\t\t\t\t{date}\t{log_start_time}\t{date}\t{log_end_time}\t{formatted_total_hours}\n"

    return output_text


def search_orders(search_input: tk.Text, search_output: tk.Text, number_of_lines_label: tk.Label) -> None:
    """
    Searches for valid service order numbers within a text widget and displays the
    results in another widget, along with a count of found orders.

    Args:
        search_input (tk.Text): The widget containing the text to search through.
        search_output (tk.Text): The widget where the found orders will be displayed.
        number_of_lines_label (tk.Label): The label to update with the count of found orders.
    """
    text = search_input.get("1.0", tk.END).replace("\n", " ")
    pattern = r"\b621\d{5}\b"
    found_orders = re.findall(pattern, text)

    search_output.delete("1.0", tk.END)

    if found_orders:
        result = " ".join(found_orders)
        search_output.insert(tk.END, result)
        number_of_lines_label.config(text=f"Quantidade de ordens encontradas: {len(found_orders)}")
    else:
        messagebox.showwarning("Atenção", "Nenhuma ordem encontrada")
        number_of_lines_label.config(text="Quantidade de ordens encontradas: 0")


def get_equipment_items(choice: int) -> pd.DataFrame:
    """
    Fetches and merges data related to equipment items based on a fleet number.

    This function queries several pre-loaded pandas DataFrames (bd_filters, stock, itens_prices)
    to compile a final DataFrame with details about parts, stock, and prices for a given
    equipment fleet number.

    Args:
        choice (int): The fleet number of the equipment.

    Returns:
        pd.DataFrame: A DataFrame containing the filtered and merged information about
                      the equipment's items. Returns an empty DataFrame or None on error.
    """
    if not choice:
        messagebox.showwarning("Atenção", "Por favor, insira uma frota")
        return pd.DataFrame()

    # Create copies to avoid modifying the global dataframes
    local_bd_filters = bd_filters.set_index("FROTA")
    local_stock = stock.set_index("Material")
    local_itens_prices = itens_prices.set_index("Material")

    try:
        # Filter items for the selected fleet number.
        equipment_items = local_bd_filters.loc[choice]
    except KeyError:
        messagebox.showwarning("Atenção", "Por favor, insira uma frota válida")
        return pd.DataFrame()

    equipment_items = equipment_items.reset_index()

    # Merge equipment items with their prices.
    final_df = pd.merge(
        equipment_items,
        local_itens_prices,
        left_on="Cod. Sap",
        right_on="Material",
        how="left"
    )

    # Join the result with stock quantity information.
    stock_quantity = local_stock[["Utilização livre"]]
    final_df = final_df.set_index("Cod. Sap").join(stock_quantity, how="left").reset_index()

    # Define and filter for the columns required for the final output.
    desired_columns = [
        "PLANO REAL", "Tipo da peça", "Cod. Sap", "Texto breve material",
        "Tipo de MRP", "QNTD."
    ]
    # Ensure all desired columns exist, adding missing ones with default values if necessary.
    for col in desired_columns:
        if col not in final_df.columns:
            final_df[col] = None

    final_df = final_df[desired_columns]

    # Clean up newline characters from string columns.
    for column in final_df.columns:
        if final_df[column].dtype == "object":
            final_df[column] = final_df[column].astype(str).str.replace("\n", "")

    # Sanitize quantity column.
    final_df["QNTD."] = final_df["QNTD."].fillna(0).astype(int)

    return final_df


def copy_text(widget: tk.Text, window: tk.Tk) -> None:
    """
    Copies the entire content of a Tkinter Text widget to the clipboard.

    Args:
        widget (tk.Text): The Text widget from which to copy the content.
        window (tk.Tk): The root Tkinter window, used to access the clipboard.
    """
    text = widget.get("1.0", tk.END).strip()
    if text:
        window.clipboard_clear()
        window.clipboard_append(text)
        window.update()  # Required to make the clipboard content available immediately.
    else:
        messagebox.showwarning("Atenção", "Nada a ser copiado")


def get_equipment_and_plan(os_number: str) -> tuple[str, list] | tuple[bool, bool]:
    """
    Retrieves the equipment model and maintenance plan(s) for a given service order number.

    Args:
        os_number (str): The service order number.

    Returns:
        tuple[str, list]: A tuple containing the equipment model (str) and a list of plan
                          numbers (list of strings).
        tuple[bool, bool]: Returns (False, False) if the service order is not found.
    """
    os_number_str = str(os_number).strip()
    os_line = df_os[df_os["O.S"].astype(str).str.strip() == os_number_str]

    if os_line.empty:
        return False, False

    equipment = str(os_line.iloc[0]["MODELO"]).strip()
    plan_str = str(os_line.iloc[0]["PLANO"]).strip()

    plan_list = plan_str.split("/")
    return equipment, plan_list


def fetch_plans(equipment: str, plans: list[str]) -> pd.DataFrame:
    """
    Fetches maintenance tasks from the matrix based on equipment and plan numbers.

    Args:
        equipment (str): The equipment model identifier.
        plans (list[str]): A list of maintenance plan numbers.

    Returns:
        pd.DataFrame: A DataFrame containing the filtered and cleaned maintenance tasks.
                      Returns an empty DataFrame if no matching tasks are found.
    """
    # Ensure plan numbers are integers for correct filtering.
    df_matrix["no_ref_prog"] = pd.to_numeric(df_matrix["no_ref_prog"], errors="coerce")
    valid_plans = [int(p.strip()) for p in plans if p.strip().isdigit()]

    # Create unique keys to filter the matrix dataframe.
    keys = [f"{equipment}{p}N" for p in valid_plans]
    df_equipment = df_matrix[df_matrix["Chave"].isin(keys)]

    if df_equipment.empty:
        return pd.DataFrame()

    # Define a blacklist of maintenance types to exclude.
    blacklist_pattern = "INSPEÇÃO|INS |HIBERNAÇÃO|ATIVAÇÃO DA HIBERNAÇÃO"
    mask_blacklist = df_equipment["de_tp_manut"].str.upper().str.contains(blacklist_pattern, na=False)

    # Apply all filters.
    filtered_df = df_equipment[
        (df_equipment["no_ref_prog"].isin(valid_plans)) &
        (df_equipment["fg_garantia"] == "N") &
        (~mask_blacklist)
    ]

    # Select and clean the final columns.
    final_columns = ["no_seq", "de_operacao", "de_tarefa", "de_sist_veic", "de_sub_sist", "de_compo"]
    filtered_df = filtered_df[final_columns]

    # Remove duplicates and re-generate sequence numbers to ensure they are consecutive.
    subset_cols = ["de_operacao", "de_sist_veic", "de_sub_sist", "de_compo"]
    filtered_df = filtered_df.drop_duplicates(subset=subset_cols).reset_index(drop=True)
    filtered_df["no_seq"] = range(1, len(filtered_df) + 1)

    return filtered_df


def _normalize_and_rename_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes the input DataFrame to a consistent format with named columns.
    Detects if the format has extra empty columns and selects the correct
    columns for status, description, and component.
    """
    df_copy = df.copy()

    # Heuristic to detect format: check if column 2 is entirely empty,
    # which indicates the sparse format with shifted columns.
    if 2 in df_copy.columns and df_copy[2].isna().all():
        # Format with blank columns: status=0, description=8, component=12
        # Ensure target columns exist before access
        if 8 not in df_copy.columns or 12 not in df_copy.columns:
            return pd.DataFrame(columns=['index', 'status', 'description', 'component'])

        renamed_df = df_copy[['index', 0, 8, 12]].copy()
        renamed_df.columns = ['index', 'status', 'description', 'component']
    else:
        # Standard format: status=0, description=6, component=10
        if 6 not in df_copy.columns or 10 not in df_copy.columns:
            return pd.DataFrame(columns=['index', 'status', 'description', 'component'])

        renamed_df = df_copy[['index', 0, 6, 10]].copy()
        renamed_df.columns = ['index', 'status', 'description', 'component']

    # Ensure consistent data types for string operations
    for col in ['status', 'description', 'component']:
        renamed_df[col] = renamed_df[col].astype(str)

    return renamed_df


def split_tire_service(df: pd.DataFrame) -> tuple[list[int], list[int]]:
    """
    Separates tire service tasks from general tasks using a set of clear, maintainable rules.
    """
    norm_df = _normalize_and_rename_df(df)

    if norm_df.empty:
        return [], []

    # --- Base Conditions ---
    is_pending = norm_df['status'].str.strip() == 'N'
    is_tire_component = norm_df['component'].str.strip().isin(['Roda', 'Pneu'])

    # --- Inclusion Rules (conditions that identify a tire service) ---

    # Rule 2.3: Description contains "borracharia"
    rule_borracharia = norm_df['description'].str.contains('borracharia', case=False, na=False)

    # Rule 2.4 & 2.5: Description contains a specific integrity check for "(trincas..."
    rule_specific_integrity = norm_df['description'].str.contains(
        r'verificar a integridade \(trincas', case=False, na=False, regex=True
    )

    # Rule 2.1: Description contains general tire-related keywords
    rule_pneu_keywords = norm_df['description'].str.contains(
        r'pneus|pneu|verificar torque das porcas das rodas', case=False, na=False, regex=True
    )

    # --- Exclusion Rules (conditions that disqualify a tire service) ---

    # Rule 2.2: Description contains "pneum" (for pneumatic), which is not a tire service
    is_pneumatic_system = norm_df['description'].str.contains('pneum', case=False, na=False)

    # Rule 2 & 2.5: General integrity checks or other specific non-tire tasks
    # are excluded unless a more specific inclusion rule (like for "trincas") matches.
    exclusion_keywords = [
        "suspensões", "Sistema de freio", "Verificar guias",
        "Verificar porca e parafuso das rodas", "Quando houver espaçador, retirar rodas"
    ]
    rule_general_exclusions = norm_df['description'].str.contains(
        '|'.join(exclusion_keywords), case=False, na=False
    )
    # A generic "Verificar a integridade" is only an exclusion if the specific one didn't match
    rule_generic_integrity_exclusion = norm_df['description'].str.contains(
        "Verificar a integridade", case=False, na=False
    ) & ~rule_specific_integrity

    # --- Combine Logic ---

    # A service is a tire service if it meets any of the primary inclusion rules.
    is_tire_service = (
        rule_borracharia |
        (is_tire_component & (rule_specific_integrity | rule_pneu_keywords))
    )

    # A service is also a tire service by default if it's a tire component
    # and not explicitly excluded.
    is_tire_by_default = (
        is_tire_component &
        ~rule_general_exclusions &
        ~rule_generic_integrity_exclusion
    )

    is_tire_service = is_tire_service | is_tire_by_default

    # Final mask: must be pending, a tire service, and not pneumatic.
    final_tire_mask = is_pending & is_tire_service & ~is_pneumatic_system

    tire_service_sequences = norm_df[final_tire_mask]['index'].tolist()
    general_service_sequences = norm_df[is_pending & ~final_tire_mask]['index'].tolist()

    return tire_service_sequences, general_service_sequences


def split_auto_tire_service(df: pd.DataFrame) -> tuple[list[int], list[int]]:
    """
    Separates tire service tasks from general tasks in a DataFrame from `fetch_plans`.

    This function is similar to `split_tire_service` but operates on a structured
    DataFrame with named columns ('de_sub_sist', 'de_tarefa') as returned by `fetch_plans`.

    Args:
        df (pd.DataFrame): The DataFrame with maintenance tasks.

    Returns:
        tuple[list[int], list[int]]: A tuple containing two lists of sequence numbers ('no_seq'):
                                     - The first list is for tire services.
                                     - The second list is for general services.
    """
    # Ensure columns exist and have the correct type for string operations.
    df["de_sub_sist"] = df["de_sub_sist"].astype(str)
    df["de_tarefa"] = df["de_tarefa"].astype(str)

    # Heuristic mask to identify tire-related services based on keywords.
    tire_service_mask = (
        (df["de_sub_sist"].str.contains(r"Verificar a integridade \(trincas, desgastes acentuados, danos críticos\) dos espelhos da roda|Verificar integridade \(trincas, desgastes acentuados, danos críticos\) dos espelhos da roda", case=False, na=False))|
        (df["de_sub_sist"].str.strip().isin(["Roda", "Pneu"])) &
        (~df["de_tarefa"].str.contains("Verificar integridade|Verificar a integridade", case=False, na=False)) &
        (~df["de_tarefa"].str.contains("Quando houver espaçador, retirar rodas", case=False, na=False)) |
        (df["de_tarefa"].str.contains("pneus|pneu", case=False, na=False)) &
        (~df["de_tarefa"].str.contains("pneum", case=False, na=False)) |
        (df["de_tarefa"].str.contains("borracharia", case=False, na=False)) &
        (~df["de_tarefa"].str.contains("Verificar integridade|Verificar a integridade", case=False, na=False))|
        (df["de_tarefa"].str.contains(r"Verificar a integridade \(trincas, desgastes acentuados, danos críticos\) dos espelhos da roda|Verificar integridade \(trincas, desgastes acentuados, danos críticos\) dos espelhos da roda", case=False, na=False))
    )

    tire_service_df = df[tire_service_mask]
    general_service_df = df[~tire_service_mask]

    tire_service_sequences = tire_service_df["no_seq"].tolist()
    general_service_sequences = general_service_df["no_seq"].tolist()

    return tire_service_sequences, general_service_sequences
