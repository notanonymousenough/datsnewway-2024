import heapq
from math import sqrt


def find_next_direction_optimized(cubes, current_position, map_size, search_radius=15, max_radius=64, max_iterations=10000):
    """
    Оптимизированная функция для выбора направления движения, основанная на A* с приоритетом дорогих кубов.
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

    # Сортируем положительные кубы на основе "цена / расстояние"
    positive_cubes.sort(key=lambda x: (-x[1], distance(current_position, x[0])))
    if not positive_cubes:
        return [(0, 0, 0), []]  # Если нет положительных кубов в радиусе, возвращаем вектор (0, 0, 0)

    # A* Search для нахождения пути
    target_position, _ = positive_cubes[0]  # Выбираем самый "ценный" доступный куб
    visited = set()
    pq = []  # Очередь с приоритетом: (стоимость, позиция, путь)
    heapq.heappush(pq, (0, current_position, []))

    while pq:
        cost, position, path = heapq.heappop(pq)
        if tuple(position) in visited:
            continue
        visited.add(tuple(position))
        # Если достигли целевой позиции
        if position == list(target_position):
            return [path[0], path] if path else [(0, 0, 0), []]

        # Рассматриваем все направления
        for direction in directions:
            next_position = [position[i] + direction[i] for i in range(3)]
            if tuple(next_position) in visited or tuple(next_position) in negative_cubes:
                continue  # Пропускаем посещенные и "отрицательные" позиции
            # Вычисляем приоритет с учётом эвристики (манхэттенское расстояние)
            heuristic = distance(next_position, target_position)
            heapq.heappush(
                pq, (cost + 1 + heuristic, next_position, path + [direction])
            )
    # Если пути не найдено, остаемся на месте
    return [(0, 0, 0), []]


def distance(a, b):
    """Расчет евклидова расстояния между двумя точками."""
    return sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))