from telegram import (
    InlineKeyboardButton, KeyboardButton, Update, CallbackQuery, ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext
)

from bot.telegram.utils import check_data_requirement
from llm.models import UserData
from .conversation import ConversationCenterController
from client import TelegramClient
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup
from datetime import datetime

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
        self.init_show_time_command()
        self.init_revoke_google_auth()
        self.init_revoke_notion_auth()


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
            keyboard = [['/timezone'], ['/notion_authorization'], ['/google_authorization'], ['/show_time'], ['/help']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            if(not context.user_data.get('user_system_data', None)):
                context.user_data['user_system_data'] = UserData(chat_id=update.effective_chat.id)


            welcome_text = open('templates/welcome.txt', 'r', encoding='utf-8').read()
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
        help_text = open('templates/help.txt', 'r', encoding='utf-8').read()

        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            keyboard = [['/start']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                help_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
                )

        self.application.add_handler(CommandHandler('help', help_command))

    def init_show_time_command(self) -> None:
        async def show_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            
            sucess, message = check_data_requirement(context, check_timezone=True)

            if(not sucess):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message
                )
                return
            
            user_data : UserData = context.user_data['user_system_data']
            timezone = user_data.timezone

            await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'The current time is {datetime.now(timezone).strftime("%H:%M")}'
                )
        self.application.add_handler(CommandHandler('show_time', show_time))

    def init_notion_authorization_command(self) -> None:

        async def notion_authorization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

            url = await self.client.get_notion_authorization_url(update.effective_chat.id)
            is_authorized = await self.client.check_notion_authorization(update.effective_chat.id)

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

    def init_notion_register_page(self) -> None:
        async def notion_register_page_normal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Please enter your database URL or database ID'
            )

        async def notion_register_page_advance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Please enter your database URL or database ID'
            )

        self.application.add_handler(CommandHandler('normal_notion_register', notion_register_page_normal))
        self.application.add_handler(CommandHandler('advance_notion_register', notion_register_page_advance))

    def init_revoke_google_auth(self) -> None:
        async def revoke_google_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            message_text = await self.client.revoke_google_authorization(update.effective_chat.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_text,
            )

        self.application.add_handler(CommandHandler('revoke_google_auth', revoke_google_auth))

    def init_revoke_notion_auth(self) -> None:
        async def revoke_notion_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            message_text = await self.client.revoke_notion_authorization(update.effective_chat.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_text,
            )

        self.application.add_handler(CommandHandler('revoke_notion_auth', revoke_notion_auth))


    def init_google_authorization_command(self) -> None:

        async def google_authorization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            
            force = False
            if(context.args):
                if(context.args[0] == 'force'):
                    force = True

            # url = await self.client.get_google_authorization_url(update.effective_chat.id)
            is_authorized = await self.client.check_google_authorization(update.effective_chat.id)

            reply_markup = None

            if(not is_authorized or force):
                text = f'Click the button to authorize with Google'
                url = await self.client.get_google_authorization_url(update.effective_chat.id)
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