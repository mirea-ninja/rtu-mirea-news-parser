import logging
import time

import schedule
from config import get_settings
from news_parser import NewsParser

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def parse(api_url: str, api_token: str):
    parser = NewsParser(api_url, api_token)
    parser.run()


if __name__ == "__main__":
    settings = get_settings()
    parse(settings.API_URL, settings.API_TOKEN)
    schedule.every(1).minutes.do(parse, settings.API_URL, settings.API_TOKEN)

    while True:
        schedule.run_pending()
        time.sleep(1)
