import logging
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime

logger = logging.getLogger(__name__)

class Threads:
    MAX_WORKERS = 50
    __executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @staticmethod
    def submit(function, /, *args, **kwargs) -> Future:
        return Threads.__executor.submit(function, *args, **kwargs)

    @staticmethod
    def shutdown(wait: bool = False, cancel_futures: bool = True):
        logger.info('Shutting down thread pool executor')
        Threads.__executor.shutdown(wait=wait, cancel_futures=cancel_futures)
