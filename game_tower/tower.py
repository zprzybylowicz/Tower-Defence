import math
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsEllipseItem, QLabel
from PyQt5.QtGui import QBrush, QColor, QPixmap, QPainter, QDrag
from PyQt5.QtCore import QTimer, Qt, QPointF, QMimeData
from enemy_base import Enemy

TILE_SIZE = 64

class Tower(QGraphicsPixmapItem):
    def __init__(self, grid_x, grid_y, tower_type="fire"):
        super().__init__()
        self.was_firing = False

        self.tower_type = tower_type

        if tower_type == "fire":
            pixmap = QPixmap(":/enemy/6.png")
            self.fire_range = 300
            self.fire_rate = 1000
            self.num_bullets = 1
        elif tower_type == "sniper":
            pixmap = QPixmap(":/enemy/12.png")
            self.fire_range = 450
            self.fire_rate = 500
            self.num_bullets = 8
        else:
            pixmap = QPixmap(":/enemy/6.png")
            self.fire_range = 300
            self.fire_rate = 1000
            self.num_bullets = 5

        pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)

        offset = (TILE_SIZE - pixmap.width()) / 2
        self.setPos(grid_x * TILE_SIZE + offset, grid_y * TILE_SIZE + offset)

        self.timer = QTimer()
        self.timer.timeout.connect(self.shoot)

        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.target_direction = QPointF(0, -1)

    def pause_game(self):
        self.was_firing = self.timer.isActive()
        if self.timer.isActive():
            self.timer.stop()

    def resume_game(self):
        if self.was_firing and not self.timer.isActive():
            self.timer.start(self.fire_rate)

    def mousePressEvent(self, event):
        if not self.timer.isActive():
            self.was_firing = True
            self.timer.start(self.fire_rate)
        super().mousePressEvent(event)

    def shoot(self):
        scene = self.scene()
        if not scene:
            return

        tower_center = self.sceneBoundingRect().center()


        if scene.level > 1 and hasattr(scene, "current_path") and scene.current_path:


                tower_center = self.sceneBoundingRect().center()
                closest = min(scene.current_path, key=lambda p: math.hypot(
                    tower_center.x() - (p[0] * TILE_SIZE + TILE_SIZE / 2),
                    tower_center.y() - (p[1] * TILE_SIZE + TILE_SIZE / 2)
                ))
                target_point = QPointF(closest[0] * TILE_SIZE + TILE_SIZE / 2,
                                       closest[1] * TILE_SIZE + TILE_SIZE / 2)


                for _ in range(self.num_bullets):
                    bullet = Bullet(tower_center, target_point)
                    scene.addItem(bullet)



        else:

            enemy_found = False
            for item in scene.items():
                if getattr(item, "isEnemy", False):
                    dx = item.x() - tower_center.x()
                    dy = item.y() - tower_center.y()
                    dist = (dx ** 2 + dy ** 2) ** 0.5
                    if dist <= self.fire_range:
                        enemy_found = True
                        for _ in range(self.num_bullets):
                            bullet = Bullet(tower_center, item)
                            scene.addItem(bullet)
            if not enemy_found:
                # brak wroga – strzał w domyślny punkt
                default_target = QPointF(tower_center.x(), 7 * TILE_SIZE + TILE_SIZE / 2)
                for _ in range(self.num_bullets):
                    bullet = Bullet(tower_center, default_target)
                    scene.addItem(bullet)


class Bullet(QGraphicsEllipseItem):
    def __init__(self, start, target, speed=5):
        super().__init__(0, 0, 10,10)
        self.setBrush(QBrush(QColor("red")))
        self.setPos(start)
        self.speed = speed
        self.target = target

        if hasattr(target, "sceneBoundingRect"):
            target_center = target.sceneBoundingRect().center()
        else:
            target_center = target

        self.total_distance = math.hypot(target_center.x() - start.x(), target_center.y() - start.y())
        self.start_pos = start
        self.vx, self.vy = self.calculate_initial_velocity(start, target)

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_bullet)
        self.timer.start(30)

    def pause_game(self):
        try:
            if hasattr(self, "timer") and self.timer.isActive():
                self.timer.stop()
        except Exception as e:
            print("[Bullet.pause_game] ERROR:", e)

    def resume_game(self):
        try:
            if hasattr(self, "timer") and not self.timer.isActive():
                self.timer.start(30)
        except Exception as e:
            print("[Bullet.resume_game] ERROR:", e)

    def calculate_initial_velocity(self, start, target):
        if hasattr(target, "sceneBoundingRect"):
            center = target.sceneBoundingRect().center()
        else:
            center = target
        dx = center.x() - start.x()
        dy = center.y() - start.y()
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        return (dx / dist) * self.speed, (dy / dist) * self.speed

    def move_bullet(self):
        scene = self.scene()
        if not scene:
            self.timer.stop()
            return

        self.moveBy(self.vx, self.vy)
        bullet_center = self.sceneBoundingRect().center()

        try:
            # Wyciągamy żywych przeciwników obecnych na scenie
            enemies = [
                item for item in scene.items()
                if isinstance(item, Enemy) and getattr(item, "isEnemy", False) and item.scene()
            ]

            for enemy in enemies:
                try:
                    enemy_center = enemy.sceneBoundingRect().center()
                    dist = math.hypot(enemy_center.x() - bullet_center.x(), enemy_center.y() - bullet_center.y())

                    if self.collidesWithItem(enemy):
                       # print("[BULLET] Kolizja z wrogiem, wywołuję hit()")
                        #nemy.hit()
                        enemy.hit()
                        self.timer.stop()
                        if self.scene():
                            self.scene().removeItem(self)
                        return
                except RuntimeError:
                    continue  # w międzyczasie wróg zniknął

        except Exception as e:
            print("")

        # Sprawdź, czy pocisk doleciał za daleko
        traveled = math.hypot(
            bullet_center.x() - self.start_pos.x(),
            bullet_center.y() - self.start_pos.y()
        )
        if traveled >= self.total_distance or traveled > 600:
            self.timer.stop()
            if scene:
                try:
                    scene.removeItem(self)
                except Exception:
                    pass
            return

        # Usuń pocisk, jeśli wyszedł poza scenę
        if not scene.sceneRect().contains(self.sceneBoundingRect()):
            self.timer.stop()
            try:
                scene.removeItem(self)
            except Exception:
                pass


class TowerDragLabel(QLabel):
    def __init__(self, pixmap, tower_type="fire", parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio))
        self.tower_type = tower_type
        self.setFixedSize(64, 64)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: lightblue; border: 1px solid black;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            mime = QMimeData()
            mime.setText(self.tower_type)

            drag = QDrag(self)
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            self.render(painter)
            painter.end()

            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.CopyAction)
