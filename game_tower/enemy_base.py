import math
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QColor

TILE_SIZE = 64

class Enemy(QGraphicsPixmapItem):
    def __init__(self, path, speed=40, start_delay=1000, skin_path=":/enemy/enemy_1.png", level=1):

        super().__init__()
        self.level = level
        self.path = path
        self.path_index = 0
        self.speed = speed  # piksele na sekundę
        self.hp = 2
        self.isEnemy = True
        self.skin_path = skin_path
        self.type_name = "Enemy"
        self.alive = True


        pix_w = self.pixmap().width()
        pix_h = self.pixmap().height()
        self.pos_x, self.pos_y = self.grid_to_pos(self.path[0], pix_w, pix_h)
        self.setPos(self.pos_x, self.pos_y)

        self.set_skin_by_level()


        self.timer = QTimer()
        self.timer.timeout.connect(self.move_step)
        self.move_interval = 30  # ms
        # Start timera z opóźnieniem
        QTimer.singleShot(start_delay, self.start_movement)

        self.type_text = QGraphicsTextItem(self.type_name)
        self.type_text.setParentItem(self)  # ustawienie explicite rodzica

        self.type_text.setDefaultTextColor(QColor("yellow"))
        self.type_text.setPos(0, -10)
        pixmap = self.pixmap()
        self.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)

        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(Qt.LeftButton)

    def start_movement(self):
        self.timer.start(self.move_interval)

    def pause_game(self):
        if self.timer.isActive():
            self.timer.stop()

    def resume_game(self):
        if not self.alive:
            return
        if not self.timer.isActive():
            self.timer.start(self.move_interval)

    def grid_to_pos(self, cell, pix_w, pix_h):
        """Zamienia współrzędne kafelka (x, y) na piksele (uwzględnia TILE_SIZE)."""
        grid_x, grid_y = cell
        return (grid_x * TILE_SIZE, grid_y * TILE_SIZE)

    def set_skin_by_level(self):

        if hasattr(self, "skin_path") and self.skin_path:
            self.setPixmap(QPixmap(self.skin_path))
        else:
            if self.level == 1:
                self.setPixmap(QPixmap(":/enemy/enemy_1.png"))
            elif self.level == 2:
                self.setPixmap(QPixmap(":/enemy/enemy_2.png"))
            elif self.level == 3:
                self.setPixmap(QPixmap(":/enemy/enemy_3.png"))
            elif self.level == 4:
                self.setPixmap(QPixmap(":/enemy/enemy_4.png"))

        pixmap = self.pixmap()
        self.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)

    def move_step(self):
        import math

        dt = self.move_interval / 1000.0

        distance_to_move = self.speed * dt


        collision_threshold = 30  # dostosuj tę wartość do swoich potrzeb
        current_scene = self.scene()
        if current_scene:
            for item in list(current_scene.items()):
                if item is self:
                    continue
                if getattr(item, "isEnemy", False):

                    if getattr(item, "path_index", 0) < self.path_index:
                        dist = math.hypot(self.x() - item.x(), self.y() - item.y())
                        if dist < collision_threshold:
                            # Jeśli wrog przed nami jest za blisko, zatrzymaj ruch w tym ticku
                            distance_to_move = 0
                            break


        if distance_to_move > 0 and self.path_index < len(self.path):

            target_node = self.path[self.path_index]
            target_px = self.grid_to_pos(target_node, self.pixmap().width(), self.pixmap().height())
            dx = target_px[0] - self.pos_x
            dy = target_px[1] - self.pos_y
            dist_to_node = math.hypot(dx, dy)

            if dist_to_node == 0:

                self.path_index += 1
            elif dist_to_node <= distance_to_move:

                self.pos_x, self.pos_y = target_px
                distance_to_move -= dist_to_node
                self.path_index += 1

                while distance_to_move > 0 and self.path_index < len(self.path):
                    target_node = self.path[self.path_index]
                    target_px = self.grid_to_pos(target_node, self.pixmap().width(), self.pixmap().height())
                    dx = target_px[0] - self.pos_x
                    dy = target_px[1] - self.pos_y
                    dist_to_node = math.hypot(dx, dy)
                    if dist_to_node <= distance_to_move:
                        self.pos_x, self.pos_y = target_px
                        distance_to_move -= dist_to_node
                        self.path_index += 1
                    else:
                        ratio = distance_to_move / dist_to_node
                        self.pos_x += dx * ratio
                        self.pos_y += dy * ratio
                        distance_to_move = 0
            else:
                # Poruszamy się o część dystansu w kierunku docelowego węzła
                ratio = distance_to_move / dist_to_node
                self.pos_x += dx * ratio
                self.pos_y += dy * ratio


        self.setPos(self.pos_x, self.pos_y)


        if self.path_index < len(self.path):
            target_px = self.grid_to_pos(self.path[self.path_index], self.pixmap().width(), self.pixmap().height())
            dx = target_px[0] - self.pos_x
            dy = target_px[1] - self.pos_y
            angle = math.degrees(math.atan2(dy, dx))
            self.setRotation(angle)


        if self.path_index >= len(self.path):
            self.timer.stop()
            if current_scene:
                if hasattr(current_scene, "game_over"):
                    current_scene.game_over()
                else:
                    current_scene.removeItem(self)

    def mousePressEvent(self, event):
        #self.upgrade()
        super().mousePressEvent(event)

    def hit(self):
       # print(f"[HIT] Wróg trafiony: {self}, HP przed: {self.hp}")
        if not self.alive:
         #   print("[HIT] Wróg już martwy")
            return

        self.hp -= 1
       # print(f"[HIT] HP po: {self.hp}")

        if self.hp <= 0:
         #   print(f"[HIT] Wróg umiera: {self}")
            self.alive = False

            scene = self.scene()
            if scene and hasattr(scene, "enemies_killed"):
                scene.enemies_killed += 1

            # Wywołaj reward()
            if hasattr(self, "reward") and callable(self.reward):
                self.reward()
               # print(f"[HIT] Wywołano reward(), Total Gold: {scene.gold}")
            else:

                if scene and hasattr(scene, "add_gold"):
                    scene.add_gold(100)
                #    print(f"[HIT] Dodano złoto, Total Gold: {scene.gold}")

            try:
                scene.removeItem(self)
              #  print("[HIT] Wróg usunięty ze sceny!")
            except Exception as e:
                print("[HIT] Błąd przy usuwaniu wroga:", e)
            scene.update()


            self.hide()
            self.setEnabled(False)
            QTimer.singleShot(0, self.deleteLater)
        else:
            print("[HIT] Wróg jeszcze żyje")


class EnemyRandom(Enemy):
    def __init__(self, path, skin_path=":/enemy/enemy_1.png"):
        super().__init__(path, speed=40, skin_path=skin_path)  # 40 px/s
        self.hp = 1
        self.type_name = "Random"
        self.type_text.setPlainText(self.type_name)
        self.alive = True


class EnemyStrateg(Enemy):
    def __init__(self, path, skin_path=":/enemy/enemy_2.png"):
        super().__init__(path, speed=60, skin_path=skin_path)  # 60 px/s
        self.hp = 3
        self.type_name = "Strateg"
        self.type_text.setPlainText(self.type_name)
        self.alive = True


class EnemyAggressor(Enemy):
    def __init__(self, path, skin_path=":/enemy/enemy_3.png"):
        super().__init__(path, speed=100, skin_path=skin_path)  # 100 px/s
        self.hp = 5
        self.type_name = "Aggressor"
        self.type_text.setPlainText(self.type_name)
        self.alive = True
