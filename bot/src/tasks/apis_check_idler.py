import asyncio
from udatetime import now
from bot.src.utils.constants import logger
from bot.src.utils.config import apischeck_minutes as constant_minutes

variable_minutes = constant_minutes

async def task():
    global variable_minutes
    msg = None
    while True:
        try:
            from bot.src.utils.config import apischeck_minutes as variable_minutes
            from bot.src.utils.proxies import last_apis_interaction
            if (now() - last_apis_interaction).seconds > (constant_minutes * 60) - 9:
                if not msg:
                    logger.info("IDLER ON")
                    msg = True
                variable_minutes = 60
            else:
                if msg:
                    logger.info("IDLER OFF")
                    msg = None
                variable_minutes = constant_minutes
        except asyncio.CancelledError:
            break
        await asyncio.sleep(10)