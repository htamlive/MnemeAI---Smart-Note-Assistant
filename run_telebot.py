from bot import Telebot
from client import DefaultClient
import logging



def main() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    client = DefaultClient()
    telebot = Telebot(client)
    telebot.run_polling()

if __name__ == '__main__':
    main()
