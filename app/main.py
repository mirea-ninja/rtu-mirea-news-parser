import schedule
import time
import sentry_sdk
from news_parser import NewsParser
from config import get_settings


def parse(api_url: str, api_token: str):
    parser = NewsParser(api_url, api_token)
    parser.run()


if __name__ == '__main__':
    settings = get_settings()

    if settings.sentry_dsn != "" and settings.sentry_dsn is not None:
        sentry_sdk.init(settings.sentry_dsn, traces_sample_rate=1.0)

    schedule.every(1).minutes.do(parse, settings.api_url, settings.api_token)

    while True:
        schedule.run_pending()
        time.sleep(1)
