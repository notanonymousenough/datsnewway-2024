import heapq
from math import sqrt


def find_next_direction_safe(cubes, current_position, search_radius=15, max_radius=100):
    """
    Функция для определения безопасного направления движения,
    с учётом необходимости избегания стенок (отрицательных кубов)
    и расширения радиуса в случае отсутствия целей.

    :param cubes: Список кубов, каждый элемент - [x, y, z, price]
    :param current_position: Текущая позиция нашего куба [x, y, z]
    :param search_radius: Начальный радиус поиска
    :param max_radius: Максимально допустимый радиус (чтобы избежать бесконечных расширений)
    :return: Вектор направления движения [dx, dy, dz]
    """
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

    def find_positive_target(radius):
        """
        Ищет ближайший положительный куб в пределах указанного радиуса.
        Возвращает цель и её позицию.
        """
        positive_cubes = [
            (cube[:3], cube[3])
            for cube in cubes
            if cube[3] > 0 and distance(current_position, cube[:3]) <= radius
        ]

        # Сортируем положительные кубы по убыванию цены и минимальному расстоянию
        positive_cubes.sort(key=lambda x: (-x[1], distance(current_position, x[0])))

        return positive_cubes[0] if positive_cubes else None

    def find_safe_direction():
        """
        Находит любое безопасное направление для движения.
        """
        safe_directions = []
        for direction in directions:
            next_position = [current_position[i] + direction[i] for i in range(3)]
            if tuple(next_position) not in negative_cubes:
                safe_directions.append(direction)

        # Если нет негативной позиции, выбираем любое безопасное направление
        return safe_directions[0] if safe_directions else (1, 0, 0)  # По умолчанию "идём вперёд"

    # Разделяем кубы на положительные и отрицательные
    negative_cubes = set(tuple(cube[:3]) for cube in cubes if cube[3] <= 0)
    target = find_positive_target(search_radius)

    # Если целей нет в пределах текущего радиуса
    while not target and search_radius <= max_radius:
        search_radius *= 2  # Увеличиваем радиус вдвое
        target = find_positive_target(search_radius)

    if not target:
        # Спасаемся, если нет целей даже после расширения радиуса
        return find_safe_direction()

    target_position, _ = target

    # A* для поиска пути к цели
    visited = set()
    pq = []
    heapq.heappush(pq, (0, current_position, None))  # Начальная позиция с нулевой стоимостью

    while pq:
        cost, position, first_step = heapq.heappop(pq)

        if tuple(position) in visited:
            continue
        visited.add(tuple(position))

        # Если достигли цели
        if position == list(target_position):
            return first_step  # Возвращаем первый шаг для достижения цели

        # Рассматриваем все возможные направления
        for direction in directions:
            next_position = [position[i] + direction[i] for i in range(3)]
            if tuple(next_position) in visited or tuple(next_position) in negative_cubes:
                continue  # Пропускаем уже посещённые или запрещённые позиции

            # Вычисляем эвристику: расстояние до цели
            heuristic = distance(next_position, target_position)
            heapq.heappush(
                pq,
                (cost + 1 + heuristic, next_position, first_step or direction)
            )

    # Если пути к цели не найдено, спасаемся
    return find_safe_direction()


def distance(a, b):
    """Вычисляем евклидово расстояние между двумя точками."""
    return sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))
