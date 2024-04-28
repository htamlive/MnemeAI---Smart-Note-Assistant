from telegram import Update
from telegram.ext import (
    CommandHandler, ConversationHandler, MessageHandler, ContextTypes, CallbackQueryHandler
)
from telegram.ext import filters

from ._note_conversation import NoteConversation
from ._remind_conversation import RemindConversation
from ._view_notes_conversation import ViewNotesConversation

from .modify_note_conversation import EditTitleConversation
from .modify_note_conversation import DeleteNoteConversation
from .modify_note_conversation import EditDetailConversation

from ._prompting_conversation import PromptingConversation

from client import Client

from config import *


class ConversationController:
    def __init__(self, client: Client) -> None:
        self.client = client

        self.note_conversation = NoteConversation(NOTE_TEXT, self.client)
        self.remind_conversation = RemindConversation(REMIND_TEXT, self.client)
        self.view_notes_conversation = ViewNotesConversation(VIEW_NOTES, EDIT_NOTE_TITLE, EDIT_NOTE_DETAIL, self.client)
        self.edit_title_conversation = EditTitleConversation(EDIT_NOTE_TITLE, self.client)
        self.edit_detail_conversation = EditDetailConversation(EDIT_NOTE_DETAIL, self.client)
        self.prompting_conversation = PromptingConversation(PROMPTING, self.client)
        self.delete_note_conversation = DeleteNoteConversation(DELETE_NOTE, VIEW_NOTES, self.client)
        
        self.conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler('note', self.note_conversation.start_conversation),
                CommandHandler('remind', self.remind_conversation.start_conversation),
                CommandHandler('view_notes', self.view_notes_conversation.start_conversation),
                
                CommandHandler('ah', self.prompting_conversation.start_conversation),

                CallbackQueryHandler(self.edit_title_conversation.start_conversation, pattern='^edit_note_title@'),
                CallbackQueryHandler(self.edit_detail_conversation.start_conversation, pattern='^edit_note_detail@'),
                CallbackQueryHandler(self.delete_note_conversation.start_conversation, pattern='^delete_note@'),
            ],
            states={
                NOTE_TEXT: [MessageHandler(filters.COMMAND, self.check_command)] + self.note_conversation.states,
                REMIND_TEXT: [MessageHandler(filters.COMMAND, self.check_command)] + self.remind_conversation.states,
                VIEW_NOTES: [
                    MessageHandler(filters.COMMAND, self.check_command),
                    CallbackQueryHandler(self.edit_title_conversation.start_conversation, pattern='^edit_note_title@'),
                    CallbackQueryHandler(self.edit_detail_conversation.start_conversation, pattern='^edit_note_detail@'),
                    CallbackQueryHandler(self.delete_note_conversation.start_conversation, pattern='^delete_note@'),
                ] + self.view_notes_conversation.states,
                EDIT_NOTE_TITLE: 
                    [MessageHandler(filters.COMMAND, self.check_command)] + self.edit_title_conversation.states + self.view_notes_conversation.states,
                EDIT_NOTE_DETAIL:
                    [MessageHandler(filters.COMMAND, self.check_command)] + self.edit_detail_conversation.states + self.view_notes_conversation.states,
                DELETE_NOTE:
                    [MessageHandler(filters.COMMAND, self.check_command)] + self.delete_note_conversation.states + self.view_notes_conversation.states,
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel)
            ]
        )

        
        
    
    def add_conversation_handler(self, application) -> None:
        application.add_handler(self.conversation_handler)

    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        command = update.message.text
        if command.startswith('/note'):
            return await self.note_conversation.start_conversation(update, context)
        elif command.startswith('/remind'):
            return await self.remind_conversation.start_conversation(update, context)
        elif command.startswith('/view_notes'):
            return await self.view_notes_conversation.start_conversation(update, context)
        elif command.startswith('/ah'):
            return await self.prompting_conversation.start_conversation(update, context)
        
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Operation canceled.")
        return ConversationHandler.END