import asyncio
import operator
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from new_visualizer import SnakeGame3D
from vpython import rate

from api import Api
from cubes import Cubes


class App:
    def __init__(self, token: str, debug: bool, mock: bool):
        self.debug = debug
        self.api = Api(token, debug, mock)
        self.running = True

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
        self.new_tick_time = game_state["tickRemainMs"] + current_time
        self.snake_game = SnakeGame3D(game_state)  # Инициализация визуализации

        # Создаем новый event loop для asyncio
        self.loop = asyncio.new_event_loop()

        # Запускаем asyncio loop в отдельном потоке
        self.thread = threading.Thread(target=self.start_async_loop_in_thread)
        self.thread.start()

        while True:
            print(game_state["snakes"])
            # Извлекаем змей для нового хода
            snakes, paths = self.process_snakes(game_state)
            print("paths:", paths)
            self.snake_game.paths = paths
            # Получаем новое состояние
            req = self.make_request(snakes)

            # Если прошла новая секунда, выполняем обработку
            print("LOOP BEFORE WHILE:", (time.time() * 1000 - current_time)/1000)
            while not self.is_new_tick():
                pass
            print("LOOP AFTER WHILE:", (time.time() * 1000 - current_time)/1000)
            game_state = await self.api.move(req)
            print("LOOP AFTER CALL:", (time.time() * 1000 - current_time)/1000)
            while game_state is None:
                await asyncio.sleep(0.5)
                print("retrying...")
                game_state = await self.api.move(req)
            # Получаем текущее время
            current_time = time.time() * 1000
            self.new_tick_time = game_state["tickRemainMs"] + current_time
            self.snake_game.game_state = game_state

    def start_async_loop_in_thread(self):
        """Функция для запуска asyncio event loop в отдельном потоке."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.game_loop())

    async def game_loop(self):
        while self.running:
            await self.snake_game.visualize_all_async()

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
            for cube in snake["geometry"][1:]:
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
        negative_cubes = set(tuple(cube[:3]) for cube in cubes if cube[3] <= 0)

        paths = {}

        # threads
        # with ThreadPoolExecutor() as executor:
        #     future_to_snake = {}
        #
        #     for snake in res["snakes"]:
        #         if len(snake.get("geometry", [])) > 0:
        #             id = snake["id"]
        #             if self.is_new_tick():
        #                 print("new tick! running find_safe_direction")
        #                 future = executor.submit(Cubes.find_safe_direction,
        #                                          snake["geometry"][0],
        #                                          negative_cubes,
        #                                          res["mapSize"])
        #             else:
        #                 future = executor.submit(Cubes.find_next_direction_to_center,
        #                                          cubes,
        #                                          snake["geometry"][0],
        #                                          res["mapSize"],
        #                                          self.is_new_tick)
        #
        #             future_to_snake[future] = id
        #
        #             # Collect results as they complete
        #     for future in as_completed(future_to_snake):
        #         id = future_to_snake[future]
        #         try:
        #             direction, path = future.result()
        #             snakes.append({
        #                 "id": id,
        #                 "direction": direction
        #             })
        #             paths[id] = path
        #             print(f"proceed snake {id}")
        #         except Exception as exc:
        #             print(f"Snake {id} generated an exception: {exc}")

        for snake in res["snakes"]:
            if len(snake.get("geometry", [])) > 0:
                id = snake["id"]
                if self.is_new_tick():
                    print("new tick! running find_safe_direction")
                    direction, path = Cubes.find_safe_direction(snake["geometry"][0], negative_cubes, res["mapSize"])
                else:
                    direction, path = Cubes.find_next_direction_to_center(cubes, snake["geometry"][0], res["mapSize"],
                                                                          self.is_new_tick)
                snakes.append({
                    "id": snake["id"],
                    "direction": direction
                })
                paths[snake["id"]] = path
                print(f"proceed snake {id} {str(direction)} {str(path)}")

        return snakes, paths

    def make_request(self, snakes=None):
        if snakes is None:
            snakes = []
        return {"snakes": snakes}

    async def close(self):
        await self.api.close()
        self.running = False
        self.loop.stop()
        self.thread.join()

    def is_new_tick(self):
        return time.time() * 1000 > self.new_tick_time