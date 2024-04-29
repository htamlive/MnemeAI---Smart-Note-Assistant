from telegram import Update
from telegram.ext import (
    CommandHandler, ConversationHandler, MessageHandler, ContextTypes, CallbackQueryHandler
)
from telegram.ext import filters

from ._note_conversation import NoteConversation
from ._remind_conversation import RemindConversation

from ._view_notes_conversation import ViewNotesConversation
from .modify_note_conversation import EditNoteTitleConversation
from .modify_note_conversation import DeleteNoteConversation
from .modify_note_conversation import EditNoteDetailConversation

from ._view_reminders_conversation import ViewRemindersConversation
from .modify_reminder_conversation import EditReminderDetailConversation
from .modify_reminder_conversation import EditReminderTitleConversation
from .modify_reminder_conversation import DeleteReminderConversation
from .modify_reminder_conversation import EditReminderTimeConversation

from ._prompting_conversation import PromptingConversation

from client import Client

from config import *


class ConversationController:
    def __init__(self, client: Client) -> None:
        self.client = client

        self.note_conversation = NoteConversation(NOTE_TEXT, self.client)
        self.remind_conversation = RemindConversation(REMIND_TEXT, self.client)

        self.init_note_conversation()
        self.init_reminder_conversation()

        self.prompting_conversation = PromptingConversation(PROMPTING, self.client)
        
        self.conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler('note', self.note_conversation.start_conversation),
                CommandHandler('remind', self.remind_conversation.start_conversation),
                CommandHandler('view_notes', self.view_notes_conversation.start_conversation),

                CommandHandler('ah', self.prompting_conversation.start_conversation),

                CallbackQueryHandler(self.edit_title_conversation.start_conversation, pattern='^edit_note_title@'),
                CallbackQueryHandler(self.edit_detail_conversation.start_conversation, pattern='^edit_note_detail@'),
                CallbackQueryHandler(self.delete_note_conversation.start_conversation, pattern='^delete_note@'),

                CommandHandler('view_reminders', self.view_reminders_conversation.start_conversation),
                CallbackQueryHandler(self.edit_reminder_title_conversation.start_conversation, pattern='^edit_reminder_title@'),
                CallbackQueryHandler(self.edit_reminder_detail_conversation.start_conversation, pattern='^edit_reminder_detail@'),
                CallbackQueryHandler(self.delete_reminder_conversation.start_conversation, pattern='^delete_reminder@'),
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
            

                VIEW_REMINDERS: [
                    MessageHandler(filters.COMMAND, self.check_command),
                    CallbackQueryHandler(self.edit_reminder_title_conversation.start_conversation, pattern='^edit_reminder_title@'),
                    CallbackQueryHandler(self.edit_reminder_detail_conversation.start_conversation, pattern='^edit_reminder_detail@'),
                    CallbackQueryHandler(self.delete_reminder_conversation.start_conversation, pattern='^delete_reminder@'),
                    CallbackQueryHandler(self.edit_reminder_time_conversation.start_conversation, pattern='^edit_reminder_time@'),
                ] + self.view_reminders_conversation.states,
                EDIT_REMINDER_TITLE:
                    [MessageHandler(filters.COMMAND, self.check_command)] + self.edit_reminder_title_conversation.states + self.view_reminders_conversation.states,
                EDIT_REMINDER_DETAIL:
                    [MessageHandler(filters.COMMAND, self.check_command)] + self.edit_reminder_detail_conversation.states + self.view_reminders_conversation.states,
                DELETE_REMINDER:
                    [MessageHandler(filters.COMMAND, self.check_command)] + self.delete_reminder_conversation.states + self.view_reminders_conversation.states,
                EDIT_REMINDER_TIME:
                    [MessageHandler(filters.COMMAND, self.check_command)] + self.view_reminders_conversation.states,            
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel)
            ]
        )

        
    def init_note_conversation(self) -> None:
        self.view_notes_conversation = ViewNotesConversation(VIEW_NOTES, EDIT_NOTE_TITLE, EDIT_NOTE_DETAIL, self.client)
        self.edit_title_conversation = EditNoteTitleConversation(EDIT_NOTE_TITLE, self.client)
        self.edit_detail_conversation = EditNoteDetailConversation(EDIT_NOTE_DETAIL, self.client)
        self.delete_note_conversation = DeleteNoteConversation(DELETE_NOTE, VIEW_NOTES, self.client)

    def init_reminder_conversation(self) -> None:
        self.view_reminders_conversation = ViewRemindersConversation(VIEW_REMINDERS, EDIT_REMINDER_TITLE, EDIT_REMINDER_DETAIL, self.client)
        self.edit_reminder_title_conversation = EditReminderTitleConversation(EDIT_REMINDER_TITLE, self.client)
        self.edit_reminder_detail_conversation = EditReminderDetailConversation(EDIT_REMINDER_DETAIL, self.client)
        self.edit_reminder_time_conversation = EditReminderTimeConversation(EDIT_REMINDER_TIME, self.client)
        self.delete_reminder_conversation = DeleteReminderConversation(DELETE_REMINDER, VIEW_REMINDERS, self.client)
        
    
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