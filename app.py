import asyncio
import threading
from new_visualizer import SnakeGame3D
from vpython import rate

from api import Api


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
            # Извлекаем змей для нового хода
            snakes = self.get_snakes(game_state)
            print("got new snakes:", snakes)

            # Получаем новое состояние
            game_state = await self.api.move(self.make_request(snakes))
            self.snake_game.game_state = game_state

            # Обновляем объекты на канвасах
            for i, snake in enumerate(game_state["snakes"]):
                self.snake_game.visualize(self.snake_game.canvases[i], snake)

            # Асинхронная задержка для плавного обновления
            await asyncio.sleep(1)

    def get_snakes(self, res):
        return []

    def make_request(self, snakes=None):
        if snakes is None:
            snakes = []
        return {"snakes": snakes}

    async def close(self):
        await self.api.close()