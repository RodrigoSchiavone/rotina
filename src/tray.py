import threading
from PIL import Image, ImageDraw
import pystray


def criar_imagem_icone():
    """Gera uma imagem simples para o ícone caso você não tenha um arquivo .ico/png."""
    largura = 64
    altura = 64
    imagem = Image.new("RGB", (largura, altura), color=(30, 144, 255))
    draw = ImageDraw.Draw(imagem)
    draw.rectangle(
        (16, 16, largura - 16, altura - 16), fill=(255, 255, 255)
    )
    return imagem


class TrayIcone:

    def __init__(self, callback_abrir, callback_sair):
        self.callback_abrir = callback_abrir
        self.callback_sair = callback_sair
        self.icone = None

    def iniciar(self):
        imagem = criar_imagem_icone()
        menu = pystray.Menu(
            pystray.MenuItem("Abrir Agendador", self._on_abrir),
            pystray.MenuItem("Sair Definitivamente", self._on_sair),
        )
        self.icone = pystray.Icon("AgendadorPython", imagem, "Agendador de Tarefas", menu)
        
        # Roda em uma thread paralela para não travar a interface
        thread = threading.Thread(target=self.icone.run, daemon=True)
        thread.start()

    def _on_abrir(self, icon, item):
        self.callback_abrir()

    def _on_sair(self, icon, item):
        self.icone.stop()
        self.callback_sair()