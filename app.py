import asyncio
import threading
import time

from new_visualizer import SnakeGame3D
from vpython import rate

from api import Api
from cubes import find_next_direction_to_center


class App:
    def __init__(self, token: str, debug: bool, mock: bool):
        self.debug = debug
        self.api = Api(token, debug, mock)

    async def run(self):
        """
        Асинхронное управление игрой с оптимизацией обновлений.
        """
        # Получаем начальное состояние игры
        # Получаем текущее время
        current_time = time.time() * 1000
        game_state = await self.api.move(self.make_request())
        while game_state is None:
            await asyncio.sleep(0.5)
            print("retrying...")
            game_state = await self.api.move(self.make_request())
        new_tick_time = game_state["tickRemainMs"] + current_time
        self.snake_game = SnakeGame3D(game_state)  # Инициализация визуализации
        previous_paths = None

        while True:
            print(game_state["snakes"])
            current_ns = time.time_ns()
            # Извлекаем змей для нового хода
            snakes, previous_paths = self.process_snakes(game_state, previous_paths)
            print(f"proceed new snakes [{str(time.time_ns()-current_ns)}ns]:", snakes)
            print("paths:", previous_paths)
            self.snake_game.paths = previous_paths
            # Получаем новое состояние
            req = self.make_request(snakes)

            # Если прошла новая секунда, выполняем обработку
            while time.time()*1000 < new_tick_time:
                pass
            game_state = await self.api.move(req)
            while game_state is None:
                await asyncio.sleep(0.5)
                print("retrying...")
                game_state = await self.api.move(req)
            # Получаем текущее время
            current_time = time.time() * 1000
            new_tick_time = game_state["tickRemainMs"] + current_time
            # Обновляем объекты на канвасах
            self.snake_game.visualize_all()
            self.snake_game.game_state = game_state

    def process_snakes(self, res, previous_paths=None):
        snakes = []
        cubes = []
        maxFoodPrice = 0
        for fence in res["fences"]:
            cubes.append(fence + [-100])
        for enemy in res["enemies"]:
            if len(enemy.get("geometry", [])) == 0:
                continue
            for cube in enemy["geometry"]:
                cubes.append(cube + [-100])
            # голова может сдвинуться в любую сторону, учитываем
            head = enemy["geometry"][0]
            cubes.append([head[0]-1, head[1], head[2], -75])
            cubes.append([head[0]+1, head[1], head[2], -75])
            cubes.append([head[0], head[1]-1, head[2], -75])
            cubes.append([head[0], head[1]+1, head[2], -75])
            cubes.append([head[0], head[1], head[2]-1, -75])
            cubes.append([head[0], head[1], head[2]+1, -75])
        for snake in res["snakes"]:
            if len(snake.get("geometry", [])) == 0:
                continue
            for cube in snake["geometry"]:
                cubes.append(cube + [-100])
        for food in res["food"]:
            if food["points"] > maxFoodPrice:
                maxFoodPrice = food["points"]
            cubes.append(food["c"] + [food["points"]])
        for golden in res["specialFood"]["golden"]:
            cubes.append(golden + [maxFoodPrice*10])
        for suspicious in res["specialFood"]["suspicious"]:
            cubes.append(suspicious + [-50])
        print(f"got {str(len(cubes))} cubes")
        paths = {}
        for snake in res["snakes"]:
            if len(snake.get("geometry", [])) > 0:
                id = snake["id"]
                path = None
                if previous_paths is not None:
                    path = previous_paths.get(id, [])
                direction, path = find_next_direction_to_center(cubes, snake["geometry"][0], res["mapSize"], previous_path=path)
                snakes.append({
                    "id": snake["id"],
                    "direction": direction
                })
                paths[snake["id"]] = path
                print(f"proceed snake {id}")
        return snakes, paths

    def make_request(self, snakes=None):
        if snakes is None:
            snakes = []
        return {"snakes": snakes}

    async def close(self):
        await self.api.close()