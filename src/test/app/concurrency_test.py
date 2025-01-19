import asyncio
import logging.config
import unittest
from datetime import datetime

from test.app.test_functions import get_logging_config

logging.config.dictConfig(get_logging_config())

# class Coroutines:
#     __eventloop = None
#
#     @staticmethod
#     def init():
#         logger.info("Initializing app thread pool executor.")
#         Coroutines.__eventloop = asyncio.new_event_loop()
#         threading.Thread(target=Coroutines.__eventloop.run_forever).start()
#
#     @staticmethod
#     def run(coroutine) -> Future:
#         return asyncio.run_coroutine_threadsafe(coroutine, Coroutines.__eventloop)
#
#     @staticmethod
#     def shutdown():
#         if Coroutines.__eventloop is None:
#             logger.warning(
#                 'Skipping shutdown of app event loop, as it was never initialized.')
#             return
#         logger.info('Shutting down app event loop.')
#         try:
#             if Coroutines.__eventloop.is_running() is True:
#                 Coroutines.__eventloop.call_soon_threadsafe(Coroutines.__eventloop.stop)
#         except Exception as ex:
#             logger.error(f"Error while shutting down app event loop: {ex}")

class ConcurrencyTestCase(unittest.IsolatedAsyncioTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    async def task():
        print(f"{datetime.now()} Sleeping for 1 second.")
        await asyncio.sleep(1)
        print(f"{datetime.now()} Done sleeping for 1 second")
        return 1
    #
    # @staticmethod
    # async def test_coroutine_lifecycle():
    #     try:
    #         Coroutines.init()
    #         result = Coroutines.run(ConcurrencyTestCase.task()).result()
    #         print(f"{datetime.now()} Task result: {result}")
    #     finally:
    #         Coroutines.shutdown()

    @staticmethod
    def test_asyncio_new_event_loop():
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(ConcurrencyTestCase.task())
            print(f"{datetime.now()} Result: {result}")
        finally:
            loop.call_soon_threadsafe(loop.stop)

    @staticmethod
    def test_asyncio_run():
        result = asyncio.run(ConcurrencyTestCase.task())
        print(f"{datetime.now()} Result: {result}")


if __name__ == '__main__':
    unittest.main()
