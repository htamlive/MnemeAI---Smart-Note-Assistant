from bot import Telebot
from client import DefaultClient
import logging



def main() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info('Starting telebot')


    client = DefaultClient()
    telebot = Telebot(client)
    telebot.run_polling()

if __name__ == '__main__':
    main()