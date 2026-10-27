"""Einstiegspunkt für Desktop und pygbag/WebAssembly."""
import asyncio
from game import Game


async def main():
    await Game().run()


if __name__ == "__main__":
    asyncio.run(main())
