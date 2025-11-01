#
# main.py
#
# Description:
# This script contains the main user interface (UI) for the "Apprentice Toolkit" application.
# It is built using Tkinter and organizes the UI into a single class, `App`.
# The application's core logic is imported from the `functions.py` module, ensuring a clear
# separation between the presentation layer (this file) and the business logic.
#

import tkinter as tk
from tkinter import ttk, messagebox
from functions import (
    process_orders,
    process_text,
    search_orders,
    copy_text,
    work_logs,
    fetch_plans,
    get_equipment_and_plan,
    split_auto_tire_service,
    get_equipment_items,
)
from data_manager import DataManager


class App:
    """
    The main application class for the Apprentice Toolkit.

    This class is responsible for initializing the main window, setting up styles,
    creating all UI frames (screens), and handling the navigation between them.
    """
    def __init__(self, root: tk.Tk):
        """
        Initializes the main application window and all its components.

        Args:
            root (tk.Tk): The root Tkinter window for the application.
        """
        self.root = root
        self.root.title("Toolkit do aprendiz")
        self.root.geometry("990x800")
        self.root.config(bg="#000000")

        try:
            self.data_manager = DataManager()
        except FileNotFoundError as e:
            messagebox.showerror("Erro de Carregamento de Dados", str(e))
            self.root.destroy()
            return

        self.setup_style()

        self.menu_frame = self.create_menu()
        self.processOrders_frame = self.create_processOrders_frame()
        self.processText_frame = self.create_processText_frame()
        self.searchOrders_frame = self.create_searchOrders_frame()
        self.apontamentos_frame = self.create_apontamentos_frame()
        self.workLogs_frame = self.create_workLogs_frame()
        self.autoWorkLogs_frame = self.create_autoWorkLogs_frame()
        self.filters_frame = self.create_filters_frame()
        self.updateLogs_frame = self.create_updateLogs_frame()

        self.show_frame(self.menu_frame)

    def setup_style(self) -> None:
        """
        Configures the application's visual style using ttk.Style.
        """
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "TLabel", background="#2b2b2b", foreground="#ffffff", font=("Arial", 12)
        )
        style.configure(
            "TButton",
            background="#036F18",
            foreground="#ffffff",
            font=("Arial", 12),
            padding=10,
        )
        style.configure("Grande.TButton", font=("Arial", 16), padding=(20, 15))
        style.configure(
            "Custom.TCheckbutton",
            font=("Arial", 8),
            foreground="white",
            background="#036F18",
        )
        style.map(
            "Custom.TCheckbutton",
            foreground=[("active", "red")],
            background=[("active", "#036F18")],
        )
        style.map(
            "TButton",
            background=[("active", "#45a049")],
        )

    def show_frame(self, frame: tk.Frame) -> None:
        """
        Raises a given frame to the top of the stacking order, making it visible.
        """
        frame.tkraise()

    def run_work_logs(self, plan_type: str = "") -> None:
        """
        Handles the logic for the manual work log generation screen.
        """
        try:
            logs = work_logs(
                self.manual_wlog_order.get(),
                self.wlog_interval_input.get("1.0", tk.END),
                self.manual_wlog_date.get(),
                self.manual_wlog_start.get(),
                self.manual_wlog_end.get(),
                plan_type
            )
            self.manual_wlog_output.delete("1.0", tk.END)
            if logs:
                self.manual_wlog_output.insert(tk.END, logs)
        except ValueError as e:
            messagebox.showwarning("Atenção", str(e))

    def run_auto_work_logs(self, plan_type: str = "") -> None:
        """
        Handles the logic for the automatic work log generation screen.
        """
        os_number = self.wlog_order.get().strip()
        date = self.wlog_date.get().strip()
        start_time = self.wlog_start.get().strip()
        end_time = self.wlog_end.get().strip()

        equipment, plan = get_equipment_and_plan(os_number, self.data_manager.df_os)
        if not equipment or not plan:
            messagebox.showwarning("Atenção!", "Ordem de serviço não encontrada!")
            self.wlog_output.delete("1.0", tk.END)
            return

        df_filtered = fetch_plans(equipment, plan, self.data_manager.df_matrix)

        borracharia_list, mecanica_list = split_auto_tire_service(df_filtered)

        if plan_type == "tire_service":
            interval_list = borracharia_list
            if not interval_list:
                messagebox.showwarning("Atenção", "Essa OS não possui nenhuma sequência de borracharia.")
                return
        else:
            interval_list = mecanica_list

        interval_str = " ".join(str(i) for i in interval_list)

        try:
            logs = work_logs(os_number, interval_str, date, start_time, end_time)
            self.wlog_output.delete("1.0", tk.END)
            if logs:
                self.wlog_output.insert(tk.END, logs)
        except ValueError as e:
            messagebox.showwarning("Atenção", str(e))

    def clear_fields(self, *widgets) -> None:
        """
        Clears the content of any number of given Tkinter widgets.
        """
        for widget in widgets:
            if isinstance(widget, (tk.Entry, ttk.Entry)):
                widget.delete(0, tk.END)
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, (tk.BooleanVar, tk.IntVar, tk.StringVar)):
                widget.set(False)

    def create_menu(self) -> tk.Frame:
        """
        Builds and returns the main menu frame.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        label = ttk.Label(frame, text="O que deseja fazer?", font=("Arial", 20))
        label.pack(pady=50)

        ttk.Button(
            frame,
            text="Unir ordens",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.processOrders_frame),
        ).pack(pady=20, ipadx=100, ipady=8)

        ttk.Button(
            frame,
            text="Unir texto",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.processText_frame),
        ).pack(pady=20, ipadx=100, ipady=8)

        ttk.Button(
            frame,
            text="Gerar apontamentos",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.apontamentos_frame),
        ).pack(pady=20, ipadx=72, ipady=8)

        ttk.Button(
            frame,
            text="Procurar ordens",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.searchOrders_frame),
        ).pack(pady=20, ipadx=92, ipady=8)

        ttk.Button(
            frame,
            text="Consulta filtros x frota",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.filters_frame),
        ).pack(pady=20, ipadx=66, ipady=8)

        tk.Button(
            frame,
            text="Notas de atualização",
            bg="#800080",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=lambda: self.show_frame(self.updateLogs_frame)
        ).pack(pady=20, ipadx=30, ipady=10)

        return frame

    def create_processOrders_frame(self) -> tk.Frame:
        """
        Builds and returns the frame for processing service orders.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Digite ou cole as ordens:").pack(padx=10, pady=10)
        self.input_text = tk.Text(frame, height=8, width=80, bg="#3c3f41", fg="#ffffff", font=("Consolas", 12))
        self.input_text.pack(padx=10, pady=10)

        ttk.Label(frame, text="Separador (deixe vazio para virgula):").pack(padx=10, pady=(5, 0))
        self.separator_entry = ttk.Entry(frame, width=10)
        self.separator_entry.pack(padx=10, pady=5)

        ttk.Button(
            frame, text="🔄 Processar",
            command=lambda: process_orders(self.input_text, self.separator_entry, self.output_text)
        ).pack(pady=10)

        ttk.Label(frame, text="Ordens processadas:").pack(padx=10, pady=10)
        self.output_text = tk.Text(frame, height=8, width=80, bg="#3c3f41", fg="#00ff00", font=("Consolas", 12))
        self.output_text.pack(padx=10, pady=10)

        ttk.Button(
            frame, text="📋 Copiar ordens processadas",
            command=lambda: copy_text(self.output_text, self.root), style="Grande.TButton"
        ).pack(pady=20)
        ttk.Button(
            frame, text="⬅ Voltar ao menu",
            command=lambda: (self.clear_fields(self.input_text, self.separator_entry), self.show_frame(self.menu_frame))
        ).pack(pady=10)

        return frame

    def create_processText_frame(self) -> tk.Frame:
        """
        Builds and returns the frame for general text processing.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="""O que deseja unir?\n\nSe o campo "Manter espaços" estiver marcado, o separador será aplicado apenas nas quebras\nde linha, caso contrário, nos espaços também.""").pack(padx=10, pady=10)
        self.ptext_input = tk.Text(frame, height=6, width=100, bg="#3c3f41", fg="#ffffff", font=("Consolas", 12))
        self.ptext_input.pack(padx=10, pady=10)

        ttk.Label(frame, text="Separador (por padrão virgula e espaço, se precisar altere para somente virgula.):").pack(padx=10, pady=(5, 0))
        self.ptext_separator = ttk.Entry(frame, width=10)
        self.ptext_separator.pack(padx=10, pady=5)

        self.space_choice = tk.BooleanVar(value=False)
        self.space_checkbox = ttk.Checkbutton(
            frame, text="Manter espaços", variable=self.space_choice, style="Custom.TCheckbutton"
        )
        self.space_checkbox.pack(pady=5)

        ttk.Button(
            frame, text="🔄 Processar",
            command=lambda: process_text(self.ptext_input, self.ptext_separator, self.space_choice.get(), self.ptext_output)
        ).pack(pady=10)

        ttk.Label(frame, text="Texto processado:").pack(padx=10, pady=10)
        self.ptext_output = tk.Text(frame, height=6, width=100, bg="#3c3f41", fg="#00ff00", font=("Consolas", 12))
        self.ptext_output.pack(padx=10, pady=10)

        ttk.Button(
            frame, text="📋 Copiar o texto processado",
            command=lambda: copy_text(self.ptext_output, self.root), style="Grande.TButton"
        ).pack(pady=10)
        ttk.Button(
            frame, text="⬅ Voltar ao menu",
            command=lambda: (self.clear_fields(self.ptext_input, self.ptext_separator, self.space_choice), self.show_frame(self.menu_frame))
        ).pack(pady=10)

        return frame

    def create_apontamentos_frame(self) -> tk.Frame:
        """
        Builds a sub-menu frame for choosing the work log generation mode.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Escolha o modo de geração de apontamentos:", font=("Arial", 20)).pack(pady=50)

        ttk.Button(frame, text="Manual", style="Grande.TButton", command=lambda: self.show_frame(self.workLogs_frame)).pack(pady=20, ipadx=100, ipady=10)
        ttk.Button(frame, text="Automático", style="Grande.TButton", command=lambda: self.show_frame(self.autoWorkLogs_frame)).pack(pady=20, ipadx=100, ipady=10)
        ttk.Button(frame, text="⬅ Voltar ao menu", command=lambda: self.show_frame(self.menu_frame)).pack(pady=40)

        return frame

    def create_workLogs_frame(self) -> tk.Frame:
        """
        Builds and returns the frame for MANUAL work log generation.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Ordem de serviço:").pack(padx=10, pady=5)
        self.manual_wlog_order = ttk.Entry(frame, width=30)
        self.manual_wlog_order.pack(padx=10, pady=5)

        ttk.Label(frame, text="Insira o intervalo de sequências (e.g., 1-5 or one per line):").pack(padx=10, pady=5)

        frame_interval = tk.Frame(frame, bg="#2b2b2b")
        frame_interval.pack(pady=5)
        self.wlog_interval_input = tk.Text(frame_interval, height=1, width=15, bg="#3c3f41", fg="#00ff00", font=("Consolas", 12))
        self.wlog_interval_input.pack(side="left", padx=(0, 5))
        ttk.Button(frame_interval, text="🧹 Limpar intervalo", command=lambda: self.wlog_interval_input.delete("1.0", tk.END)).pack(side="left")

        ttk.Label(frame, text="Data (dd/mm/aaaa):").pack(padx=10, pady=5)
        self.manual_wlog_date = ttk.Entry(frame, width=30)
        self.manual_wlog_date.pack(padx=10, pady=5)

        ttk.Label(frame, text="Hora inicial (hh:mm):").pack(padx=10, pady=5)
        self.manual_wlog_start = ttk.Entry(frame, width=30)
        self.manual_wlog_start.pack(padx=10, pady=5)

        ttk.Label(frame, text="Hora final (hh:mm):").pack(padx=10, pady=5)
        self.manual_wlog_end = ttk.Entry(frame, width=30)
        self.manual_wlog_end.pack(padx=10, pady=5)

        button_frame = tk.Frame(frame, bg="#2b2b2b")
        button_frame.pack(pady=10, fill="x")
        ttk.Button(button_frame, text="⚙️ Gerar apontamentos gerais", command=self.run_work_logs, style="Grande.TButton").pack(side="left", expand=True, fill="x", padx=(10,5))
        ttk.Button(button_frame, text="⚙️ Gerar apontamentos da borracharia", command=lambda: self.run_work_logs("tire_service"), style="Grande.TButton").pack(side="left", expand=True, fill="x", padx=(5,10))

        ttk.Label(frame, text="Apontamentos:").pack(padx=10, pady=5)
        self.manual_wlog_output = tk.Text(frame, height=5, width=100, bg="#3c3f41", fg="#00ff00", font=("Consolas", 12))
        self.manual_wlog_output.pack(padx=10, pady=10)

        ttk.Button(frame, text="📋 Copiar apontamentos", command=lambda: copy_text(self.manual_wlog_output, self.root), style="Grande.TButton").pack(pady=5)
        ttk.Button(
            frame, text="⬅ Voltar ao menu",
            command=lambda: (self.clear_fields(self.manual_wlog_order, self.wlog_interval_input, self.manual_wlog_date, self.manual_wlog_start, self.manual_wlog_end), self.show_frame(self.menu_frame))
        ).pack(pady=10)

        return frame

    def create_autoWorkLogs_frame(self) -> tk.Frame:
        """
        Builds and returns the frame for AUTOMATIC work log generation.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Ordem de serviço:").pack(padx=10, pady=5)
        self.wlog_order = ttk.Entry(frame, width=30)
        self.wlog_order.pack(padx=10, pady=15)

        ttk.Label(frame, text="Data (dd/mm/aaaa):").pack(padx=10, pady=5)
        self.wlog_date = ttk.Entry(frame, width=30)
        self.wlog_date.pack(padx=10, pady=15)

        ttk.Label(frame, text="Hora inicial (hh:mm):").pack(padx=10, pady=5)
        self.wlog_start = ttk.Entry(frame, width=30)
        self.wlog_start.pack(padx=10, pady=15)

        ttk.Label(frame, text="Hora final (hh:mm):").pack(padx=10, pady=5)
        self.wlog_end = ttk.Entry(frame, width=30)
        self.wlog_end.pack(padx=10, pady=15)

        button_frame = tk.Frame(frame, bg="#2b2b2b")
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Serviço geral", command=self.run_auto_work_logs, style="Grande.TButton").pack(side="left", pady=10)
        ttk.Button(button_frame, text="Borracharia", command=lambda: self.run_auto_work_logs("tire_service"), style="Grande.TButton").pack(side="left", padx=30, pady=10)

        ttk.Label(frame, text="Apontamentos:").pack(padx=10, pady=5)
        self.wlog_output = tk.Text(frame, height=5, width=100, bg="#3c3f41", fg="#00ff00", font=("Consolas", 12))
        self.wlog_output.pack(padx=10, pady=10)

        ttk.Button(frame, text="📋 Copiar apontamentos", command=lambda: copy_text(self.wlog_output, self.root), style="Grande.TButton").pack(pady=5)
        ttk.Button(
            frame, text="⬅ Voltar ao menu",
            command=lambda: (self.clear_fields(self.wlog_order, self.wlog_date, self.wlog_start, self.wlog_end), self.show_frame(self.menu_frame))
        ).pack(pady=10)

        return frame

    def create_searchOrders_frame(self) -> tk.Frame:
        """
        Builds and returns the frame for searching service orders.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Insira o texto aqui: ").pack(padx=10, pady=10)
        self.search_input = tk.Text(frame, height=10, width=100, bg="#3c3f41", fg="#ffffff", font=("Consolas", 12))
        self.search_input.pack(padx=10, pady=10)

        ttk.Button(
            frame, text="🔍 Encontrar ordens",
            command=lambda: search_orders(self.search_input, self.search_output, self.number_of_lines)
        ).pack(pady=10)

        ttk.Label(frame, text="Ordens encontradas:").pack(padx=10, pady=10)
        self.search_output = tk.Text(frame, height=10, width=100, bg="#3c3f41", fg="#00ff00", font=("Consolas", 12))
        self.search_output.pack(padx=10, pady=10)

        self.number_of_lines = tk.Label(frame, text="Quantidade de ordens encontradas: 0", bg="#2b2b2b", fg="#ff00bb", font=("Consolas", 12), anchor="w")
        self.number_of_lines.pack(padx=10, pady=10)

        ttk.Button(
            frame, text="📋 Copiar ordens encontradas",
            command=lambda: copy_text(self.search_output, self.root), style="Grande.TButton"
        ).pack(pady=10)
        ttk.Button(
            frame, text="⬅ Voltar ao menu",
            command=lambda: (self.clear_fields(self.search_input), self.show_frame(self.menu_frame))
        ).pack(pady=10)

        return frame

    def create_updateLogs_frame(self) -> tk.Frame:
        """
        Builds and returns the frame for displaying update/changelog notes.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        tk.Label(frame, text="Confira o que mudou desde a última versão: ", bg="#2b2b2b", fg="#a20290", font=("Segoe UI", 15, "bold")).pack(padx=10, pady=50)

        changelog_text = """
- 🛠️ Adicionado suporte a multiplos intervalos para a geração de apontamentos.
- 🛠️ Adicionado suporte ao plano de manutenção para a geração de apontamentos.
- 🛠️ Adicionado contador de OS a função de procurar ordens.
- 🛠️ Melhorias na compatibilidade do design geral.
- 🛠️ Melhorias de qualidade de vida.
        """
        update_output = tk.Message(frame, text=changelog_text, width=800, bg="#2b2b2b", fg="#da9ad3", font=("Consolas", 15))
        update_output.pack(padx=20, pady=40)

        ttk.Button(frame, text="⬅ Voltar ao menu", command=lambda: self.show_frame(self.menu_frame)).pack(pady=10, ipady=15, ipadx=30)

        return frame

    def run_filters_search(self) -> None:
        """
        Handles the logic for the "Consulta filtros x frota" screen.
        """
        choice = self.equipment_to_use.get()

        try:
            choice = int(choice)
        except ValueError:
            messagebox.showwarning("Atenção", "Por favor, insira apenas valores numéricos.")
            return

        try:
            itens_result_df = get_equipment_items(choice, self.data_manager.bd_filters, self.data_manager.stock, self.data_manager.itens_prices)
        except ValueError as e:
            messagebox.showwarning("Atenção", str(e))
            return

        if itens_result_df is None or itens_result_df.empty:
            self.filters_output.config(state="normal")
            self.filters_output.delete("1.0", tk.END)
            self.filters_output.config(state="disabled")
            return

        itens_result_str = itens_result_df.to_string(index=False)
        itens_rows = itens_result_str.strip().split("\n")

        self.filters_output.config(state="normal")
        self.filters_output.delete("1.0", tk.END)

        for i, row in enumerate(itens_rows):
            if i == 0:
                tag_to_use = "first_row"
            elif i % 2 == 0:
                tag_to_use = "even_row"
            else:
                tag_to_use = "odd_row"
            self.filters_output.insert(tk.END, row + "\n", tag_to_use)

        self.filters_output.config(state="disabled")

    def create_filters_frame(self) -> tk.Frame:
        """
        Builds and returns the frame for querying equipment filters by fleet number.
        """
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        label = ttk.Label(frame, text="Insira a frota do equipamento: ", font=("Arial", 20))
        label.pack(pady=20)
        self.equipment_to_use = ttk.Entry(frame, width=25)
        self.equipment_to_use.pack(pady=0)

        self.filters_output = tk.Text(
            frame, height=27, width=120, bg="#3c3f41", font=("Consolas", 12),
            state="disabled", selectbackground="lightblue", selectforeground="black"
        )
        self.filters_output.bind("<1>", lambda event: self.filters_output.focus_set())

        self.filters_output.tag_configure("first_row", background="#2b2b2b", foreground="#da46f4", font=("Consolas", 11))
        self.filters_output.tag_configure("odd_row", background="#3c3f41", foreground="#ffffff", font=("Consolas", 11))
        self.filters_output.tag_configure("even_row", background="#2b2b2b", foreground="#ffffff", font=("Consolas", 11))
        self.filters_output.tag_raise("sel")

        ttk.Button(frame, text="Procurar", command=self.run_filters_search).pack(pady=10)
        self.filters_output.pack(padx=10, pady=10)
        ttk.Button(frame, text="⬅ Voltar ao menu", command=lambda: self.show_frame(self.menu_frame)).pack(pady=10)

        self.equipment_to_use.bind("<Return>", lambda event: self.run_filters_search())

        return frame

# --- Main Execution Block ---
if __name__ == "__main__":
    """
    Entry point of the application.
    """
    root = tk.Tk()
    app = App(root)
    root.mainloop()
