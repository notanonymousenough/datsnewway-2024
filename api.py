import aiohttp
import asyncio
import json


class Api:
    url_test = "http://games-test.datsteam.dev/play/snake3d/player/move"
    url = "http://games.datsteam.dev/play/snake3d/player/move"

    def __init__(self, token, debug=False, mock=False):
        self.debug = debug
        self.mock = mock
        self.session = aiohttp.ClientSession(headers={"X-Auth-Token": token, "Content-Type": "application/json"})

    async def move(self, req):
        if self.mock:
            return json.load(open('example_response.json', 'r'))
        async with self.session.post(url=Api.url_test if self.debug else Api.url, data=json.dumps(req)) as resp:
            if resp.status != 200:
                print(f"ERR {str(resp.status)}: {await resp.text()}")
                return None
            return json.loads(await resp.text())


    async def close(self):
        await self.session.close()