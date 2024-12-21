from vpython import canvas, vector, box, color, rate


class SnakeGame3D:
    canvas_instances = []  # Статический атрибут для хранения всех созданных канвасов

    def __init__(self, game_state, fps=10):
        """
        Инициализация визуализации игры с добавлением канвасов.
        :param game_state: Начальное состояние игры.
        :param fps: Количество обновлений в секунду для ограничения частоты.
        """
        self.game_state = game_state
        self.fps = fps  # Число кадров в секунду
        self.paths = []

        # Проверяем, созданы ли уже канвасы
        if not SnakeGame3D.canvas_instances:
            for i in range(3):
                SnakeGame3D.canvas_instances.append(canvas(
                    title=f"Snake-{i + 1}",
                    width=500,
                    height=500,
                    center=vector(90, 30, 90),  # Центр карты
                    background=color.white  # Исходный фон
                ))

        # Уникальный список всех объектов для проверки пересечений
        self.objects = [{} for _ in range(3)]  # Отслеживаем объекты для каждого канваса

        # Запускаем визуализацию сразу для всех канвасов
        self.visualize_all()

    def clear_canvas(self, canvas_id):
        """Удалить объекты из канваса, которые больше не обновляются."""
        for obj in list(self.objects[canvas_id].values()):
            obj.visible = False  # Скройте объект, чтобы освободить память
        self.objects[canvas_id] = {}

    def draw_object(self, canvas_instance, position, size, color_value, canvas_id, key):
        """
        Добавляет или обновляет объект на канвасе.
        :param canvas_instance: Канвас для отрисовки объекта.
        :param position: Позиция объекта в пространстве.
        :param size: Размер объекта.
        :param color_value: Цвет объекта.
        :param canvas_id: ID канваса.
        :param key: Уникальный ключ объекта (например, его позиция).
        """
        pos_tuple = tuple(position)
        if key in self.objects[canvas_id]:  # Если объект существует, обновляем его
            obj = self.objects[canvas_id][key]
            obj.pos = vector(*pos_tuple)
        else:  # Иначе создаем новый объект
            self.objects[canvas_id][key] = box(pos=vector(*pos_tuple), size=size, color=color_value,
                                               canvas=canvas_instance)

    def draw_fences(self, canvas_instance, canvas_id):
        for fence in self.game_state["fences"]:
            self.draw_object(canvas_instance, position=fence, size=vector(1, 1, 1), color_value=color.green,
                             canvas_id=canvas_id, key=tuple(fence))

    def draw_food(self, canvas_instance, canvas_id):
        for food in self.game_state["food"]:
            food_color = self.parse_color_by_points(food["points"])
            self.draw_object(canvas_instance, position=food["c"], size=vector(1, 1, 1), color_value=food_color,
                             canvas_id=canvas_id, key=tuple(food["c"]))
        for special_type, special_list in self.game_state["specialFood"].items():
            special_color = color.yellow if special_type == "golden" else color.magenta
            for position in special_list:
                self.draw_object(canvas_instance, position=position, size=vector(1, 1, 1), color_value=special_color,
                                 canvas_id=canvas_id, key=tuple(position))

    def draw_snake(self, canvas_instance, canvas_id, snake):
        geometry = snake["geometry"]
        if geometry:
            head_position = geometry[0]
            canvas_instance.center = vector(*head_position)  # Центрируем камеру на голове змеи
        for i, segment in enumerate(geometry):
            seg_color = color.blue if i > 0 else color.cyan
            self.draw_object(canvas_instance, position=segment, size=vector(1, 1, 1), color_value=seg_color,
                             canvas_id=canvas_id, key=tuple(segment))

    def draw_enemies(self, canvas_instance, canvas_id):
        for enemy in self.game_state["enemies"]:
            geometry = enemy["geometry"]
            for i, segment in enumerate(geometry):
                seg_color = color.cyan if i == 0 else color.blue
                self.draw_object(canvas_instance, position=segment, size=vector(1, 1, 1),
                                 color_value=seg_color, canvas_id=canvas_id, key=tuple(segment))

    def draw_paths(self, canvas_instance, canvas_id):
        for path in self.paths:
            crop_path = path[1:-1]
            for segment in crop_path:
                seg_color = color.black
                self.draw_object(canvas_instance, position=segment, size=vector(1, 1, 1),
                                 color_value=seg_color, canvas_id=canvas_id, key=tuple(segment))

    def parse_color_by_points(self, points):
        if points <= 0:
            return color.white
        elif points < 50:
            return vector(1, 1 - points / 50, 0)  # Переход от желтого к красному
        else:
            return vector(1, 0, 0)  # Красный

    def visualize(self, canvas_instance, canvas_id, snake):
        self.clear_canvas(canvas_id)  # Удаляем старые объекты, если они больше не нужны
        self.draw_fences(canvas_instance, canvas_id)
        self.draw_food(canvas_instance, canvas_id)
        self.draw_snake(canvas_instance, canvas_id, snake)
        self.draw_enemies(canvas_instance, canvas_id)
        self.draw_paths(canvas_instance, canvas_id)

    def visualize_all(self):
        for i, snake in enumerate(self.game_state["snakes"]):
            self.visualize(SnakeGame3D.canvas_instances[i], i, snake)