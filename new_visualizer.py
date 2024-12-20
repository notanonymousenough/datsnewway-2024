from vpython import canvas, vector, box, color


class SnakeGame3D:
    def __init__(self, game_state):
        """
        Инициализация визуализации игры на трех независимых канвасах с привязкой к каждой змее.
        """
        self.game_state = game_state

        # Создаем три отдельных канваса, по одному для каждой змеи
        self.canvases = []
        for i in range(3):
            self.canvases.append(canvas(
                title=f"Snake-{i + 1}",
                width=500,
                height=500,
                center=vector(90, 30, 90),  # Центр карты
                background=color.black
            ))

        # Уникальный список всех объектов для проверки пересечений
        self.existing_positions = set()

        # Запускаем визуализацию сразу для всех канвасов
        self.visualize_all()

    def check_overlap(self, position):
        """Проверяет, пересекается ли объект с уже добавленным (только для статических объектов)."""
        return tuple(position) in self.existing_positions

    def add_position(self, position):
        """Добавляет позицию в список существующих объектов."""
        self.existing_positions.add(tuple(position))

    def draw_fences(self, canvas_instance):
        """Отображение зеленых препятствий на заданном канвасе."""
        for fence in self.game_state["fences"]:
            if not self.check_overlap(fence):  # Проверяем пересечение
                box(pos=vector(*fence), size=vector(1, 1, 1), color=color.green, canvas=canvas_instance)
                self.add_position(fence)

    def draw_food(self, canvas_instance):
        """Отображение еды на заданном канвасе."""
        for food in self.game_state["food"]:
            food_color = self.parse_color_by_points(food["points"])
            if not self.check_overlap(food["c"]):  # Проверяем пересечение
                box(pos=vector(*food["c"]), size=vector(1, 1, 1), color=food_color, canvas=canvas_instance)
                self.add_position(food["c"])

        for special_type, special_list in self.game_state["specialFood"].items():
            special_color = color.yellow if special_type == "golden" else color.magenta
            for position in special_list:
                if not self.check_overlap(position):  # Проверяем пересечение
                    box(pos=vector(*position), size=vector(1, 1, 1), color=special_color, canvas=canvas_instance)
                    self.add_position(position)

    def draw_snake(self, canvas_instance, snake):
        """Отображение змеи на заданном канвасе."""
        geometry = snake["geometry"]

        # Привязываем камеру к голове змеи, если сегменты есть
        if geometry:
            head_position = geometry[0]
            canvas_instance.center = vector(*head_position)  # Устанавливаем центр канваса на голову змеи

        # Отрисовываем сегменты змеи
        for i, segment in enumerate(geometry):
            seg_color = color.blue if i > 0 else color.cyan  # Голова голубая, тело синее
            box(pos=vector(*segment), size=vector(1, 1, 1), color=seg_color, canvas=canvas_instance)

    def draw_enemies(self, canvas_instance):
        """Отображение врагов с синим телом и голубой головой на заданном канвасе."""
        for enemy in self.game_state["enemies"]:
            geometry = enemy["geometry"]
            for i, segment in enumerate(geometry):
                # Голова — голубая, тело — синее
                seg_color = color.cyan if i == 0 else color.blue
                if not self.check_overlap(segment):  # Проверяем пересечение
                    box(
                        pos=vector(*segment),
                        size=vector(1, 1, 1),
                        color=seg_color,
                        canvas=canvas_instance
                    )
                    self.add_position(segment)

    def parse_color_by_points(self, points):
        """Возвращает RGB-значение цвета еды в зависимости от ее стоимости."""
        if points <= 0:
            return color.white
        elif points < 50:
            return vector(1, 1 - points / 50, 0)  # Переход от желтого к красному
        else:
            return vector(1, 0, 0)  # Красный

    def visualize(self, canvas_instance, snake):
        """
        Визуализация объектов на заданном канвасе для одной змеи.
        :param canvas_instance: Канвас для отрисовки объектов.
        :param snake: Данные змеи (словарь).
        """
        # Очищаем все объекты на текущем канвасе
        canvas_instance.objects.clear()

        # Обновляем список текущих позиций
        self.existing_positions.clear()

        # Рисуем игровые элементы
        self.draw_fences(canvas_instance)
        self.draw_food(canvas_instance)
        self.draw_snake(canvas_instance, snake)
        self.draw_enemies(canvas_instance)

    def visualize_all(self):
        """
        Визуализирует все змеи на отдельных канвасах.
        """
        for i, snake in enumerate(self.game_state["snakes"]):
            self.visualize(self.canvases[i], snake)
