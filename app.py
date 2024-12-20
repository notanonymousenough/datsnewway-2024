import asyncio
import threading
from math import sqrt
from vizualizer import Snake3DVisualizer

from api import Api
from threading import Thread


class App:
    def __init__(self, token: str, debug: bool):
        self.debug = debug
        self.api = Api(token, debug)
        self.visualizer = Snake3DVisualizer([20, 20, 20])

    async def run(self):
        snakes = []
        while True:
            req = {"snakes": snakes}
            res = await self.api.move(req)
            self.visualizer.update_food(res["food"])
            self.visualizer.update_fences(res["fences"])
            self.visualizer.update_snakes(res["snakes"])
            snakes = self.get_snakes(res)
            await asyncio.sleep(1)

    def get_snakes(self, res):
        return []

    async def close(self):
        await self.api.close()