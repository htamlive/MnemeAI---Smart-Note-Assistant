from telegram import (
    InlineKeyboardButton, Update, CallbackQuery, ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext
)
from .conversation import ConversationCenterController
from client import TelegramClient
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup


NOTE_TEXT, REMIND_TEXT = range(2)

class Telebot:
    def __init__(self, client: TelegramClient) -> None:
        from dotenv import load_dotenv
        import os

        load_dotenv()
        TELEBOT_TOKEN = os.getenv('TELEBOT_TOKEN')
        self.application = Application.builder().token(TELEBOT_TOKEN).build()
        self.client = client

        self.init_conversation_controller(client)
        self.init_start_command()
        self.init_notion_authorization_command()
        self.init_google_authorization_command()
        self.init_help_command()
        self.init_test_routine_notification()


    def init_test_routine_notification(self) -> None:

        async def daily_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            async def notify_assignees(context: CallbackContext) -> None:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello! This is a daily reminder to check your tasks for today.')
                print('sent message')

            await context.job_queue.run_repeating(notify_assignees, interval=5)

        self.application.add_handler(CommandHandler('test', daily_job))

    def init_conversation_controller(self, client: TelegramClient) -> None:
        self.conservation_controller = ConversationCenterController(client)
        self.conservation_controller.add_conversation_handler(self.application)


    def init_start_command(self) -> None:
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [['/help']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            welcome_text = open('templates/welcome.txt', 'r').read()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text= welcome_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
                )
            await self.client.user_subscribe(update.effective_chat.id)

            for job, interval in self.client.get_jobs_from_start(update):
                try:
                    await context.job_queue.run_repeating(job, interval)
                except TypeError as _:
                    continue

            # print chat_id
            print(f'Chat ID: {update.effective_chat.id}')

        self.application.add_handler(CommandHandler('start', start))


    def init_help_command(self) -> None:
        help_text = open('templates/help.txt', 'r').read()

        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [['/start']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                help_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
                )

        self.application.add_handler(CommandHandler('help', help_command))

    def init_notion_authorization_command(self) -> None:

        async def notion_authorization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

            url = self.client.get_notion_authorization_url(update.effective_chat.id)
            is_authorized = self.client.check_notion_authorization(update.effective_chat.id)

            reply_markup = None

            if(not is_authorized):
                text = f'Click the button to authorize with Notion'
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Authorize', url=url)]])
            else:
                text = 'You have already authorized the bot to access your Notion account.'



            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                # use button url
                reply_markup=reply_markup,
                parse_mode='HTML'
                )


        self.application.add_handler(CommandHandler('notion_authorization', notion_authorization))

    def init_google_authorization_command(self) -> None:

        async def google_authorization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

            url = await self.client.get_google_authorization_url(update.effective_chat.id)
            is_authorized = await self.client.check_google_authorization(update.effective_chat.id)

            reply_markup = None

            if(not is_authorized):
                text = f'Click the button to authorize with Google'
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Authorize', url=url)]])
            else:
                text = 'You have already authorized the bot to access your Google account.'



            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                # use button url
                reply_markup=reply_markup,
                parse_mode='HTML'
                )


        self.application.add_handler(CommandHandler('google_authorization', google_authorization))



    def run_polling(self) -> None:
        print('Bot is running...')
        self.application.run_polling()