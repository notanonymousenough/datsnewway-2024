from vpython import canvas, vector, box, color, sphere, scene, rate, curve


class Snake3DVisualizer:
    def __init__(self, map_size):
        """Инициализация визуализатора."""
        self.map_size = map_size
        self.snakes = []
        self.food = []
        self.fences = []

        # Создание трех канвасов для каждой змеи
        self.canvases = []
        for i in range(3):
            self.canvases.append(canvas(title=f"Snake {i + 1}", width=600, height=600, background=color.black))

        # Сетка в виде трехмерного куба
        for c in self.canvases:
            self._create_grid(c)

    def _create_grid(self, canvas):
        """Создание трехмерной сетки в виде пустых кубов."""
        grid_color = color.gray(0.2)
        half_size = vector(self.map_size[0] / 2, self.map_size[1] / 2, self.map_size[2] / 2)

        # Грани куба
        edges = [
            # Верхняя часть
            [vector(-half_size.x, half_size.y, -half_size.z), vector(half_size.x, half_size.y, -half_size.z)],
            [vector(half_size.x, half_size.y, -half_size.z), vector(half_size.x, half_size.y, half_size.z)],
            [vector(half_size.x, half_size.y, half_size.z), vector(-half_size.x, half_size.y, half_size.z)],
            [vector(-half_size.x, half_size.y, half_size.z), vector(-half_size.x, half_size.y, -half_size.z)],

            # Нижняя часть
            [vector(-half_size.x, -half_size.y, -half_size.z), vector(half_size.x, -half_size.y, -half_size.z)],
            [vector(half_size.x, -half_size.y, -half_size.z), vector(half_size.x, -half_size.y, half_size.z)],
            [vector(half_size.x, -half_size.y, half_size.z), vector(-half_size.x, -half_size.y, half_size.z)],
            [vector(-half_size.x, -half_size.y, half_size.z), vector(-half_size.x, -half_size.y, -half_size.z)],

            # Соединяющие ребра
            [vector(-half_size.x, -half_size.y, -half_size.z), vector(-half_size.x, half_size.y, -half_size.z)],
            [vector(half_size.x, -half_size.y, -half_size.z), vector(half_size.x, half_size.y, -half_size.z)],
            [vector(half_size.x, -half_size.y, half_size.z), vector(half_size.x, half_size.y, half_size.z)],
            [vector(-half_size.x, -half_size.y, half_size.z), vector(-half_size.x, half_size.y, half_size.z)],
        ]

        for edge in edges:
            curve(canvas=canvas, pos=edge, color=grid_color)

    def update_snakes(self, snake_data):
        print(snake_data)
        """Обновление позиций змей и привязка камеры к головам."""
        for i, snake in enumerate(snake_data):
            if i >= len(self.canvases):
                break

            canvas = self.canvases[i]
            body_color = color.blue
            head_color = color.cyan

            # Очистка предыдущей змеи
            if i < len(self.snakes):
                for segment in self.snakes[i]:
                    segment.visible = False

            # Создание змеи
            snake_geometry = []
            for idx, segment in enumerate(snake['geometry']):
                segment_color = head_color if idx == 0 else body_color
                snake_geometry.append(
                    box(canvas=canvas, pos=vector(*segment), size=vector(1, 1, 1), color=segment_color)
                )

            # Привязка камеры к голове змеи
            if len(snake['geometry']) > 0:
                canvas.center = vector(*snake['geometry'][0])  # Камера направлена в центр головы
                canvas.forward = vector(0, -1, 0)  # Смотрит вниз

            # Сохранение геометрии змеи
            if i < len(self.snakes):
                self.snakes[i] = snake_geometry
            else:
                self.snakes.append(snake_geometry)

    def update_food(self, food_data):
        print(food_data)
        """Обновление еды."""
        for food in self.food:
            food.visible = False

        self.food = []
        for food_item in food_data:
            food_color = self._get_food_color(food_item['points'])
            self.food.append(
                sphere(pos=vector(*food_item['c']), radius=0.3, color=food_color)
            )

    def update_fences(self, fence_data):
        print(fence_data)
        """Обновление препятствий."""
        for fence in self.fences:
            fence.visible = False

        self.fences = []
        for fence_item in fence_data:
            self.fences.append(
                box(pos=vector(*fence_item), size=vector(1, 1, 1), color=color.green)
            )

    def _get_food_color(self, points):
        """Получить цвет еды в зависимости от её стоимости."""
        if points <= 0:
            return color.white
        elif points < 5:
            return color.yellow
        elif points < 10:
            return color.orange
        else:
            return color.red

    def run(self):
        """Основной цикл игры."""
        while True:
            rate(10)
            # Здесь можно обновлять состояния змей, еды и препятствий, вызывая соответствующие методы.
