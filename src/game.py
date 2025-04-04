import json
import os
import logging
from tkinter import messagebox

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Game:
    """
    Klasa zarządzająca logiką gry Familiada.
    """
    def __init__(self):
        self.questions = []  # lista pytań
        self.current_question = None
        self.current_question_index = None
        self.team1_mistakes = 0  # błędy drużyny lewej
        self.team2_mistakes = 0  # błędy drużyny prawej
        self.team1_score = 0
        self.team2_score = 0
        self.team1_name = "Drużyna Lewa"
        self.team2_name = "Drużyna Prawa"
        self.intro_image_path = None  # Ścieżka do pliku z logo

    def add_question(self, question_text, answers):
        """
        Dodaje nowe pytanie do listy pytań.

        Args:
            question_text (str): Tekst pytania.
            answers (list): Lista krotek (odpowiedź, punkty).
        """
        question = {'question': question_text, 'answers': []}
        for ans, pts in answers:
            question['answers'].append({
                'answer': ans,
                'points': pts,
                'revealed': False
            })
        self.questions.append(question)

    def load_questions(self, file_path):
        """
        Ładuje pytania z pliku JSON.

        Args:
            file_path (str): Ścieżka do pliku z pytaniami.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
            logging.info("Pytania wczytane.")
        except FileNotFoundError:
            messagebox.showerror("Błąd", "Plik z pytaniami nie istnieje.")
            logging.error("Nie znaleziono pliku z pytaniami: %s", file_path)
        except Exception as e:
            messagebox.showerror("Błąd", "Wystąpił błąd podczas wczytywania pytań.")
            logging.error("Błąd przy ładowaniu pytań: %s", e)

    def save_questions(self, file_path):
        """
        Zapisuje pytania do pliku JSON.

        Args:
            file_path (str): Ścieżka do pliku, gdzie zapisać pytania.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=4)
            logging.info("Pytania zapisane.")
        except Exception as e:
            messagebox.showerror("Błąd", "Wystąpił błąd podczas zapisywania pytań.")
            logging.error("Błąd przy zapisywaniu pytań: %s", e)

    def set_current_question(self, index):
        """
        Ustawia aktualne pytanie na podstawie indeksu.

        Args:
            index (int): Indeks pytania.
        """
        self.current_question_index = index
        self.current_question = self.questions[index]
        self.team1_mistakes = 0
        self.team2_mistakes = 0
        for ans in self.current_question['answers']:
            ans['revealed'] = False

    def reveal_answer(self, answer_index, team):
        """
        Odkrywa odpowiedź i przyznaje punkty odpowiedniej drużynie.

        Args:
            answer_index (int): Indeks odpowiedzi.
            team (str): 'left' lub 'right' określające drużynę.
        """
        if self.current_question is not None and 0 <= answer_index < len(self.current_question['answers']):
            if not self.current_question['answers'][answer_index]['revealed']:
                self.current_question['answers'][answer_index]['revealed'] = True
                pts = self.current_question['answers'][answer_index]['points']
                if team == 'left':
                    self.team1_score += pts
                elif team == 'right':
                    self.team2_score += pts

    def add_mistake(self, team):
        """
        Rejestruje błąd dla danej drużyny.

        Args:
            team (str): 'left' lub 'right'.

        Returns:
            bool: True, jeśli błąd został dodany, False, jeśli osiągnięto limit.
        """
        if self.current_question is None:
            return False
        if team == 'left':
            if self.team1_mistakes < 3:
                self.team1_mistakes += 1
            else:
                return False
        elif team == 'right':
            if self.team2_mistakes < 3:
                self.team2_mistakes += 1
            else:
                return False
        return True

    def reset_game(self):
        """Resetuje punkty, błędy oraz aktualne pytanie."""
        self.team1_score = 0
        self.team2_score = 0
        self.team1_mistakes = 0
        self.team2_mistakes = 0
        self.current_question = None
        self.current_question_index = None
