import heapq
from math import sqrt


def find_next_direction_to_center(
    cubes, current_position, map_size, search_radius=15, max_radius=64,
    max_iterations=10000, previous_path=None
):
    """
    Ищет следующий шаг для движения к положительному кубу или к центру карты.
    В режиме centering путь рассчитывается только на несколько шагов вперед.
    """
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    center_position = [map_size[i] / 2 for i in range(3)]  # Центр карты
    max_steps_in_centering = 5  # Максимальное количество шагов в режиме centering

    def is_within_bounds(position):
        """Проверяет, что позиция внутри границ карты."""
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
        return (
            (1, 0, 0),
            [
                current_position,
                [current_position[0] + 1, current_position[1], current_position[2]],
            ],
        )  # По умолчанию "идём вперёд"

    # Разделяем кубы на положительные и отрицательные
    negative_cubes = set(tuple(cube[:3]) for cube in cubes if cube[3] <= 0)
    target = find_positive_target(search_radius)
    mode = "positive_target" if target else "centering"

    while not target and search_radius <= max_radius:
        search_radius *= 2
        target = find_positive_target(search_radius)

    if not target:
        # Если цель не найдена, сменяем цель на движение к центру карты
        target_position = center_position
        mode = "centering"
    else:
        target_position, _ = target

    # A* поиск пути
    visited = set()
    pq = []
    heapq.heappush(pq, (0, current_position, [], None))  # (приоритет, позиция, путь, первый шаг)
    iteration_count = 0

    while pq:
        iteration_count += 1
        if iteration_count > max_iterations:
            if mode == "positive_target":
                # Если мы в режиме поиска цели и превышен лимит итераций, переключаемся на центр карты
                print("[LOG] Переключение на центр карты из positive_target после превышения итераций.")
                target_position = center_position
                mode = "centering"
                pq = []  # Сбрасываем очередь для нового режима
                heapq.heappush(pq, (0, current_position, [], None))
                visited = set()
                iteration_count = 0
                continue

            elif mode == "centering":
                # Если превышен лимит итераций в режиме стремления к центру
                print("[LOG] Превышено максимальное количество итераций. Режим: centering")
                return find_safe_direction()

        cost, position, path, first_step = heapq.heappop(pq)

        if tuple(position) in visited:
            continue
        visited.add(tuple(position))

        # Добавляем текущую позицию в путь
        path = path + [position]

        # Если достигли цели
        if position == list(target_position):
            # В режиме centering ограничиваем путь 5 шагами
            if mode == "centering":
                path = path[:max_steps_in_centering + 1]  # Оставляем до 5 шагов
            return first_step, path

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