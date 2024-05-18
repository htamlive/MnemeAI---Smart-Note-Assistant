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
from .._timezone_request_conversation import TimezoneRequestConversation
from .._query_knowledge_conversation import QueryKnowledgeConversation

from client import TelegramClient

from config import *
import re


class ConversationCenterController:
    def __init__(self, client: TelegramClient) -> None:
        self.client = client

        self.reminder_conversation_controller = ReminderConversationController(self.client)
        self.note_conversation_controller = NoteConversationController(self.client)
        self.notion_db_request_conversation = RequestNotionDBConversation(NOTION_REQ_DB, self.client)
        self.notion_page_request_conversation = RequestNotionPageConversation(NOTION_REQ_PAGE, self.client)
        
        self.query_knowledge_conversation = QueryKnowledgeConversation(QUERY_KNOWLEDGE, self.client)

        self.prompting_conversation = PromptingConversation(PROMPTING, self.client)

        self.timezone_request_conversation = TimezoneRequestConversation(TIMEZONE_REQ, self.client)
        # self.init_preview_page_callbacks()

        command_handler = MessageHandler(filters.COMMAND, self.check_command)
        
        self.conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler(Commands.PROMPTING.value, self.prompting_conversation.start_conversation),
                CommandHandler(Commands.TIMEZONE_REQ.value, self.timezone_request_conversation.start_conversation),
                # CommandHandler(Commands.NOTION_REQ_DB.value, self.notion_db_request_conversation.start_conversation),
                CommandHandler(Commands.NOTION_REQ_PAGE.value, self.notion_page_request_conversation.start_conversation),
                CommandHandler(Commands.QUERY_KNOWLEDGE.value, self.query_knowledge_conversation.start_conversation),
            ] + self.note_conversation_controller.get_entry_points() + self.reminder_conversation_controller.get_entry_points(),
            states = {
                # NOTION_REQ_DB: [command_handler] + self.notion_db_request_conversation.states,
                NOTION_REQ_PAGE: [command_handler] + self.notion_page_request_conversation.states,
                TIMEZONE_REQ: [command_handler] + self.timezone_request_conversation.states,
                QUERY_KNOWLEDGE: [command_handler] + self.query_knowledge_conversation.states

            } | self.note_conversation_controller.get_states_dict(command_handler)
              | self.reminder_conversation_controller.get_states_dict(command_handler),
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

        print(command)
        if command.startswith('/'+Commands.NOTE.value):
            context.args = re.split(r'\s+', command)[1:]
            return await self.note_conversation_controller.factory[NOTE_TEXT].start_conversation(update, context)
        
        if command.startswith('/'+Commands.VIEW_NOTES.value):
            return await self.note_conversation_controller.factory[VIEW_NOTES].start_conversation(update, context)
        
        if command.startswith('/'+Commands.REMINDER.value):
            context.args = re.split(r'\s+', command)[1:]
            return await self.reminder_conversation_controller.factory[REMIND_TEXT].start_conversation(update, context)
        
        if command.startswith('/'+Commands.VIEW_REMINDERS.value):
            return await self.reminder_conversation_controller.factory[VIEW_REMINDERS].start_conversation(update, context) 
        
        if command.startswith('/'+Commands.PROMPTING.value):
            # get the args after the command /ah
            context.args = re.split(r'\s+', command)[1:]

            return await self.prompting_conversation.start_conversation(update, context)
        
        if command.startswith('/'+Commands.TIMEZONE_REQ.value):
            return await self.timezone_request_conversation.start_conversation(update, context)
        
        # if command.startswith('/'+Commands.NOTION_REQ_DB.value):
        #     return await self.notion_db_request_conversation.start_conversation(update, context)
        
        if command.startswith('/'+Commands.NOTION_REQ_PAGE.value):
            return await self.notion_page_request_conversation.start_conversation(update, context)
        
        
        if command.startswith('/'+Commands.QUERY_KNOWLEDGE.value):
            context.args = re.split(r'\s+', command)[1:]
            return await self.query_knowledge_conversation.start_conversation(update, context)
        
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Operation canceled.")
        return ConversationHandler.END