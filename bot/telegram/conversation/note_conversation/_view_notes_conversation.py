from .._command_conversation import CommandConversation
from telegram import (
    Update, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, CallbackQueryHandler
)

from config import PAGE_DELIMITER, DETAIL_NOTE_CHAR, NOTE_PAGE_CHAR
from ...telegram_pages import NotePages
from client import TelegramClient

from bot.telegram.ui_templates import get_note_option_keyboard
import base64

class ViewNotesConversation(CommandConversation):
    def __init__(self, VIEW_NOTES: int, EDIT_TITLE: int, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.VIEW_ITEMS = VIEW_NOTES
        self.EDIT_TITLE = EDIT_TITLE
        self.EDIT_DETAIL = EDIT_DETAIL
        self.previewing_pages: NotePages = self.init_reviewing_pages()

        self._states = [
            CallbackQueryHandler(self._preview_detail_callback, pattern=f'^{DETAIL_NOTE_CHAR}{PAGE_DELIMITER}'),
            CallbackQueryHandler(self.previewing_pages._preview_page_callback, pattern=f'^{NOTE_PAGE_CHAR}{PAGE_DELIMITER}')
            ]


    def add_preview_pages_callback(self, application) -> None:
        application.add_handler(CallbackQueryHandler(self.previewing_pages.preview_page_callback, pattern=f'^{NOTE_PAGE_CHAR}{PAGE_DELIMITER}'))

    def share_preview_page_callback(self) -> CallbackQueryHandler:
        # print(f'^{NOTE_PAGE_CHAR}#')
        return CallbackQueryHandler(self.previewing_pages.preview_page_callback, pattern=f'^{NOTE_PAGE_CHAR}{PAGE_DELIMITER}')

    def init_reviewing_pages(self) -> NotePages:
        return NotePages(self.client)

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        await self.previewing_pages.view_note_page_command(update, context)

        await update.message.reply_text("Please send me the note index.")

        return self.VIEW_ITEMS
    
    async def view_note_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()


    async def receive_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        received_text = update.message.text
        await self.handle_preview(update, context, received_text)
        return self.VIEW_ITEMS
        # return ConversationHandler.END


    async def _response_modifying_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_content, token) -> None:
        keyboard = self.get_option_keyboard(token)

        if('prev_review_message' in context.user_data):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['prev_review_message']['message_id']
            )


        query = update.callback_query
        message = await query.message.reply_text(
            text=note_content,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

        self.update_review_message_tracker(context, message.message_id, note_content, token)

    def update_review_message_tracker(self, context, message_id, text_html, token) -> None:
        context.user_data['prev_review_message'] = {
            'message_id': message_id,
            'text_html': text_html,
            'note_token': token
        }

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_note_option_keyboard(note_idx)

    async def _handle_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, token: str | None = None) -> None:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        try:
            content = await self.client_get_content(chat_id, token)
        except Exception as e:
            content = str(e)
            await query.message.reply_text(content)
            return

        await self._response_modifying_options(update, context, content, token)

    async def _preview_detail_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query_data = update.callback_query.data
        token = query_data.split(PAGE_DELIMITER)[1]

        message = update.callback_query.message

        for entity in message.entities:
            if(entity.type == 'text_link'):
                url = entity.url
                if(url.startswith('tg://btn/')):
                    encoded_data = url.split('tg://btn/')[1]

                    raw_data = base64.urlsafe_b64decode(encoded_data.encode()).split(b'\0')

                    token = raw_data[int(token)].decode()

                    await self._handle_preview(update, context, token)
                    return

        await message.reply_text('Cannot find the reminder, please use /view_reminders to view the latest reminders.')

    def client_get_content(self, chat_id: int, idx: str | None) -> str:
        # may need to change
        return self.client.get_note_content(chat_id, idx)



