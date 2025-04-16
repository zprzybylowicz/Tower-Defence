import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QButtonGroup, QRadioButton,
    QLabel, QPushButton, QLineEdit, QHBoxLayout
)
from PyQt5.QtGui import QFont, QValidator
from PyQt5.QtCore import Qt


class IP4Validator(QValidator):
    def __init__(self, parent=None):
        super(IP4Validator, self).__init__(parent)

    def validate(self, address, pos):
        address_clean = address.replace('_', '').strip()
        if not address_clean:
            return QValidator.Intermediate, address, pos

        if ':' in address:
            ip_part = address.split(':')[0]
        else:
            ip_part = address

        ip_part = ip_part.replace('_', '').strip()
        octets = ip_part.split(".")
        size = len(octets)
        if size > 4:
            return QValidator.Invalid, address, pos
        emptyOctet = False
        for octet in octets:
            octet_clean = octet.replace('_', '').strip()
            if not octet_clean:
                emptyOctet = True
                continue
            try:
                value = int(octet_clean)
            except Exception:
                return QValidator.Intermediate, address, pos
            if value < 0 or value > 255:
                return QValidator.Invalid, address, pos
        if size < 4 or emptyOctet:
            return QValidator.Intermediate, address, pos
        return QValidator.Acceptable, address, pos


class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tower Defense – Konfiguracja")
        self.setFixedSize(400, 300)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Tytuł
        title_label = QLabel("Wybierz tryb gry:")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Radio buttony – dodajemy dodatkową opcję "Wznowienie gry"
        self.radio_group = QButtonGroup(self)
        self.radio_single = QRadioButton("1 gracz")
        self.radio_two = QRadioButton("2 graczy lokalnie")
        self.radio_net = QRadioButton("Gra sieciowa")
        self.radio_resume = QRadioButton("Wznowienie gry z Json")
        self.radio_group.addButton(self.radio_single)
        self.radio_group.addButton(self.radio_two)
        self.radio_group.addButton(self.radio_net)
        self.radio_group.addButton(self.radio_resume)
        main_layout.addWidget(self.radio_single)
        main_layout.addWidget(self.radio_two)
        main_layout.addWidget(self.radio_net)
        self.radio_resume_xml = QRadioButton("Wznowienie z XML")
        self.radio_group.addButton(self.radio_resume_xml)
        main_layout.addWidget(self.radio_resume_xml)
        self.radio_resume_mongo = QRadioButton("Wznowienie z Mongo")
        self.radio_group.addButton(self.radio_resume_mongo)
        main_layout.addWidget(self.radio_resume_mongo)

        main_layout.addWidget(self.radio_resume)
        # Ustaw domyślnie "1 gracz"
        self.radio_single.setChecked(True)

        # Sekcja adresu IP i portu – widoczna tylko przy trybie sieciowym
        ip_layout = QHBoxLayout()
        ip_label = QLabel("Adres IP i port:")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("np. 192.168.000.178:8080")
        self.ip_input.setToolTip("Wprowadź adres IP i port w formacie: 000.000.000.000:0000")
        self.ip_input.setEnabled(False)
        self.ip_input.setInputMask("172.20.10.5:8080;_")
        validator = IP4Validator(self)
        self.ip_input.setValidator(validator)
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input)
        main_layout.addLayout(ip_layout)

        # Przycisk Start
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_game)
        main_layout.addWidget(self.start_button)

        # Łączenie sygnałów radiobuttonów
        self.radio_single.toggled.connect(self.on_radio_changed)
        self.radio_two.toggled.connect(self.on_radio_changed)
        self.radio_net.toggled.connect(self.on_radio_changed)
        self.radio_resume.toggled.connect(self.on_radio_changed)

        self.setLayout(main_layout)

        self.selected_mode = None
        self.selected_ip = None

    def on_radio_changed(self):

        if self.radio_net.isChecked():
            self.ip_input.setEnabled(True)
            self.ip_input.setFocus()
        else:
            self.ip_input.setEnabled(False)

    def start_game(self):
        if self.radio_single.isChecked():
            self.selected_mode = "single"
        elif self.radio_two.isChecked():
            self.selected_mode = "local_coop"
        elif self.radio_net.isChecked():
            self.selected_mode = "network"
        elif self.radio_resume.isChecked():
            self.selected_mode = "resume_json"
        elif self.radio_resume_xml.isChecked():
            self.selected_mode = "resume_xml"
        elif self.radio_resume_mongo.isChecked():
            self.selected_mode = "resume_mongo"
        self.selected_ip = self.ip_input.text() if self.selected_mode == "network" else ""
        self.accept()


def main():
    app = QApplication(sys.argv)

    config_dialog = ConfigDialog()
    result = config_dialog.exec_()

    if result == QDialog.Accepted:
        selected_mode = config_dialog.selected_mode
        selected_ip = config_dialog.selected_ip

        print("[DEBUG] Wybrany tryb gry:", selected_mode)
        print("[DEBUG] Wybrany adres IP:", selected_ip)

        
        from game import MainWindow
        window = MainWindow(game_mode=selected_mode, ip_address=selected_ip)
        window.resize(1200, 800)
        window.show()
        sys.exit(app.exec_())
    else:
        print("[DEBUG] Użytkownik anulował konfigurację.")
        sys.exit(0)


if __name__ == "__main__":
    main()
