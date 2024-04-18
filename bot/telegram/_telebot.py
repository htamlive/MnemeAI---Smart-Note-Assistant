from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler
)
from telegram.ext import filters
from .conservations import ConservationController
from client import DefaultClient

NOTE_TEXT, REMIND_TEXT = range(2)

class Telebot:
    def __init__(self, client: DefaultClient) -> None:
        from dotenv import load_dotenv
        import os

        load_dotenv()
        TELEBOT_TOKEN = os.getenv('TELEBOT_TOKEN')
        self.application = Application.builder().token(TELEBOT_TOKEN).build()

        self.init_conversation_controller(client)
        self.init_start_command()
        self.init_help_command()

    def init_conversation_controller(self, client: DefaultClient) -> None:
        self.conservation_controller = ConservationController(client)
        self.conservation_controller.add_conversation_handler(self.application)


    def init_start_command(self) -> None:
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [['/help']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text('Welcome to the bot! Type /help to see available commands.', reply_markup=reply_markup)

        self.application.add_handler(CommandHandler('start', start))

    def init_help_command(self) -> None:
        help_text = open('templates/help.txt', 'r').read()

        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [['/start']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(help_text, reply_markup=reply_markup)

        self.application.add_handler(CommandHandler('help', help_command))



    def run_polling(self) -> None:
        print('Bot is running...')
        self.application.run_polling()