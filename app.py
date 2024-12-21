import asyncio
import threading
from new_visualizer import SnakeGame3D
from vpython import rate

from api import Api
from cubes import find_next_direction_optimized


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
            # Извлекаем змей для нового хода
            snakes = self.process_snakes(game_state)
            print("proceed new snakes:", snakes)

            # Получаем новое состояние
            game_state = await self.api.move(self.make_request(snakes))
            self.snake_game.game_state = game_state

            # Обновляем объекты на канвасах
            self.snake_game.visualize_all()

            # Асинхронная задержка для плавного обновления
            await asyncio.sleep(0.9)

    def process_snakes(self, res):
        snakes = []
        cubes = []
        maxFoodPrice = 0
        for fence in res["fences"]:
            cubes.append(fence + [-100])
        for enemy in res["enemies"]:
            for cube in enemy["geometry"]:
                cubes.append(cube + [-100])
        for snake in res["snakes"]:
            for cube in snake["geometry"]:
                cubes.append(cube + [-100])
        for food in res["food"]:
            if food["points"] > maxFoodPrice:
                maxFoodPrice = food["points"]
            cubes.append(food["c"] + [food["points"]])
        for golden in res["specialFood"]["golden"]:
            cubes.append(golden + [maxFoodPrice*100])
        for suspicious in res["specialFood"]["suspicious"]:
            cubes.append(suspicious + [-50])
        print(f"got {str(len(cubes))} cubes")
        for snake in res["snakes"]:
            if len(snake.get("geometry", [])) > 0:
                snakes.append({
                    "id": snake["id"],
                    "direction": find_next_direction_optimized(cubes, snake["geometry"][0])
                })
        return snakes

    def make_request(self, snakes=None):
        if snakes is None:
            snakes = []
        return {"snakes": snakes}

    async def close(self):
        await self.api.close()