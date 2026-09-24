import json
import os
import subprocess
import threading
import time
from datetime import datetime
import schedule

ARQUIVO_JSON = "agendamentos.json"


class GerenciadorTarefas:

    def __init__(self):
        self.agendamentos = []
        self.rodando = False
        self.thread_loop = None
        self.carregar_agendamentos()

    def carregar_agendamentos(self):
        if os.path.exists(ARQUIVO_JSON):
            try:
                with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
                    self.agendamentos = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar JSON: {e}")
                self.agendamentos = []
        else:
            self.agendamentos = []

    def salvar_agendamentos(self):
        with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
            json.dump(self.agendamentos, f, indent=4, ensure_ascii=False)
        self.reconfigurar_agenda()

    def adicionar_agendamento(
        self, nome, caminho_executavel, frequencia, horarios, dia_semana=None
    ):
        # horarios deve ser uma lista de strings HH:MM, ex: ["08:00", "14:30"]
        novo = {
            "id": int(time.time()),
            "nome": nome,
            "caminho": caminho_executavel,
            "frequencia": frequencia,  # "Uma vez", "Diariamente", "Semanalmente", "Mensalmente"
            "horarios": horarios,
            "dia_semana": dia_semana,  # Usado se for semanal (ex: "segunda")
            "ativo": True,
        }
        self.agendamentos.append(novo)
        self.salvar_agendamentos()

    def excluir_agendamento(self, id_tarefa):
        self.agendamentos = [
            t for t in self.agendamentos if t["id"] != id_tarefa
        ]
        self.salvar_agendamentos()

    def _executar_programa(self, caminho):
        try:
            subprocess.Popen(caminho, shell=True)
            print(f"[{datetime.now()}] Executado com sucesso: {caminho}")
        except Exception as e:
            print(f"Erro ao executar {caminho}: {e}")

    def reconfigurar_agenda(self):
        """Limpa o agendador e recarrega as regras a partir do JSON."""
        schedule.clear()

        for t in self.agendamentos:
            if not t.get("ativo", True):
                continue

            caminho = t["caminho"]
            freq = t["frequencia"]
            horarios = t.get("horarios", [])

            for h in horarios:
                if freq == "Diariamente":
                    schedule.every().day.at(h).do(
                        self._executar_programa, caminho
                    )
                elif freq == "Semanalmente" and t.get("dia_semana"):
                    dia = t["dia_semana"].lower()
                    if hasattr(schedule.every(), dia):
                        getattr(schedule.every(), dia).at(h).do(
                            self._executar_programa, caminho
                        )
                elif freq == "Uma vez":
                    # Para 'Uma vez', checa o horário e desativa após executar
                    schedule.every().day.at(h).do(
                        self._executar_uma_vez, t["id"], caminho
                    )

    def _executar_uma_vez(self, id_tarefa, caminho):
        self._executar_programa(caminho)
        # Desativa a tarefa para não rodar novamente
        for t in self.agendamentos:
            if t["id"] == id_tarefa:
                t["ativo"] = False
                break
        self.salvar_agendamentos()

    def iniciar(self):
        if not self.rodando:
            self.rodando = True
            self.reconfigurar_agenda()
            self.thread_loop = threading.Thread(
                target=self._loop_agendador, daemon=True
            )
            self.thread_loop.start()

    def _loop_agendador(self):
        while self.rodando:
            schedule.run_pending()
            time.sleep(1)

    def parar(self):
        self.rodando = False