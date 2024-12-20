import requests
from vpython import canvas, vector, box, color, label, rate

# Установить размеры карты
MAP_SIZE = [180, 180, 180]


# ---------- Классы для визуализации ----------
class SnakeMap:
    def __init__(self, snake_data, position_offset, fences):
        self.id = snake_data["id"]
        # Центр камеры для каждого индивидуального представления
        self.map_center = vector(*snake_data["geometry"][0]) + vector(*position_offset)

        # Инициализация отдельной сцены
        self.scene = canvas(title=f"Snake {self.id}", width=600, height=600,
                            center=self.map_center, forward=vector(0, 0, -1), align="right")

        # Разбиение области координат на оси
        self.draw_grid()

        # Задаем границы карты (основной контейнер)
        self.grid = box(canvas=self.scene, pos=self.map_center,
                        size=vector(*MAP_SIZE), opacity=0.1, color=color.white)

        # Преграды (зелёного цвета)
        self.fences = [
            box(canvas=self.scene, pos=vector(*fence), size=vector(2, 2, 2), color=color.green)
            for fence in fences
        ]

        # Змейка
        self.body = self.create_snake_body(snake_data["geometry"])
        self.direction = vector(*snake_data["direction"])
        self.head_label = label(canvas=self.scene, pos=self.body[0].pos,
                                text=f"Head: {self.body[0].pos}", xoffset=10, yoffset=10, box=False, height=10)

    def create_snake_body(self, geometry):
        """Создает тело змеи (голубая голова, синее тело)."""
        body_parts = []
        for i, segment in enumerate(geometry):
            color_part = color.cyan if i == 0 else color.blue  # Голубая голова, синее тело
            body_parts.append(box(canvas=self.scene, pos=vector(*segment), size=vector(2, 2, 2), color=color_part))
        return body_parts

    def update(self, new_geometry, new_direction):
        """Обновляет положение змеи."""
        for i, segment in enumerate(new_geometry):
            self.body[i].pos = vector(*segment)

        self.direction = vector(*new_direction)

        # Обновляем метку для головы
        self.head_label.pos = self.body[0].pos
        self.head_label.text = f"Head: {self.body[0].pos}"

        # Центрируем камеру на голову змеи
        self.scene.center = self.body[0].pos

    def draw_grid(self):
        """Рисует линии сетки для измерений оси."""
        for x in range(0, MAP_SIZE[0] + 1, 10):
            for y in range(0, MAP_SIZE[1] + 1, 10):
                box(canvas=self.scene, pos=vector(x, y, 0), size=vector(0.2, 0.2, MAP_SIZE[2]), color=color.gray(0.5))

        for y in range(0, MAP_SIZE[1] + 1, 10):
            for z in range(0, MAP_SIZE[2] + 1, 10):
                box(canvas=self.scene, pos=vector(0, y, z), size=vector(0.2, 0.2, MAP_SIZE[2]), color=color.gray(0.5))

        for z in range(0, MAP_SIZE[2] + 1, 10):
            for x in range(0, MAP_SIZE[0] + 1, 10):
                box(canvas=self.scene, pos=vector(x, 0, z), size=vector(0.2, MAP_SIZE[1], 0.2), color=color.gray(0.5))

    def draw_food(food_data, canvas_scene):
        """Рисует еду на карте (от желтого до красного в зависимости от `points`)."""
        food_boxes = []
        for food in food_data:
            # Определяем цвет еды в зависимости от количества очков
            points = food["points"]
            food_color = vector(1, 1 - min(points, 10) / 10, 0)  # Градиент от желтого (1, 1, 0) к красному (1, 0, 0)
            food_boxes.append(box(pos=vector(*food["c"]), size=vector(2, 2, 2), color=food_color, canvas=canvas_scene))
        return food_boxes


