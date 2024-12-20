import asyncio
from vizualizer import SnakeMap, rate

from api import Api


class App:
    def __init__(self, token: str, debug: bool, mock: bool):
        self.debug = debug
        self.api = Api(token, debug, mock)

    async def run(self):
        # Получаем начальное состояние игры
        game_state = await self.api.move(self.make_request())
        if not game_state:
            print("Не удалось получить начальное состояние игры.")
            await self.close()

        # Ограничение: до 3 змей
        snakes_data = game_state["snakes"][:3]
        fences = game_state["fences"]  # Преграды
        position_offsets = [[-300, 0, 0], [0, 0, 0], [300, 0, 0]]  # Сдвиги для трех змей
        snake_maps = [SnakeMap(snake_data, offset, fences) for snake_data, offset in zip(snakes_data, position_offsets)]

        # Еда
        food_items = []
        for snake_map in snake_maps:
            food_items.append(SnakeMap.draw_food(game_state["food"], snake_map.scene))

        while True:
            rate(10)  # Перерисовка каждые 10 кадров

            # Составляем запрос на движения всех змей
            snakes_payload = []
            for i, snake_map in enumerate(snake_maps):
                direction = [int(snake_map.direction.x), int(snake_map.direction.y), int(snake_map.direction.z)]
                snakes_payload.append({"id": snake_map.id, "direction": direction})

            # Запрашиваем новое состояние игры
            game_response = await self.api.move(self.make_request(snakes_payload))
            if game_response:
                for i, new_snake_data in enumerate(game_response["snakes"]):
                    snake_maps[i].update(new_snake_data["geometry"], new_snake_data["direction"])

                # Обновляем еду
                for i, snake_map in enumerate(snake_maps):
                    for item in food_items[i]:
                        item.visible = False  # Удаляем предыдущую еду
                    food_items[i] = SnakeMap.draw_food(game_response["food"], snake_map.scene)

    def get_snakes(self, res):
        return []

    def make_request(self, snakes=None):
        if snakes is None:
            snakes = []
        return {"snakes": snakes}

    async def close(self):
        await self.api.close()