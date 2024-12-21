import heapq
from math import sqrt


def find_next_direction_to_center(cubes, current_position, map_size, search_radius=15, max_radius=64, max_iterations=100000):
    """
    Ищет следующий шаг для движения к положительному кубу или к центру карты,
    а также возвращает полный путь до выбранной цели.

    :param cubes: Список кубов, каждый элемент - [x, y, z, price]
    :param current_position: Текущая позиция [x, y, z]
    :param map_size: Размер карты [max_x, max_y, max_z]
    :param search_radius: Начальный радиус поиска
    :param max_radius: Максимальный радиус поиска
    :param max_iterations: Максимальное количество итераций для предотвращения зависания
    :return: Следующий шаг [dx, dy, dz] и полный путь до цели
    """
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    center_position = [map_size[i] / 2 for i in range(3)]  # Центр карты

    def is_within_bounds(position):
        """Проверяет, находится ли позиция в пределах карты."""
        return all(0 <= position[i] <= map_size[i] for i in range(3))

    def find_positive_target(radius):
        """Ищет ближайший положительный куб в пределах заданного радиуса."""
        positive_cubes = [
            (cube[:3], cube[3])
            for cube in cubes
            if cube[3] > 0
            and distance(current_position, cube[:3]) <= radius
            and is_within_bounds(cube[:3])
        ]
        positive_cubes.sort(key=lambda x: (-x[1], distance(current_position, x[0])))
        return positive_cubes[0] if positive_cubes else None

    def manhattan_distance(a, b):
        """Рассчитывает манхэттенское расстояние."""
        return sum(abs(a[i] - b[i]) for i in range(3))

    def find_safe_direction():
        """Находит безопасное направление для движения."""
        for direction in directions:
            next_position = [current_position[i] + direction[i] for i in range(3)]
            if tuple(next_position) not in negative_cubes and is_within_bounds(next_position):
                return direction, [current_position, next_position]
        return (1, 0, 0), [current_position, [current_position[0] + 1, current_position[1], current_position[2]]]  # По умолчанию "идём вперёд"

    # Разделяем кубы на положительные и отрицательные
    negative_cubes = set(tuple(cube[:3]) for cube in cubes if cube[3] <= 0)
    target = find_positive_target(search_radius)

    while not target and search_radius <= max_radius:
        search_radius *= 2
        target = find_positive_target(search_radius)

    if not target:
        # Если цель не найдена, стремимся к центру карты
        target_position = center_position
        heuristic_mode = "centering"
    else:
        target_position, _ = target
        heuristic_mode = "positive_target"

    # A* поиск пути
    visited = set()
    pq = []
    heapq.heappush(pq, (0, current_position, [], None))  # (приоритет, позиция, путь, первый шаг)
    iteration_count = 0

    while pq:
        iteration_count += 1
        if iteration_count > max_iterations:
            print(f"[LOG] Превышено максимальное количество итераций. Режим: {heuristic_mode}")
            return find_safe_direction()

        cost, position, path, first_step = heapq.heappop(pq)

        if tuple(position) in visited:
            continue
        visited.add(tuple(position))

        # Добавляем текущую позицию в путь
        path = path + [position]

        # Если достигли цели
        if position == list(target_position):
            return (first_step, path)

        # Обрабатываем каждое направление
        for direction in directions:
            next_position = [position[i] + direction[i] for i in range(3)]

            # Проверяем границы, статус препятствия и посещение
            if (
                tuple(next_position) in visited
                or tuple(next_position) in negative_cubes
                or not is_within_bounds(next_position)
            ):
                continue

            # Вычисляем эвристику
            heuristic_to_target = manhattan_distance(next_position, target_position)
            heuristic_to_center = manhattan_distance(next_position, center_position)
            heuristic = heuristic_to_target + 0.5 * heuristic_to_center

            heapq.heappush(
                pq, (cost + 1 + heuristic, next_position, path, first_step or direction)
            )

    # Если не нашли путь, возвращаем безопасное направление
    return find_safe_direction()


def distance(a, b):
    """Вычисляем евклидово расстояние между двумя точками."""
    return sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))
