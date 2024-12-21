import heapq
from math import sqrt


def find_next_direction_safe(cubes, current_position, map_size, search_radius=15, max_radius=64, max_iterations=10000):
    """
    Функция с оптимизированным поиском пути через A*, ограничением итераций и эвристикой манхэттена.
    """

    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

    def is_within_bounds(position):
        """Проверка, что позиция внутри границ карты."""
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
        """Рассчитывает более простую манхэттенскую эвристику."""
        return sum(abs(a[i] - b[i]) for i in range(3))

    def find_safe_direction():
        """Находит безопасное направление движения."""
        for direction in directions:
            next_position = [current_position[i] + direction[i] for i in range(3)]
            if tuple(next_position) not in negative_cubes and is_within_bounds(next_position):
                return direction
        return (1, 0, 0)  # Если всё занято, идём вперёд по умолчанию.

    # Разделяем кубы на положительные и отрицательные
    negative_cubes = set(tuple(cube[:3]) for cube in cubes if cube[3] <= 0)

    # Ищем цель в пределах заданного радиуса
    target = find_positive_target(search_radius)
    while not target and search_radius <= max_radius:
        search_radius *= 2  # Увеличиваем радиус, если цели нет
        target = find_positive_target(search_radius)

    if not target:
        # Если цель не найдена, возвращаем безопасное направление
        return find_safe_direction()

    target_position, _ = target

    # A* поиск пути
    visited = set()
    pq = []
    heapq.heappush(pq, (0, current_position, None))  # (приоритет, позиция, первый шаг)
    iteration_count = 0

    while pq:
        iteration_count += 1
        if iteration_count > max_iterations:
            # Если достигли предела по итерациям, возвращаем безопасное направление
            print("[LOG] Превышено максимальное количество итераций в A*. Возвращаем безопасное направление.")
            return find_safe_direction()

        cost, position, first_step = heapq.heappop(pq)

        if tuple(position) in visited:
            continue
        visited.add(tuple(position))

        # Если достигли цели
        if position == list(target_position):
            return first_step

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

            # Используем манхэттенскую эвристику
            heuristic = manhattan_distance(next_position, target_position)
            heapq.heappush(
                pq, (cost + 1 + heuristic, next_position, first_step or direction)
            )

    # Если не нашли путь, возвращаем безопасное направление
    return find_safe_direction()


def distance(a, b):
    """Вычисляем евклидово расстояние между двумя точками."""
    return sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))
