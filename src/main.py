import tkinter as tk
from game import Game
from tv_panel import TVPanel
from admin_panel import AdminPanel

try:
    from sound_manager import SoundManager
except ImportError:
    SoundManager = None

def main():
    """Główny punkt wejścia do aplikacji Familiada."""
    root = tk.Tk()
    game = Game()
    # Przykładowe pytania
    game.add_question("Podaj popularne imiona w Polsce", [
        ("Jan", 35),
        ("Anna", 30),
        ("Piotr", 20),
        ("Katarzyna", 10),
        ("Andrzej", 5)
    ])
    game.add_question("Wymień przysmaki na weselu", [
        ("Sałatka jarzynowa", 40),
        ("Rolada", 30),
        ("Pasztet", 20),
        ("Śledzie", 10)
    ])

    sound_manager = SoundManager() if SoundManager is not None else None
    tv_panel = TVPanel(root, game, sound_manager)
    admin_panel = AdminPanel(root, game, tv_panel, sound_manager)

    admin_panel.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
