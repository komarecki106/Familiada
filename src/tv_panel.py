import tkinter as tk
import os
from tkinter import messagebox
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None
from utils import resource_path

class TVPanel(tk.Toplevel):
    """
    Panel telewizyjny do wyświetlania informacji i animacji w grze Familiada.
    """
    def __init__(self, master, game, sound_manager):
        super().__init__(master)
        self.game = game
        self.sound_manager = sound_manager
        self.fullscreen = False
        self.title("TV Panel - Familiada")
        self.configure(bg="black")
        self.geometry("1200x700")
        self.bind("<Double-Button-1>", self.toggle_fullscreen)
        self.bind("<Configure>", self.on_resize)

        # Układ grid: trzy kolumny
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Lewy i prawy panel błędów
        self.left_error_canvas = tk.Canvas(self, bg="black", width=300, highlightthickness=0)
        self.left_error_canvas.grid(row=0, column=0, sticky="ns")
        self.right_error_canvas = tk.Canvas(self, bg="black", width=300, highlightthickness=0)
        self.right_error_canvas.grid(row=0, column=2, sticky="ns")

        # Etykiety punktacji
        self.left_score_label = tk.Label(self.left_error_canvas, text="", font=("familiada", 20, "bold"), fg="yellow", bg="black")
        self.right_score_label = tk.Label(self.right_error_canvas, text="", font=("familiada", 20, "bold"), fg="yellow", bg="black")
        self.left_score_label.place_forget()
        self.right_score_label.place_forget()

        self.initialize_error_panels()

        # Duże X dla narady
        self.left_big_x = tk.Label(self.left_error_canvas, text="X", font=("familiada", 220, "bold"), fg="red", bg="black")
        self.right_big_x = tk.Label(self.right_error_canvas, text="X", font=("familiada", 220, "bold"), fg="red", bg="black")
        self.left_big_x.place_forget()
        self.right_big_x.place_forget()

        # Panel centralny
        self.center_frame = tk.Frame(self, bg="black")
        self.center_frame.grid(row=0, column=1, sticky="nsew")
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.answer_labels = []

    def initialize_error_panels(self):
        """Inicjalizuje panele błędów z pustymi 'X'."""
        self.left_error_items = []
        self.right_error_items = []
        positions = [200, 350, 500]
        for pos in positions:
            item = self.left_error_canvas.create_text(150, pos, text="X", font=("familiada", 90, "bold"), fill="black")
            self.left_error_items.append(item)
            item2 = self.right_error_canvas.create_text(150, pos, text="X", font=("familiada", 90, "bold"), fill="black")
            self.right_error_items.append(item2)

    def update_error_panels(self):
        """Aktualizuje widok paneli błędów na podstawie liczby błędów drużyn."""
        for i, item in enumerate(self.left_error_items):
            if i < self.game.team1_mistakes:
                self.left_error_canvas.itemconfig(item, fill="yellow")
            else:
                self.left_error_canvas.itemconfig(item, fill="black")
        for i, item in enumerate(self.right_error_items):
            if i < self.game.team2_mistakes:
                self.right_error_canvas.itemconfig(item, fill="yellow")
            else:
                self.right_error_canvas.itemconfig(item, fill="black")
        self.update_score_labels()

    def update_score_labels(self):
        """Aktualizuje etykiety punktacji."""
        self.left_score_label.config(text=f"{self.game.team1_name}\n{self.game.team1_score}")
        self.right_score_label.config(text=f"{self.game.team2_name}\n{self.game.team2_score}")

    def show_team_names(self):
        """Wyświetla nazwy drużyn na panelu punktacji."""
        self.left_score_label.place(relx=0.5, y=10, anchor="n")
        self.right_score_label.place(relx=0.5, y=10, anchor="n")
        self.update_score_labels()

    def on_resize(self, event):
        """Obsługuje zmianę rozmiaru okna."""
        self.update_error_panels()

    def toggle_fullscreen(self, event=None):
        """Przełącza tryb pełnoekranowy."""
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)
        self.update_idletasks()
        self._start_intro_text()  # Ponowne wywołanie metody, aby dostosować napis

    def start_intro(self):
        """Rozpoczyna intro, wyświetlając logo lub napis 'FAMILIADA'."""
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        if self.game.intro_image_path and os.path.exists(self.game.intro_image_path) and Image and ImageTk:
            try:
                self.center_frame.update_idletasks()
                w = self.center_frame.winfo_width() or 800
                h = self.center_frame.winfo_height() or 600
                pil_img = Image.open(self.game.intro_image_path)
                pil_img = pil_img.resize((w, h), Image.ANTIALIAS)
                self.intro_image = ImageTk.PhotoImage(pil_img)
                lbl = tk.Label(self.center_frame, image=self.intro_image, bg="black")
                lbl.place(relx=0.65, rely=0.5, anchor="center")
            except Exception as e:
                print("Błąd przy ładowaniu obrazu intro:", e)
                self._start_intro_text()
        else:
            self._start_intro_text()
        if self.sound_manager and self.sound_manager.sounds.get("start"):
            self.sound_manager.play("start")
        self.show_team_names()

    def _start_intro_text(self):
        """Wyświetla napis 'FAMILIADA' wraz z animowanymi paskami."""
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        if hasattr(self, "intro_canvas") and self.intro_canvas.winfo_exists():
            self.intro_canvas.destroy()
        self.intro_canvas = tk.Canvas(self.center_frame, bg="black", highlightthickness=0)
        self.intro_canvas.grid(row=0, column=0, sticky="nsew")
        self.center_frame.update_idletasks()

        w = self.intro_canvas.winfo_width() or 1200
        h = self.intro_canvas.winfo_height() or 700

        font_size = max(40, min(100, int(w / 10), int(h / 8)))

        if hasattr(self, "intro_text_item"):
            self.intro_canvas.delete(self.intro_text_item)

        self.intro_text_item = self.intro_canvas.create_text(
            w / 2, h / 2, text="FAMILIADA",
            font=("familiada", font_size, "bold"),
            fill="yellow", width=w * 0.9, anchor="center"
        )
        self.intro_canvas.update()

        bbox = self.intro_canvas.bbox(self.intro_text_item)
        if not bbox:
            bbox = (w/2 - 200, h/2 - 40, w/2 + 200, h/2 + 40)
        x1, y1, x2, y2 = bbox
        num_stripes = 20
        stripe_height = (y2 - y1) / num_stripes
        self.stripe_ids = []
        for i in range(num_stripes):
            rect = self.intro_canvas.create_rectangle(
                x1, y1 + i * stripe_height, x2, y1 + (i+1) * stripe_height,
                fill="black", outline="black"
            )
            self.stripe_ids.append(rect)
        self._animate_stripes(0, num_stripes, x1, x2, stripe_height)

    def _animate_stripes(self, i, num_stripes, x1, x2, stripe_height, step=80):
        if i < num_stripes:
            self._animate_stripe(self.stripe_ids[i], x1, x2, step,
                                 lambda: self._animate_stripes(i+1, num_stripes, x1, x2, stripe_height, step))

    def _animate_stripe(self, stripe_id, current_x, target_x, step, callback=None):
        if not self.intro_canvas.winfo_exists():
            return
        try:
            coords = self.intro_canvas.coords(stripe_id)
        except tk.TclError:
            return
        if current_x < target_x:
            new_x = min(current_x + step, target_x)
            _, y1, x2, y2 = coords
            self.intro_canvas.coords(stripe_id, new_x, y1, x2, y2)
            self.after(30, self._animate_stripe, stripe_id, new_x, target_x, step, callback)
        else:
            self.intro_canvas.delete(stripe_id)
            if callback:
                callback()

    def animate_answers(self):
        """Animacja wyświetlania pytań i odpowiedzi na panelu."""
        if self.game.current_question is None:
            return
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        self.answers_frame = tk.Frame(self.center_frame, bg="black")
        self.answers_frame.pack(expand=True)
        self.answers_container = tk.Frame(self.answers_frame, bg="black")
        self.answers_container.pack(expand=True)
        top_spacer = tk.Frame(self.answers_container, bg="black")
        top_spacer.pack(expand=True)
        self.answer_labels = []

        w = self.center_frame.winfo_width() or 1200
        base_font_size = 36
        responsive_font_size = min(base_font_size, max(20, int(w / 40)))

        answers = self.game.current_question['answers']
        placeholders = [f"{i+1}. --------------------" for i in range(len(answers))]
        for idx in range(len(answers)):
            row_frame = tk.Frame(self.answers_container, bg="black")
            row_frame.pack(anchor="center", pady=5, fill="x")
            lbl = tk.Label(row_frame, text="", font=("familiada", responsive_font_size, "bold"),
                           bg="black", fg="yellow", anchor="w", justify="left")
            lbl.pack(side="left", padx=(20, 0), fill="x", expand=True)
            self.answer_labels.append(lbl)
        bottom_spacer = tk.Frame(self.answers_container, bg="black")
        bottom_spacer.pack(expand=True)
        self._animate_placeholders_seq(0, placeholders, delay=20)
        self.update_error_panels()

    def _animate_placeholders_seq(self, idx, placeholders, delay=20):
        if idx < len(placeholders):
            self._animate_label_text_seq(self.answer_labels[idx], 0, placeholders[idx], delay,
                                          lambda: self._animate_placeholders_seq(idx+1, placeholders, delay))

    def _animate_label_text_seq(self, label, index, full_text, delay, callback=None):
        if index <= len(full_text):
            label.config(text=full_text[:index])
            self.after(delay, self._animate_label_text_seq, label, index+1, full_text, delay, callback)
        else:
            if callback:
                callback()

    def animate_reveal_answer(self, idx):
        """Animacja odkrywania odpowiedzi dla danego indeksu."""
        if self.game.current_question is None or idx >= len(self.game.current_question['answers']):
            return
        ans_data = self.game.current_question['answers'][idx]
        prefix = f"{idx+1}. "
        final_text = f"{ans_data['answer']} - {ans_data['points']} pkt"
        label = self.answer_labels[idx]
        label.config(text=prefix)
        self._animate_reveal_portion(label, prefix, 0, final_text, delay=10)
        self.update_error_panels()

    def _animate_reveal_portion(self, label, prefix, index, final_text, delay=10):
        if index <= len(final_text):
            animated = final_text[:index]
            label.config(text=prefix + animated)
            self.after(delay, self._animate_reveal_portion, label, prefix, index+1, final_text, delay)
        else:
            label.config(text=prefix + final_text)

    def show_big_x(self, team):
        """
        Wyświetla duże czerwone "X" dla danej drużyny z opóźnieniem oraz odtwarza dźwięk błędu.
        """
        if team == 'left':
            self.left_big_x.place(relx=0.5, rely=0.5, anchor="center")
            self.after(2000, lambda: (self.left_big_x.place_forget(),
                                      self.sound_manager.play("error") if self.sound_manager else None))
        elif team == 'right':
            self.right_big_x.place(relx=0.5, rely=0.5, anchor="center")
            self.after(2000, lambda: (self.right_big_x.place_forget(),
                                      self.sound_manager.play("error") if self.sound_manager else None))

    def reset_screen(self):
        """Resetuje ekran centralny i wyświetla nazwy drużyn."""
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        self.show_team_names()
