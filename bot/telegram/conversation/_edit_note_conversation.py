from ._command_conversation import (
    CommandConversation
)
from telegram import (
    Update
)
from telegram.ext import (
    ContextTypes
)

class EditNoteConversation(CommandConversation):

    async def on_finish_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        if('note_pages_message_id' in context.user_data):
            note_pages_message_id = context.user_data['note_pages_message_id']
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=note_pages_message_id,
                text="Done viewing note!"
            )
            context.user_data.pop('note_pages_message_id')

        if('prev_review_note_message_id' in context.user_data):
            prev_review_note_message = context.user_data['prev_review_note_message_id']
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=prev_review_note_message,
                text="Note has been updated!"
            )
            context.user_data.pop('prev_review_note_message_id')