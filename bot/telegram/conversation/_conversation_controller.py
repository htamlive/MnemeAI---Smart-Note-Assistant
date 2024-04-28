from telegram import Update
from telegram.ext import (
    CommandHandler, ConversationHandler, MessageHandler, ContextTypes, CallbackQueryHandler
)
from telegram.ext import filters

from ._note_conversation import NoteConversation
from ._remind_conversation import RemindConversation
from ._view_notes_conversation import ViewNotesConversation
from ._edit_title_conversation import EditTileConversation
from ._edit_detail_conversation import EditDetailConversation

from client import Client

(
    NOTE_TEXT, REMIND_TEXT, 
    VIEW_NOTES,
    EDIT_TITLE, EDIT_DETAIL
    
    ) = range(5)


class ConversationController:
    def __init__(self, client: Client) -> None:
        self.client = client

        self.note_conversation = NoteConversation(NOTE_TEXT, self.client)
        self.remind_conversation = RemindConversation(REMIND_TEXT, self.client)
        self.view_notes_conversation = ViewNotesConversation(VIEW_NOTES, EDIT_TITLE, EDIT_DETAIL, self.client)
        self.edit_title_conversation = EditTileConversation(EDIT_TITLE, self.client)
        self.edit_detail_conversation = EditDetailConversation(EDIT_DETAIL, self.client)
        
        self.conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler('note', self.note_conversation.start_conservation),
                CommandHandler('remind', self.remind_conversation.start_conservation),
                CommandHandler('view_notes', self.view_notes_conversation.start_conservation),

                CallbackQueryHandler(self.edit_title_conversation.start_conservation, pattern='^editTitle@'),
                CallbackQueryHandler(self.edit_detail_conversation.start_conservation, pattern='^editDetail@'),
            ],
            states={
                NOTE_TEXT: [MessageHandler(filters.COMMAND, self.check_command)] + self.note_conversation.states,
                REMIND_TEXT: [MessageHandler(filters.COMMAND, self.check_command)] + self.remind_conversation.states,
                VIEW_NOTES: [
                    CallbackQueryHandler(self.edit_title_conversation.start_conservation, pattern='^editTitle@'),
                    CallbackQueryHandler(self.edit_detail_conversation.start_conservation, pattern='^editDetail@'),
                ] + self.view_notes_conversation.states,
                EDIT_TITLE: self.edit_title_conversation.states + self.view_notes_conversation.states,
                EDIT_DETAIL: self.edit_detail_conversation.states + self.view_notes_conversation.states,
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
            return await self.note_conversation.start_conservation(update, context)
        elif command.startswith('/remind'):
            return await self.remind_conversation.start_conservation(update, context)
        elif command.startswith('/view_notes'):
            return await self.view_notes_conversation.start_conservation(update, context)
        
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Operation canceled.")
        return ConversationHandler.END