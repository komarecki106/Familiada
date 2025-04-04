import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from game import Game

class AdminPanel(tk.Frame):
    """
    Panel Administratora do zarządzania grą Familiada.

    Parametry:
        master (tk.Tk): Główne okno aplikacji.
        game (Game): Instancja logiki gry.
        tv_panel (TVPanel): Panel wyświetlający informacje na ekranie.
        sound_manager (SoundManager): Obiekt do obsługi dźwięków.
    """
    def __init__(self, master, game, tv_panel, sound_manager, theme=None):
        # Automatyczne wykrywanie motywu systemowego przy użyciu darkdetect, jeśli theme nie jest podany
        try:
            import darkdetect
            if theme is None:
                theme = "dark" if darkdetect.isDark() else "light"
        except ImportError:
            if theme is None:
                theme = "light"
        self.theme = theme
        if theme == "dark":
            self.team1_color = "#E57373"
            self.team2_color = "#64B5F6"
        else:
            self.team1_color = "red"
            self.team2_color = "blue"
        
        super().__init__(master)
        self.game = game
        self.tv_panel = tv_panel
        self.sound_manager = sound_manager
        master.title("Panel Administratora - Familiada")
        master.geometry("1200x700")

        # Pasek z nazwami drużyn i wynikami
        header_frame = tk.Frame(self)
        header_frame.pack(side="top", fill="x", pady=5)
        self.team1_label = tk.Label(header_frame, text=self.game.team1_name, font=("Arial", 20, "bold"), fg=self.team1_color)
        self.team1_label.pack(side="left", padx=20)
        self.team2_label = tk.Label(header_frame, text=self.game.team2_name, font=("Arial", 20, "bold"), fg=self.team2_color)
        self.team2_label.pack(side="right", padx=20)

        # Lewy panel – przyciski sterujące i lista pytań
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.start_button = tk.Button(self.left_frame, text="Start", font=("Arial", 16),
                                      command=self.start_game)
        self.start_button.pack(pady=5)
        self.stop_button = tk.Button(self.left_frame, text="STOP", font=("Arial", 16),
                                     command=self.stop_game)
        self.stop_button.pack(pady=5)
        self.change_names_button = tk.Button(self.left_frame, text="Zmień nazwy drużyn", font=("Arial", 16),
                                             command=self.change_team_names)
        self.change_names_button.pack(pady=5)

        tk.Label(self.left_frame, text="Lista pytań:", font=("Arial", 16)).pack(pady=(10, 0))
        self.question_listbox = tk.Listbox(self.left_frame, width=60, font=("Arial", 14))
        self.question_listbox.pack(pady=5)
        self.question_listbox.bind("<<ListboxSelect>>", self.on_question_select)
        self.update_question_listbox()

        self.add_question_button = tk.Button(self.left_frame, text="Dodaj pytanie", font=("Arial", 14),
                                             command=self.open_add_question_window)
        self.add_question_button.pack(pady=5)
        self.load_questions_button = tk.Button(self.left_frame, text="Wczytaj pytania", font=("Arial", 14),
                                               command=self.load_questions)
        self.load_questions_button.pack(pady=5)
        self.save_questions_button = tk.Button(self.left_frame, text="Zapisz pytania", font=("Arial", 14),
                                               command=self.save_questions)
        self.save_questions_button.pack(pady=5)

        # Prawy panel – szczegóły aktualnego pytania oraz przyciski odkrywania odpowiedzi
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.update_question_controls()

    def start_game(self):
        """Rozpoczyna grę, uruchamia intro na panelu TV."""
        self.tv_panel.start_intro()

    def stop_game(self):
        """Resetuje stan gry po potwierdzeniu od użytkownika."""
        if messagebox.askyesno("STOP", "Czy na pewno chcesz zresetować punkty i pytania?"):
            self.game.reset_game()
            self.tv_panel.reset_screen()
            self.update_question_listbox()
            self.update_question_controls()
            self.tv_panel.update_error_panels()

    def change_team_names(self):
        """Pozwala zmienić nazwy drużyn."""
        new_left = simpledialog.askstring("Zmiana nazwy", "Podaj nazwę dla drużyny LEWEJ:", initialvalue=self.game.team1_name)
        new_right = simpledialog.askstring("Zmiana nazwy", "Podaj nazwę dla drużyny PRAWEJ:", initialvalue=self.game.team2_name)
        if new_left:
            self.game.team1_name = new_left
        if new_right:
            self.game.team2_name = new_right
        self.tv_panel.update_score_labels()
        self.team1_label.config(text=f"{self.game.team1_name}: {self.game.team1_score}", fg=self.team1_color)
        self.team2_label.config(text=f"{self.game.team2_name}: {self.game.team2_score}", fg=self.team2_color)
        self.update_question_controls()

    def update_question_listbox(self):
        """Aktualizuje listę pytań wyświetlaną w panelu administratora."""
        self.question_listbox.delete(0, tk.END)
        for idx, q in enumerate(self.game.questions):
            self.question_listbox.insert(tk.END, f"{idx+1}. {q['question']}")

    def on_question_select(self, event):
        """Obsługuje wybór pytania z listy."""
        selection = self.question_listbox.curselection()
        if selection:
            index = selection[0]
            self.game.set_current_question(index)
            self.tv_panel.animate_answers()
            self.update_question_controls()
            # Odtworzenie dźwięku po wybraniu pytania
            if self.sound_manager:
                self.sound_manager.play("question_intro")

    def update_question_controls(self):
        """Aktualizuje panel kontroli pytań na podstawie aktualnie wybranego pytania."""
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        if self.game.current_question is None:
            tk.Label(self.right_frame, text="Wybierz pytanie z listy", font=("Arial", 20)).pack()
            return
        tk.Label(self.right_frame, text=self.game.current_question['question'],
                font=("Arial", 20)).pack(pady=10)

        answers_frame = tk.Frame(self.right_frame)
        answers_frame.pack(pady=10)
        for idx, ans in enumerate(self.game.current_question['answers']):
            revealed = ans['revealed']
            row_frame = tk.Frame(answers_frame)
            row_frame.grid(row=idx, column=0, pady=5, sticky="w")
            text = f"{idx+1}. {ans['answer']} - {ans['points']} pkt"
            tk.Label(row_frame, text=text, font=("Arial", 16), anchor="w").grid(row=0, column=0, padx=5)
            btn_left = tk.Button(row_frame, text="Odkryj", font=("Arial", 14),
                                 command=lambda i=idx: self.reveal_answer(i, 'left'))
            btn_left.grid(row=0, column=1, padx=5)
            btn_right = tk.Button(row_frame, text="Odkryj", font=("Arial", 14),
                                  command=lambda i=idx: self.reveal_answer(i, 'right'))
            btn_right.grid(row=0, column=2, padx=5)
            if revealed:
                btn_left.config(state="disabled")
                btn_right.config(state="disabled")

        # Przyciski do rejestrowania błędów (dodają żółte X)
        error_frame = tk.Frame(self.right_frame)
        error_frame.pack(pady=10)
        btn_error_left = tk.Button(error_frame, text="Błąd", font=("Arial", 14),
                                   command=lambda: self.add_error('left'))
        btn_error_left.grid(row=0, column=0, padx=10)
        btn_error_right = tk.Button(error_frame, text="Błąd", font=("Arial", 14),
                                    command=lambda: self.add_error('right'))
        btn_error_right.grid(row=0, column=1, padx=10)

        # Przyciski "Błąd narada" – pokazują duże czerwone X
        consult_frame = tk.Frame(self.right_frame)
        consult_frame.pack(pady=10)
        btn_consult_left = tk.Button(consult_frame, text="Błąd narada", font=("Arial", 14),
                                     command=lambda: self.tv_panel.show_big_x('left'))
        btn_consult_left.grid(row=0, column=0, padx=10)
        btn_consult_right = tk.Button(consult_frame, text="Błąd narada", font=("Arial", 14),
                                      command=lambda: self.tv_panel.show_big_x('right'))
        btn_consult_right.grid(row=0, column=1, padx=10)

    def reveal_answer(self, index, team):
        """Odkrywa odpowiedź i aktualizuje punkty."""
        self.game.reveal_answer(index, team)
        self.update_question_controls()
        self.tv_panel.animate_reveal_answer(index)
        if self.sound_manager and self.sound_manager.sounds.get("reveal"):
            self.sound_manager.play("reveal")

    def add_error(self, team):
        """Rejestruje błąd dla danej drużyny i aktualizuje panel błędów."""
        if self.game.current_question is None:
            messagebox.showinfo("Informacja", "Wybierz pytanie z listy!")
            return
        success = self.game.add_mistake(team)
        if success:
            if self.sound_manager and self.sound_manager.sounds.get("error"):
                self.sound_manager.play("error")
        else:
            messagebox.showinfo("Informacja", f"Osiągnięto maksymalną liczbę błędów dla drużyny {team.upper()}.")
        self.tv_panel.update_error_panels()

    def open_add_question_window(self):
        """Otwiera okno do dodawania nowego pytania."""
        AddQuestionWindow(self, self.game)

    def load_questions(self):
        """Wczytuje pytania z pliku JSON."""
        file_path = filedialog.askopenfilename(
            title="Wybierz plik z pytaniami",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.game.load_questions(file_path)
            self.update_question_listbox()

    def save_questions(self):
        """Zapisuje pytania do pliku JSON."""
        file_path = filedialog.asksaveasfilename(
            title="Zapisz pytania",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.game.save_questions(file_path)

class AddQuestionWindow(tk.Toplevel):
    """
    Okno do dodawania nowego pytania.
    """
    def __init__(self, parent, game):
        super().__init__(parent)
        self.parent = parent
        self.game = game
        self.title("Dodaj nowe pytanie")
        self.geometry("500x500")
        tk.Label(self, text="Pytanie:", font=("Arial", 16)).pack(pady=5)
        self.question_entry = tk.Entry(self, width=60, font=("Arial", 14))
        self.question_entry.pack(pady=5)

        self.answers_entries = []
        self.points_entries = []
        for i in range(5):
            frame = tk.Frame(self)
            frame.pack(pady=3)
            tk.Label(frame, text=f"Odpowiedź {i+1}:", font=("Arial", 14)).pack(side="left")
            ans_entry = tk.Entry(frame, width=30, font=("Arial", 14))
            ans_entry.pack(side="left", padx=5)
            tk.Label(frame, text="Pkt:", font=("Arial", 14)).pack(side="left")
            pts_entry = tk.Entry(frame, width=5, font=("Arial", 14))
            pts_entry.pack(side="left", padx=5)
            self.answers_entries.append(ans_entry)
            self.points_entries.append(pts_entry)

        self.add_btn = tk.Button(
            self, text="Dodaj pytanie", font=("Arial", 16),
            command=self.add_question
        )
        self.add_btn.pack(pady=10)

    def add_question(self):
        """Dodaje pytanie do gry po walidacji danych."""
        question_text = self.question_entry.get().strip()
        if not question_text:
            messagebox.showerror("Błąd", "Pytanie nie może być puste")
            return
        answers = []
        for ans_entry, pts_entry in zip(self.answers_entries, self.points_entries):
            ans_text = ans_entry.get().strip()
            pts_text = pts_entry.get().strip()
            if ans_text:
                try:
                    pts = int(pts_text)
                except ValueError:
                    pts = 0
                answers.append((ans_text, pts))
        if not answers:
            messagebox.showerror("Błąd", "Dodaj przynajmniej jedną odpowiedź")
            return
        self.game.add_question(question_text, answers)
        self.parent.update_question_listbox()
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    from game import Game
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

    from tv_panel import TVPanel
    tv_panel = TVPanel(root, game, None)
    try:
        from sound_manager import SoundManager
        sound_manager = SoundManager()
    except ImportError:
        sound_manager = None

    admin_panel = AdminPanel(root, game, tv_panel, sound_manager)
    admin_panel.pack(fill="both", expand=True)
    root.mainloop()
