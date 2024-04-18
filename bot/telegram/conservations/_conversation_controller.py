from telegram import Update
from telegram.ext import (
    CommandHandler, ConversationHandler, MessageHandler, ContextTypes
)
from telegram.ext import filters

from ._note_conversation import NoteConversation
from ._remind_conversation import RemindConversation

NOTE_TEXT, REMIND_TEXT = range(2)


class ConservationController:
    def __init__(self) -> None:

        self.note_conversation = NoteConversation(NOTE_TEXT)
        self.remind_conversation = RemindConversation(REMIND_TEXT)
        
        self.conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler('note', self.note_conversation.start_conservation),
                CommandHandler('remind', self.remind_conversation.start_conservation)
            ],
            states={
                NOTE_TEXT: [MessageHandler(filters.COMMAND, self.check_command)] + self.note_conversation.states,
                REMIND_TEXT: [MessageHandler(filters.COMMAND, self.check_command)] + self.remind_conversation.states
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
            await self.note_conversation.start_conservation(update, context)
        elif command.startswith('/remind'):
            await self.remind_conversation.start_conservation(update, context)
        else:
            await update.message.reply_text("Unknown command. Try /help.")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Operation canceled.")
        return ConversationHandler.END