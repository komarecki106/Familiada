import pygame
from utils import resource_path

class SoundManager:
    """
    Klasa do zarządzania dźwiękami w aplikacji.
    """
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        """Ładuje dźwięki z plików znajdujących się w folderze assets."""
        try:
            self.sounds['start'] = pygame.mixer.Sound(resource_path("intro1.mp3"))
        except Exception as e:
            print("Błąd przy ładowaniu start_sound:", e)
            self.sounds['start'] = None
        try:
            self.sounds['question_intro'] = pygame.mixer.Sound(resource_path("intro.mp3"))
        except Exception as e:
            print("Błąd przy ładowaniu question_intro_sound:", e)
            self.sounds['question_intro'] = None
        try:
            self.sounds['reveal'] = pygame.mixer.Sound(resource_path("ok.mp3"))
        except Exception as e:
            print("Błąd przy ładowaniu reveal_sound:", e)
            self.sounds['reveal'] = None
        try:
            self.sounds['error'] = pygame.mixer.Sound(resource_path("error.mp3"))
        except Exception as e:
            print("Błąd przy ładowaniu error_sound:", e)
            self.sounds['error'] = None

    def play(self, sound_name):
        """
        Odtwarza dźwięk o podanej nazwie.

        Args:
            sound_name (str): Nazwa dźwięku.
        """
        sound = self.sounds.get(sound_name)
        if sound:
            sound.play()
