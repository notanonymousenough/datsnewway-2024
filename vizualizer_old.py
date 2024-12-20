import requests
from vpython import canvas, vector, box, color, label, rate

# Конфигурация API
BASE_URL = "https://games-test.datsteam.dev"
HEADERS = {"X-Auth-Token": "token"}

# Установить размеры карты
MAP_SIZE = [180, 180, 30]


# ---------- API Запросы ----------
def get_initial_game_state():
    """Отправляет начальный запрос на /player/move с пустым списком змей и возвращает состояние игры."""
    payload = {"snakes": []}
    try:
        response = requests.post(f"{BASE_URL}/play/snake3d/player/move", headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка начального запроса: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Ошибка соединения с API: {e}")
        return None


def move_snakes(snakes):
    """Отправляет список змей с их направлениями для обновления их положения."""
    payload = {"snakes": snakes}
    try:
        response = requests.post(f"{BASE_URL}/play/snake3d/player/move", headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка запроса на движение змей: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Ошибка соединения с API: {e}")
        return None


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


# ---------- Основной игровой цикл ----------
def game_loop():
    # Получаем начальное состояние игры
    game_state = get_initial_game_state()
    if not game_state:
        print("Не удалось получить начальное состояние игры.")
        return

    # Ограничение: до 3 змей
    snakes_data = game_state["snakes"][:3]
    fences = game_state["fences"]  # Преграды
    position_offsets = [[-300, 0, 0], [0, 0, 0], [300, 0, 0]]  # Сдвиги для трех змей
    snake_maps = [SnakeMap(snake_data, offset, fences) for snake_data, offset in zip(snakes_data, position_offsets)]

    # Еда
    food_items = []
    for snake_map in snake_maps:
        food_items.append(draw_food(game_state["food"], snake_map.scene))

    while True:
        rate(10)  # Перерисовка каждые 10 кадров

        # Составляем запрос на движения всех змей
        snakes_payload = []
        for i, snake_map in enumerate(snake_maps):
            direction = [int(snake_map.direction.x), int(snake_map.direction.y), int(snake_map.direction.z)]
            snakes_payload.append({"id": snake_map.id, "direction": direction})

        # Запрашиваем новое состояние игры
        game_response = move_snakes(snakes_payload)
        if game_response:
            for i, new_snake_data in enumerate(game_response["snakes"]):
                snake_maps[i].update(new_snake_data["geometry"], new_snake_data["direction"])

            # Обновляем еду
            for i, snake_map in enumerate(snake_maps):
                for item in food_items[i]:
                    item.visible = False  # Удаляем предыдущую еду
                food_items[i] = draw_food(game_response["food"], snake_map.scene)


# ---------- Запуск ----------
game_loop()