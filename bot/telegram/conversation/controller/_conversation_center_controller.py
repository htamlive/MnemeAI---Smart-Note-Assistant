from telegram import Update
from telegram.ext import (
    CommandHandler, ConversationHandler, MessageHandler, ContextTypes, CallbackQueryHandler
)
from telegram.ext import filters

from ._note_conversation_controller import NoteConversationController
from ._reminder_conversation_controller import ReminderConversationController
from ..notion_request.request_notion_db_conversation import RequestNotionDBConversation
from ..notion_request.request_page_conversation import RequestNotionPageConversation

from .._prompting_conversation import PromptingConversation

from client import TelegramClient

from config import *


class ConversationCenterController:
    def __init__(self, client: TelegramClient) -> None:
        self.client = client

        self.reminder_conversation_controller = ReminderConversationController(self.client)
        self.note_conversation_controller = NoteConversationController(self.client)
        self.notion_db_request_conversation = RequestNotionDBConversation(NOTION_REQ_DB, self.client)
        self.notion_page_request_conversation = RequestNotionPageConversation(NOTION_REQ_PAGE, self.client)
        

        self.prompting_conversation = PromptingConversation(PROMPTING, self.client)

        # self.init_preview_page_callbacks()

        command_handler = MessageHandler(filters.COMMAND, self.check_command)
        
        self.conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler(Commands.PROMPTING.value, self.prompting_conversation.start_conversation),
                CommandHandler(Commands.NOTION_REQ_DB.value, self.notion_db_request_conversation.start_conversation),
                CommandHandler(Commands.NOTION_REQ_PAGE.value, self.notion_page_request_conversation.start_conversation)
            ] + self.note_conversation_controller.get_entry_points() + self.reminder_conversation_controller.get_entry_points(),
            states = {
                NOTION_REQ_DB: [command_handler] + self.notion_db_request_conversation.states,
                NOTION_REQ_PAGE: [command_handler] + self.notion_page_request_conversation.states

            } | self.note_conversation_controller.get_states_dict(command_handler) | self.reminder_conversation_controller.get_states_dict(command_handler),
            fallbacks=[
                CommandHandler('cancel', self.cancel)
            ]
        )


    def add_conversation_handler(self, application) -> None:
        application.add_handler(self.conversation_handler)
        self.reminder_conversation_controller.share_preview_page_callback(application)
        self.note_conversation_controller.share_preview_page_callback(application)


    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        command = update.message.text
        if command.startswith('/'+Commands.NOTE.value):
            return await self.note_conversation_controller.factory[NOTE_TEXT].start_conversation(update, context)
        
        if command.startswith('/'+Commands.VIEW_NOTES.value):
            return await self.note_conversation_controller.factory[VIEW_NOTES].start_conversation(update, context)
        
        if command.startswith('/'+Commands.REMINDER.value):
            return await self.reminder_conversation_controller.factory[REMIND_TEXT].start_conversation(update, context)
        
        if command.startswith('/'+Commands.VIEW_REMINDERS.value):
            return await self.reminder_conversation_controller.factory[VIEW_REMINDERS].start_conversation(update, context) 
        
        if command.startswith('/'+Commands.PROMPTING.value):
            return await self.prompting_conversation.start_conversation(update, context)
        
        if command.startswith('/'+Commands.NOTION_REQ_DB.value):
            return await self.notion_db_request_conversation.start_conversation(update, context)
        
        if command.startswith('/'+Commands.NOTION_REQ_PAGE.value):
            return await self.notion_page_request_conversation.start_conversation(update, context)
        
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Operation canceled.")
        return ConversationHandler.END