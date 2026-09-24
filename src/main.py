from tkinter import filedialog, messagebox
import customtkinter as ctk
from gerenciador import GerenciadorTarefas
from tray import TrayIcone

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AppAgendador(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Meu Agendador de Tarefas")
        self.geometry("650x500")

        self.gerenciador = GerenciadorTarefas()
        self.gerenciador.iniciar()

        # Configurar interceptação do botão Fechar (X)
        self.protocol("WM_DELETE_WINDOW", self.esconder_janela)

        # Configurar Ícone na Bandeja
        self.tray = TrayIcone(
            callback_abrir=self.mostrar_janela, callback_sair=self.encerrar_app
        )
        self.tray.iniciar()

        self.criar_interface()

    def criar_interface(self):
        # Layout Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Cabeçalho / Botão Criar
        frame_topo = ctk.CTkFrame(self)
        frame_topo.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        btn_novo = ctk.CTkButton(
            frame_topo,
            text="+ Novo Agendamento",
            command=self.abrir_dialogo_novo,
        )
        btn_novo.pack(side="left", padx=10, pady=10)

        label_info = ctk.CTkLabel(
            frame_topo, text="Ao fechar no X, o app continua na bandeja."
        )
        label_info.pack(side="right", padx=10)

        # Lista de Agendamentos
        self.scroll_lista = ctk.CTkScrollableFrame(
            self, label_text="Agendamentos Cadastrados"
        )
        self.scroll_lista.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
        )

        self.atualizar_lista_gui()

    def atualizar_lista_gui(self):
        # Limpa widgets antigos
        for widget in self.scroll_lista.winfo_children():
            widget.destroy()

        agendamentos = self.gerenciador.agendamentos

        if not agendamentos:
            lbl = ctk.CTkLabel(
                self.scroll_lista, text="Nenhum agendamento cadastrado."
            )
            lbl.pack(pady=20)
            return

        for item in agendamentos:
            card = ctk.CTkFrame(self.scroll_lista)
            card.pack(fill="x", padx=5, pady=5)

            info_texto = f"📌 {item['nome']}\nFrequência: {item['frequencia']} | Horários: {', '.join(item['horarios'])}\nCaminho: {item['caminho']}"

            lbl = ctk.CTkLabel(card, text=info_texto, justify="left")
            lbl.pack(side="left", padx=10, pady=5)

            btn_excluir = ctk.CTkButton(
                card,
                text="Excluir",
                fg_color="red",
                hover_color="darkred",
                width=60,
                command=lambda id_t=item["id"]: self.excluir_item(id_t),
            )
            btn_excluir.pack(side="right", padx=10, pady=5)

    def excluir_item(self, id_tarefa):
        self.gerenciador.excluir_agendamento(id_tarefa)
        self.atualizar_lista_gui()

    def abrir_dialogo_novo(self):
        JanelaNovoAgendamento(self, self.salvar_novo_agendamento)

    def salvar_novo_agendamento(
        self, nome, caminho, frequencia, horarios, dia_semana
    ):
        self.gerenciador.adicionar_agendamento(
            nome, caminho, frequencia, horarios, dia_semana
        )
        self.atualizar_lista_gui()

    def esconder_janela(self):
        self.withdraw()  # Esconde a janela sem fechar o processo

    def mostrar_janela(self):
        self.deiconify()  # Restaura a janela
        self.focus_force()

    def encerrar_app(self):
        self.gerenciador.parar()
        self.destroy()


class JanelaNovoAgendamento(ctk.CTkToplevel):

    def __init__(self, parent, callback_salvar):
        super().__init__(parent)
        self.callback_salvar = callback_salvar

        self.title("Novo Agendamento")
        self.geometry("450x450")
        self.grab_set()  # Torna a janela modal

        # Nome
        ctk.CTkLabel(self, text="Nome do Agendamento:").pack(
            anchor="w", padx=20, pady=(10, 0)
        )
        self.txt_nome = ctk.CTkEntry(self, width=400)
        self.txt_nome.pack(padx=20, pady=5)

        # Executável
        ctk.CTkLabel(self, text="Caminho do Programa/Script:").pack(
            anchor="w", padx=20, pady=(5, 0)
        )
        frame_caminho = ctk.CTkFrame(self, fg_color="transparent")
        frame_caminho.pack(fill="x", padx=20, pady=5)

        self.txt_caminho = ctk.CTkEntry(frame_caminho, width=300)
        self.txt_caminho.pack(side="left")

        btn_buscar = ctk.CTkButton(
            frame_caminho,
            text="Buscar",
            width=80,
            command=self.selecionar_arquivo,
        )
        btn_buscar.pack(side="right")

        # Frequência
        ctk.CTkLabel(self, text="Frequência:").pack(
            anchor="w", padx=20, pady=(5, 0)
        )
        self.combo_freq = ctk.CTkComboBox(
            self,
            values=["Diariamente", "Uma vez", "Semanalmente"],
            width=400,
        )
        self.combo_freq.pack(padx=20, pady=5)

        # Horários (separados por vírgula)
        ctk.CTkLabel(
            self, text="Horários (formato HH:MM, separados por vírgula):"
        ).pack(anchor="w", padx=20, pady=(5, 0))
        self.txt_horarios = ctk.CTkEntry(
            self, width=400, placeholder_text="Ex: 08:00, 13:30, 18:00"
        )
        self.txt_horarios.pack(padx=20, pady=5)

        # Botão Salvar
        btn_salvar = ctk.CTkButton(
            self,
            text="Salvar Agendamento",
            command=self.confirmar_salvamento,
        )
        btn_salvar.pack(pady=20)

    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o executável ou script",
            filetypes=[("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.txt_caminho.delete(0, "end")
            self.txt_caminho.insert(0, caminho)

    def confirmar_salvamento(self):
        nome = self.txt_nome.get().strip()
        caminho = self.txt_caminho.get().strip()
        freq = self.combo_freq.get()
        horarios_raw = self.txt_horarios.get().strip()

        if not nome or not caminho or not horarios_raw:
            messagebox.showerror(
                "Erro", "Preencha todos os campos obrigatórios."
            )
            return

        horarios = [h.strip() for h in horarios_raw.split(",") if h.strip()]

        self.callback_salvar(nome, caminho, freq, horarios, None)
        self.destroy()


if __name__ == "__main__":
    app = AppAgendador()
    app.mainloop()