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

class ViewNotesConversation(CommandConversation):
    def __init__(self, VIEW_NOTES: int, EDIT_TITLE: int, EDIT_DETAIL: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.VIEW_ITEMS = VIEW_NOTES
        self.EDIT_TITLE = EDIT_TITLE
        self.EDIT_DETAIL = EDIT_DETAIL

        self._states = [
            CallbackQueryHandler(self._preview_detail_callback, pattern=f'^{DETAIL_NOTE_CHAR}{PAGE_DELIMITER}'),
            ]

        self.previewing_pages: NotePages = self.init_reviewing_pages()

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


    async def response_modifying_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_content, note_idx) -> None:
        keyboard = self.get_option_keyboard(note_idx)

        if('prev_review_message' in context.user_data):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['prev_review_message'][0]
            )


        query = update.callback_query
        message = await query.message.reply_text(
            text=note_content,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

        context.user_data['prev_review_message'] = (message.message_id, message.text_html)

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_note_option_keyboard(note_idx)

    async def _handle_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, note_token: str | None = None) -> None:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        try:
            content = await self.client_get_content(chat_id, note_token)
        except Exception as e:
            content = str(e)
            await query.message.reply_text(content)
            return

        await self.response_modifying_options(update, context, content, note_token)

    async def _preview_detail_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query_data = update.callback_query.data
        token = query_data.split(PAGE_DELIMITER)[1]
        await self._handle_preview(update, context, token)




    def client_get_content(self, chat_id: int, idx: str | None) -> str:

        return self.client.get_note_content(chat_id, idx)



