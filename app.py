import asyncio
import threading
import time

from new_visualizer import SnakeGame3D
from vpython import rate

from api import Api
from cubes import find_next_direction_safe


class App:
    def __init__(self, token: str, debug: bool, mock: bool):
        self.debug = debug
        self.api = Api(token, debug, mock)

    async def run(self):
        """
        Асинхронное управление игрой с оптимизацией обновлений.
        """
        # Получаем начальное состояние игры
        game_state = await self.api.move(self.make_request())
        self.snake_game = SnakeGame3D(game_state)  # Инициализация визуализации

        while True:
            print(game_state["snakes"])
            # Получаем текущее время
            current_time = int(time.time())
            # Извлекаем змей для нового хода
            snakes = self.process_snakes(game_state)
            print("proceed new snakes:", snakes)

            # Получаем новое состояние
            req = self.make_request(snakes)

            # Асинхронная задержка

            # Если прошла новая секунда, выполняем обработку
            while current_time == int(time.time()):
                pass
            game_state = await self.api.move(req)
            self.snake_game.game_state = game_state

            # Обновляем объекты на канвасах
            self.snake_game.visualize_all()

    def process_snakes(self, res):
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
        for snake in res["snakes"]:
            if len(snake.get("geometry", [])) > 0:
                snakes.append({
                    "id": snake["id"],
                    "direction": find_next_direction_safe(cubes, snake["geometry"][0])
                })
        return snakes

    def make_request(self, snakes=None):
        if snakes is None:
            snakes = []
        return {"snakes": snakes}

    async def close(self):
        await self.api.close()