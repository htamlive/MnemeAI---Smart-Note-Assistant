from ..._command_conversation import (
    CommandConversation
)
from telegram import (
    InlineKeyboardButton,
    Update
)
from telegram.ext import (
    ContextTypes
)

from telegram import InlineKeyboardMarkup

class ModifyNoteConversation(CommandConversation):

    def __init__(self, debug=True) -> None:
        super().__init__(debug)

    async def on_finish_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        if('review_pages_message_id' in context.user_data):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['review_pages_message_id']
            )
            context.user_data.pop('review_pages_message_id')


        if('prev_review_message' in context.user_data):
            message_id = context.user_data['prev_review_message']['message_id']
            # text_html = context.user_data['prev_review_message']['text_html']

            # print(text_html)
            # delete the previous message
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=message_id
            )

            # edit previous message
            # await context.bot.edit_message_text(
            #     chat_id=update.effective_chat.id,
            #     message_id=message_id,
            #     text="Edited!",
            #     # delete reply_markup
            #     reply_markup=None,
            #     parse_mode='HTML'
            # )
            context.user_data.pop('prev_review_message')


        await update.message.reply_text(
            'Woohoo! Finished!\n\n<i>View your latest version with</i> /view_notes <i>and</i> /view_reminders',
            parse_mode='HTML'
            )
