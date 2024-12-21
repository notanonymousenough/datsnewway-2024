import heapq
from math import sqrt


def find_next_direction_optimized(cubes, current_position, search_radius=15):
    """
    Оптимизированная функция для выбора направления движения, исправляющая проблемы зацикливания.

    :param cubes: Список кубов, каждый элемент - [x, y, z, price]
    :param current_position: Текущая позиция нашего куба [x, y, z]
    :param search_radius: Радиус для учета ближайших кубов (ускоряет поиск)
    :return: Вектор направления движения [dx, dy, dz]
    """
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

    # Разделяем кубы на положительные и отрицательные
    positive_cubes = [
        (cube[:3], cube[3])
        for cube in cubes
        if cube[3] > 0 and distance(current_position, cube[:3]) <= search_radius
    ]
    negative_cubes = set(tuple(cube[:3]) for cube in cubes if cube[3] <= 0)

    if not positive_cubes:
        return (0, 0, 0)  # Если положительных кубов нет, остаёмся на месте

    # Сортируем положительные кубы на основе "цена / расстояние"
    positive_cubes.sort(key=lambda x: (-x[1], distance(current_position, x[0])))

    # Берём ближайший максимально ценностный куб
    target_position, _ = positive_cubes[0]

    # Priority Queue для поиска пути
    visited = set()
    pq = []
    heapq.heappush(pq, (0, current_position, None))  # Начальная позиция с нулевой стоимостью

    # A* с приоритетами
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

    # Если пути вообще не найдено, остаёмся на месте
    return (0, 0, 0)


def distance(a, b):
    """Вычисляем евклидово расстояние между двумя точками."""
    return sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))