import tkinter as tk
from tkinter import ttk
from functions import (
    process_orders,
    process_text,
    search_orders,
    copy_text,
    work_logs,
)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Toolkit do aprendiz")
        self.root.geometry("900x800")
        self.root.config(bg="#000000")

        self.setup_style()

        # Creating frames
        self.menu_frame = self.create_menu()
        self.processOrders_frame = self.create_processOrders_frame()
        self.processText_frame = self.create_processText_frame()
        self.searchOrders_frame = self.create_searchOrders_frame()
        self.workLogs_frame = self.create_workLogs_frame()
        self.updateLogs_frame = self.create_updateLogs_frame()

        self.show_frame(self.menu_frame)

        # General style

    def setup_style(self):
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
        # Frame raiser

    def show_frame(self, frame):
        frame.tkraise()

    def interval_frame(self, iframe):
        iframe.tkraise()

        # Menu config

    def clear_fields(
        self, *widgets
    ):  # Used to clear all the input fields when the user clicks on the menu button
        for widget in widgets:
            if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, (tk.BooleanVar, tk.IntVar, tk.StringVar)):
                widget.set(False)

    def create_menu(self):
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        label = ttk.Label(frame, text="O que deseja fazer?", font=("Arial", 20))
        label.pack(pady=50)

        ttk.Button(
            frame,
            text="Unir ordens",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.processOrders_frame),
        ).pack(pady=20, ipadx=100, ipady=10)

        ttk.Button(
            frame,
            text="Unir texto",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.processText_frame),
        ).pack(pady=20, ipadx=100, ipady=10)

        ttk.Button(
            frame,
            text="Apontamentos automatizados",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.workLogs_frame),
        ).pack(pady=20, ipadx=30, ipady=10)

        ttk.Button(
            frame,
            text="Procurar ordens",
            style="Grande.TButton",
            command=lambda: self.show_frame(self.searchOrders_frame),
        ).pack(pady=20, ipadx=92, ipady=10)

        tk.Button(
            frame,
            text="Notas de atualização",
            bg="#800080",  # Fundo roxo
            fg="white",    # Texto branco
            font=("Segoe UI", 10, "bold"),
            command=lambda: self.show_frame(self.updateLogs_frame)
            ).pack(pady=20, ipadx=30, ipady=10)

        return frame

        # process orders gui

    def create_processOrders_frame(self):
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Digite ou cole as ordens:").pack(padx=10, pady=10)

        self.input_text = tk.Text(
            frame,
            height=8,
            width=80,
            bg="#3c3f41",
            fg="#ffffff",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.input_text.pack(padx=10, pady=10)

        ttk.Label(frame, text="Separador (deixe vazio para virgula):").pack(
            padx=10, pady=(5, 0)
        )
        self.separator_entry = ttk.Entry(frame, width=10)
        self.separator_entry.pack(padx=10, pady=5)

        ttk.Button(
            frame,
            text="🔄 Processar",
            command=lambda: process_orders(
                self.input_text, self.separator_entry, self.output_text
            ),
        ).pack(pady=10)

        ttk.Label(frame, text="Ordens processadas:").pack(padx=10, pady=10)

        self.output_text = tk.Text(
            frame,
            height=8,
            width=80,
            bg="#3c3f41",
            fg="#00ff00",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.output_text.pack(padx=10, pady=10)

        ttk.Button(
            frame,
            text="📋 Copiar ordens processadas",
            command=lambda: copy_text(self.output_text, self.root),
            style="Grande.TButton",
        ).pack(pady=20)

        ttk.Button(
            frame,
            text="⬅ Voltar ao menu",
            command=lambda: (
                self.clear_fields(self.input_text, self.separator_entry),
                self.show_frame(self.menu_frame),
            ),
        ).pack(pady=10)

        return frame

    def create_processText_frame(self):
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(
            frame,
            text="""                                                            O que deseja unir?

        Se o campo "Manter espaços" estiver marcado, o separador será aplicado apenas nas quebras
        de linha, caso contrário, nos espaços também.""",
        ).pack(padx=10, pady=10)

        self.ptext_input = tk.Text(
            frame,
            height=8,
            width=100,
            bg="#3c3f41",
            fg="#ffffff",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.ptext_input.pack(padx=10, pady=10)

        # separator input
        ttk.Label(
            frame,
            text="Separador (por padrão virgula e espaço, se precisar altere para somente virgula.):",
        ).pack(padx=10, pady=(5, 0))
        self.ptext_separator = ttk.Entry(frame, width=10)
        self.ptext_separator.pack(padx=10, pady=5)

        # checkbox to keep spaces or not
        self.space_choice = tk.BooleanVar(
            value=False
        )  # Idk why but this is returning True by default
        self.space_checkbox = ttk.Checkbutton(  # wont touch it since its working tho
            frame,
            text="Manter espaços",
            variable=self.space_choice,
            style="Custom.TCheckbutton",
        )
        self.space_checkbox.pack(pady=5)

        ttk.Button(
            frame,
            text="🔄 Processar",
            command=lambda: process_text(
                self.ptext_input,
                self.ptext_separator,
                self.space_choice.get(),
                self.ptext_output,
            ),
        ).pack(pady=(10))

        ttk.Label(frame, text="Texto processado:").pack(padx=10, pady=10)

        self.ptext_output = tk.Text(
            frame,
            height=8,
            width=100,
            bg="#3c3f41",
            fg="#00ff00",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.ptext_output.pack(padx=10, pady=10)

        ttk.Button(
            frame,
            text="📋 Copiar o texto processado",
            command=lambda: copy_text(self.ptext_output, self.root),
            style="Grande.TButton",
        ).pack(pady=10)

        ttk.Button(
            frame,
            text="⬅ Voltar ao menu",
            command=lambda: (
                self.clear_fields(
                    self.ptext_input,
                    self.ptext_separator,
                    self.space_choice,
                ),
                self.show_frame(self.menu_frame),
            ),
        ).pack(pady=10)

        return frame

    def create_workLogs_frame(self):
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Ordem de serviço:").pack(padx=10, pady=5)
        self.wlog_order = ttk.Entry(frame, width=30)
        self.wlog_order.pack(padx=10, pady=5)

        ttk.Label(
            frame,
            text="Insira o intervalo de sequências nessa caixinha, separados por um traço (1-5) ou copiadas do excel (uma sequencia por linha)",
        ).pack(padx=10, pady=5)

        frame_interval = tk.Frame(
            frame, bg="#2b2b2b"
        )  # custom frame used to clear the interval input
        frame_interval.pack(pady=5)

        self.wlog_interval_input = tk.Text(
            frame_interval,
            height=1,
            width=15,
            bg="#3c3f41",
            fg="#00ff00",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.wlog_interval_input.pack(side="left", padx=(0, 5))

        ttk.Button(
            frame_interval,
            text="🧹 Limpar intervalo",
            command=lambda: self.wlog_interval_input.delete("1.0", tk.END),
        ).pack(side="left")

        ttk.Label(frame, text="Data (dd/mm/aaaa):").pack(padx=10, pady=5)
        self.wlog_date = ttk.Entry(frame, width=30)
        self.wlog_date.pack(padx=10, pady=5)

        ttk.Label(frame, text="Hora inicial (hh:mm):").pack(padx=10, pady=5)
        self.wlog_start = ttk.Entry(frame, width=30)
        self.wlog_start.pack(padx=10, pady=5)

        ttk.Label(frame, text="Hora final (hh:mm):").pack(padx=10, pady=5)
        self.wlog_end = ttk.Entry(frame, width=30)
        self.wlog_end.pack(padx=10, pady=5)

        ttk.Button(
            frame,
            text="⚙️ Gerar apontamentos",
            command=self.run_work_logs,
            style="Grande.TButton",
        ).pack(pady=20)

        ttk.Label(frame, text="Apontamentos:").pack(padx=10, pady=5)

        self.wlog_output = tk.Text(
            frame,
            height=9,
            width=100,
            bg="#3c3f41",
            fg="#00ff00",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.wlog_output.pack(padx=10, pady=10)

        ttk.Button(
            frame,
            text="📋 Copiar apontamentos",
            command=lambda: copy_text(self.wlog_output, self.root),
            style="Grande.TButton",
        ).pack(pady=5)

        ttk.Button(
            frame,
            text="⬅ Voltar ao menu",
            command=lambda: (
                self.clear_fields(
                    self.wlog_order,
                    self.wlog_interval_input,
                    self.wlog_date,
                    self.wlog_start,
                    self.wlog_end,
                ),
                self.show_frame(self.menu_frame),
            ),
        ).pack(pady=10)

        return frame

    def run_work_logs(self):
        logs = work_logs(
            self.wlog_order.get(),
            self.wlog_interval_input.get("1.0", tk.END),
            self.wlog_date.get(),
            self.wlog_start.get(),
            self.wlog_end.get(),
        )
        self.wlog_output.delete("1.0", tk.END)
        self.wlog_output.insert(tk.END, logs)

    # search orders gui
    def create_searchOrders_frame(self):
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        ttk.Label(frame, text="Joga o textão confuso ai:").pack(padx=10, pady=10)

        self.search_input = tk.Text(
            frame,
            height=10,
            width=100,
            bg="#3c3f41",
            fg="#ffffff",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.search_input.pack(padx=10, pady=10)

        ttk.Button(
            frame,
            text="🔍 Encontrar ordens",
            command=lambda: search_orders(self.search_input, self.search_output),
        ).pack(pady=10)

        ttk.Label(frame, text="Ordens encontradas:").pack(padx=10, pady=10)

        self.search_output = tk.Text(
            frame,
            height=10,
            width=100,
            bg="#3c3f41",
            fg="#00ff00",
            insertbackground="white",
            font=("Consolas", 12),
            wrap="word",
        )
        self.search_output.pack(padx=10, pady=10)

        ttk.Button(
            frame,
            text="📋 Copiar ordens encontradas",
            command=lambda: copy_text(self.search_output, self.root),
            style="Grande.TButton",
        ).pack(pady=10)

        ttk.Button(
            frame,
            text="⬅ Voltar ao menu",
            command=lambda: (
                self.clear_fields(self.search_input),
                self.show_frame(self.menu_frame),
            ),
        ).pack(pady=10)

        return frame

    def create_updateLogs_frame(self):
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relwidth=1, relheight=1)

        tk.Label(
            frame, 
            text="Essas são as mudanças que ocorreram desde a última versão: ",
            bg="#2b2b2b",
            fg="#a20290",
            font=("Segoe UI", 15, "bold"),
            ).pack(padx=10, pady=50)
        

        changelog_text = """
- 🛠️ Adicionado suporte à datas em formatação alternativa (sem as barras "/").

- 🛠️ Adicionado suporte à horários em formatação alternativa (sem os dois pontos ":").

- 🆕 Melhorias visuais implementadas.

- 🆕 Seção "Notas de atualização" implementada.

- 🆕 O programa agora possui um novo icone!

- 🚀 Correções de pequenos erros e melhorias de qualidade de vida.

        """

        texto_exibicao = tk.Message(
        frame,
        text=changelog_text,
        width=800,
        bg="#2b2b2b",
        fg="#a20290",
        font=("Consolas", 15),
        )
        texto_exibicao.pack(padx=20, pady=40)

        ttk.Button(
            frame,
            text="⬅ Voltar ao menu",
            command=lambda: (
                self.show_frame(self.menu_frame),
            ),
        ).pack(pady=10)

        return frame


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
