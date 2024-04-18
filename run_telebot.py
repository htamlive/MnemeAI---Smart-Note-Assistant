from bot import Telebot
from client import DefaultClient

def main() -> None:
    client = DefaultClient()
    telebot = Telebot(client)
    telebot.run_polling()

if __name__ == '__main__':
    main()
