import heapq
from math import sqrt


class Cubes:
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

    @staticmethod
    def find_next_direction_to_center(
        cubes, current_position, map_size, is_next_tick, search_radius=15, max_radius=64,
        max_iterations=1000000
    ):
        """
        Ищет следующий шаг для движения к положительному кубу или к центру карты.
        В режиме centering не строится полный путь до центра: выбирается вариант, минимизирующий расстояние.
        """
        center_position = [map_size[i] / 2 for i in range(3)]  # Центр карты

        def find_positive_target(radius):
            """Ищет ближайший положительный куб в пределах заданного радиуса."""
            positive_cubes = [
                (cube[:3], cube[3])
                for cube in cubes
                if cube[3] > 0
                and distance(current_position, cube[:3]) <= radius
                and Cubes.is_within_bounds(cube[:3], map_size)
            ]
            positive_cubes.sort(key=lambda x: (-x[1], distance(current_position, x[0])))
            return positive_cubes[0] if positive_cubes else None

        def distance(a, b):
            """Рассчитывает евклидово расстояние (или квадратичную метрику)."""
            return sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))

        def evaluate_centering():
            """
            В режиме centering:
            - Рассматриваем каждый возможный шаг.
            - Выбираем направление, уменьшающее расстояние до центра.
            """
            best_step = None
            best_distance = float("inf")
            path = []

            for direction in Cubes.directions:
                next_position = [current_position[i] + direction[i] for i in range(3)]

                # Проверяем, чтобы следующий шаг был безопасным
                if (
                    tuple(next_position) in negative_cubes
                    or not Cubes.is_within_bounds(next_position, map_size)
                ):
                    continue

                # Вычисляем расстояние до центра из новой позиции
                new_distance = distance(next_position, center_position)

                # Если нашли направление с минимальным уменьшением расстояния
                if new_distance < best_distance:
                    best_distance = new_distance
                    best_step = direction
                    path = [current_position, next_position]

            return best_step, path

        # Разделяем кубы на положительные и отрицательные
        negative_cubes = set(tuple(cube[:3]) for cube in cubes if cube[3] <= 0)
        target = find_positive_target(search_radius)
        mode = "positive_target" if target else "centering"

        # Если мы ищем положительную цель
        while not target and search_radius <= max_radius:
            search_radius *= 2
            target = find_positive_target(search_radius)

        if not target:
            # Если цель не найдена, переключаемся на режим 'centering'
            print("[LOG] Режим centering: минимизация расстояния до центра.")
            return evaluate_centering()

        print("[LOG] found target", target)
        # Если цель найдена, мы строим путь к ней
        target_position, _ = target
        visited = set()
        pq = []
        heapq.heappush(pq, (0, current_position, [], None))  # (приоритет, позиция, путь, первый шаг)
        iteration_count = 0

        best_first_step = None

        while pq:
            iteration_count += 1
            if iteration_count > max_iterations:
                if mode == "positive_target":
                    # Если мы в режиме поиска цели и превышен лимит итераций, переключаемся на центр карты
                    print("[LOG] Переключение на центр карты из positive_target после превышения итераций.")
                    return evaluate_centering()

            if is_next_tick():
                print("[LOG] Переключение на центр карты из positive_target после начала следующего тика.")
                return evaluate_centering()

            cost, position, path, first_step = heapq.heappop(pq)

            if tuple(position) in visited:
                continue
            visited.add(tuple(position))

            # Добавляем текущую позицию в путь
            path = path + [position]

            # Если достигли цели
            if position == list(target_position):
                if not best_first_step:
                    best_first_step = first_step  # Зафиксировать первый шаг
                return best_first_step, path

            # Обрабатываем каждое направление
            for direction in Cubes.directions:
                next_position = [position[i] + direction[i] for i in range(3)]

                # Проверяем границы, статус препятствия и посещение
                if (
                        tuple(next_position) in visited
                        or tuple(next_position) in negative_cubes
                        or not Cubes.is_within_bounds(next_position, map_size)
                ):
                    continue

                # Используем эвристику: расстояние до цели
                heuristic_to_target = distance(next_position, target_position)
                heapq.heappush(
                    pq, (cost + 1 + heuristic_to_target, next_position, path, first_step or direction)
                )

        # Если не нашли путь, возвращаем безопасное направление
        return Cubes.find_safe_direction(current_position, negative_cubes, map_size)

    @staticmethod
    def find_safe_direction(current_position, negative_cubes, map_size):
        """Находит безопасное направление для движения."""
        for direction in Cubes.directions:
            next_position = [current_position[i] + direction[i] for i in range(3)]
            if tuple(next_position) not in negative_cubes and Cubes.is_within_bounds(next_position, map_size):
                return direction, [current_position, next_position]
        return (
            (1, 0, 0),
            [
                current_position,
                [current_position[0] + 1, current_position[1], current_position[2]],
            ],
        )  # По умолчанию "идём вперёд"

    @staticmethod
    def is_within_bounds(position, map_size):
        """Проверяет, что позиция внутри границ карты."""
        return all(0 <= position[i] <= map_size[i] for i in range(3))