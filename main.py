import asyncio
import traceback
from app import App

with open("token", 'r') as file:
    TOKEN = file.read()
DEBUG = True


async def main():
    app = App(TOKEN, DEBUG)
    try:
        await app.run()
    except Exception as e:
        await app.close()
        print(e)
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())