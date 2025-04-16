from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QDrag, QPainter
from PyQt5.QtCore import Qt, QMimeData
from tower import TowerDragLabel

class ShopItem(QLabel):
    def __init__(self, pixmap, tower_type, cost, scene):
        super().__init__()
        self.original_pixmap = QPixmap(pixmap)  # zachowaj oryginał!

        self.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio))
        self.setFixedSize(52, 52)
        self.setStyleSheet("border: 1px solid gray; margin: 2px;")
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)
        self.tower_type = tower_type
        self.cost = cost
        self.scene = scene

    def mousePressEvent(self, event):
        if self.scene.gold < self.cost:
            QMessageBox.information(self, "Brak złota", "Nie masz wystarczająco złota!")
            return

        self.scene.pause_game()

        msg = QMessageBox()
        msg.setWindowTitle("Zakup wieży")
        msg.setText(f"Czy chcesz kupić wieżę typu {self.tower_type} za {self.cost} złota?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec_()

        if result == QMessageBox.Yes:
            self.scene.gold -= self.cost
            self.scene.gold_display_widget.setText(f"Gold: {self.scene.gold}")


            drag_label = TowerDragLabel(QPixmap(self.original_pixmap), tower_type=self.tower_type)
            self.scene.replace_widget(drag_label)

        self.scene.resume_game()
