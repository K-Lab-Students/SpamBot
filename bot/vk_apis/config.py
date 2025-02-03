import os
from dotenv import load_dotenv
from .utils.logger import logger

load_dotenv()


class Config:
    @property
    def group_token(self):
        return os.getenv('GROUP_TOKEN')

    @property
    def group_id(self):
        return int(os.getenv('GROUP_ID'))

    @property
    def riddles(self):
        riddles_str = os.getenv('RIDDLES')
        if not riddles_str:
            logger.error("RIDDLES environment variable is not set")
            return [["Сколько букв в аббревиатуре ФКТИПМ?", "6"]] 
        try:
            result = eval(riddles_str)

            if not isinstance(result, list) or not all(isinstance(item, list) and len(item) == 2 for item in result):
                logger.error("RIDDLES format is invalid")
                return [["Сколько букв в аббревиатуре ФКТИПМ?", "6"]]
            logger.info(f"Successfully loaded {len(result)} riddles")
            return result
        except Exception as e:
            logger.error(f"RIDDLES parsing error: {e}")
            logger.debug(f"Attempted to parse: {riddles_str}")
            return [["Сколько букв в аббревиатуре ФКТИПМ?", "6"]]

    @property
    def greeting_message(self):
        return os.getenv('GREETING_MESSAGE')

    @property
    def ban_message(self):
        return os.getenv('BAN_MESSAGE')

    @property
    def max_attempts(self):
        return int(os.getenv('MAX_ATTEMPTS', 2))

    @property
    def wait_time(self):
        return int(os.getenv('WAIT_TIME', 60)) 