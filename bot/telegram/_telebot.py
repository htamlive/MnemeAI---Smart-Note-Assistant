from telegram import (
    InlineKeyboardButton, Update, CallbackQuery, ReplyKeyboardMarkup    
)
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext
)
from .conversation import ConversationController
from .telegram_pages import NotePages
from client import Client
from telegram_bot_pagination import InlineKeyboardPaginator

NOTE_TEXT, REMIND_TEXT = range(2)

class Telebot:
    def __init__(self, client: Client) -> None:
        from dotenv import load_dotenv
        import os

        load_dotenv()
        TELEBOT_TOKEN = os.getenv('TELEBOT_TOKEN')
        self.application = Application.builder().token(TELEBOT_TOKEN).build()
        self.client = client

        self.init_conversation_controller(client)
        self.init_start_command()
        self.init_help_command()
        self.init_test_routine_notification()
        self.init_pagination()



    def init_test_routine_notification(self) -> None:

        async def daily_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            async def notify_assignees(context: CallbackContext) -> None:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello! This is a daily reminder to check your tasks for today.')
                print('sent message')

            await context.job_queue.run_repeating(notify_assignees, interval=5)

        self.application.add_handler(CommandHandler('test', daily_job))

    def init_conversation_controller(self, client: Client) -> None:
        self.conservation_controller = ConversationController(client)
        self.conservation_controller.add_conversation_handler(self.application)


    def init_start_command(self) -> None:
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [['/help']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to the bot! Type /help to see available commands.', reply_markup=reply_markup)
            await self.client.user_subscribe(update.effective_chat.id)
            
            for job, interval in self.client.get_jobs_from_start(update):
                try:
                    await context.job_queue.run_repeating(job, interval)
                except TypeError as _:
                    continue

        self.application.add_handler(CommandHandler('start', start))

    def init_pagination(self) -> None:
        self.note_pages = NotePages(self.client)

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