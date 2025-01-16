import logging
from concurrent.futures import Future, ThreadPoolExecutor

logger = logging.getLogger(__name__)

class Threads:
    __executor = None

    @staticmethod
    def init(max_workers: int = 50):
       Threads.__executor = ThreadPoolExecutor(max_workers=max_workers)

    @staticmethod
    def submit(function, /, *args, **kwargs) -> Future:
        return Threads.__executor.submit(function, *args, **kwargs)

    @staticmethod
    def shutdown(wait: bool = False, cancel_futures: bool = True):
        if Threads.__executor is None:
            logger.warning('Skipping shutdown of thread pool executor, as it was never initialized.')
            return
        logger.info('Shutting down thread pool executor.')
        Threads.__executor.shutdown(wait=wait, cancel_futures=cancel_futures)
