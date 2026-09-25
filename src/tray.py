import os
import sys
import threading
from PIL import Image, ImageDraw
import pystray


def obter_caminho_recurso(caminho_relativo):
    """Obtém o caminho absoluto para recursos, funcionando em dev e no .exe do PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, caminho_relativo)


def carregar_imagem_icone():
    caminho_ico = obter_caminho_recurso(os.path.join("assets", "icon.ico"))
    if os.path.exists(caminho_ico):
        try:
            return Image.open(caminho_ico)
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

    # Fallback caso não encontre o arquivo assets/icon.ico
    largura = 64
    altura = 64
    imagem = Image.new("RGB", (largura, altura), color=(30, 144, 255))
    draw = ImageDraw.Draw(imagem)
    draw.rectangle((16, 16, largura - 16, altura - 16), fill=(255, 255, 255))
    return imagem


class TrayIcone:

    def __init__(self, callback_abrir, callback_sair):
        self.callback_abrir = callback_abrir
        self.callback_sair = callback_sair
        self.icone = None

    def iniciar(self):
        imagem = carregar_imagem_icone()
        menu = pystray.Menu(
            pystray.MenuItem("Abrir Rotina", self._on_abrir),
            pystray.MenuItem("Sair Definitivamente", self._on_sair),
        )
        self.icone = pystray.Icon("RotinaApp", imagem, "Rotina - Agendador", menu)

        thread = threading.Thread(target=self.icone.run, daemon=True)
        thread.start()

    def _on_abrir(self, icon, item):
        self.callback_abrir()

    def _on_sair(self, icon, item):
        self.icone.stop()
        self.callback_sair()