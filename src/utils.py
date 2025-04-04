import os
import sys

def resource_path(filename):
    """
    Zwraca poprawną ścieżkę do plików zasobów w folderze assets.

    Args:
        filename (str): Nazwa pliku zasobów.

    Returns:
        str: Pełna ścieżka do pliku.
    """
    if getattr(sys, 'frozen', False):  # aplikacja spakowana przez PyInstaller
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "assets", filename)
