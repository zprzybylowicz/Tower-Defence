import json
import os
from datetime import datetime


class GameHistory:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.history = []
        self.load_history()

    def load_history(self):
        """Odczytuje historię z pliku JSON (jeśli plik istnieje)"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        """Zapisuje bieżącą historię do pliku JSON"""
        with open(self.filename, "w") as f:
            json.dump(self.history, f, indent=4)

    def add_record(self, mode, gold, enemies_killed, level, time_played, details=""):
        record = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "gold": gold,
            "enemies_killed": enemies_killed,
            "level": level,
            "time_played": time_played,
            "details": details
        }
        self.history.append(record)
        self.save_history()

    def get_history(self):
        """Zwraca listę zapisanych rekordów historii gry"""
        return self.history


# Przykładowe użycie:
if __name__ == "__main__":
    gh = GameHistory()
    # Dodajemy przykładowy rekord
    gh.add_record("single", 1500, "Przykładowa gra zakończona sukcesem.")
    print("Historia gry:")
    for record in gh.get_history():
        print(record)
