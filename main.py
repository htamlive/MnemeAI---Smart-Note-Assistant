from bot import Telebot

def main() -> None:
    telebot = Telebot()
    telebot.run_polling()

if __name__ == '__main__':
    main()
