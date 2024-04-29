from .._command_conversation import (
    CommandConversation
)
from telegram import (
    Update
)
from telegram.ext import (
    ContextTypes
)

class ModifyNoteConversation(CommandConversation):

    def __init__(self, debug=True) -> None:
        super().__init__(debug)

    async def on_finish_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        if('review_pages_message_id' in context.user_data):
            review_pages_message_id = context.user_data['review_pages_message_id']
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=review_pages_message_id,
                text="<i>Done viewing! View your latest version with</i> /view_notes <i>and</i> /view_reminders",
                parse_mode='HTML'
            )
            context.user_data.pop('review_pages_message_id')

        if('prev_review_message' in context.user_data):
            message_id, text_html = context.user_data['prev_review_message']

            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=f"<i>You have changed this content</i>",#"\n<blockquote>{text_html}</blockquote>",
                parse_mode='HTML'
            )
            context.user_data.pop('prev_review_message')

        query = update.callback_query
        await query.answer()

        await query.message.reply_text('Woohoo! Finished!')
