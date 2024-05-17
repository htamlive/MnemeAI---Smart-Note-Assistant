import base64
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
from bot.telegram.utils import extract_hidden_url_data, get_hidden_url_html

from bot.telegram.ui_templates import get_note_option_keyboard

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

        return self.VIEW_ITEMS
    
    async def view_note_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

    async def receive_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        received_text = update.message.text
        await self.handle_preview(update, context, received_text)
        return self.VIEW_ITEMS
        # return ConversationHandler.END


    async def _response_modifying_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, token) -> None:

        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id

        if('prev_review_message' in context.user_data):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['prev_review_message']['message_id']
            )
        try:
            message = update.callback_query.message

            note_token = None
            url = None

            for entity in message.entities:
                if(entity.type == 'text_link'):
                    url = entity.url
                    if(url.startswith('tg://btn/')):

                        note_tokens = extract_hidden_url_data(url)
                        note_token = note_tokens[int(token)]

                        break

            if(not note_token):
                raise Exception('No text link found')

            hidden_url_html = get_hidden_url_html([note_token])
            note_content = hidden_url_html + await self.client_get_content(chat_id, note_token)

            keyboard = self.get_option_keyboard(0)

            query = update.callback_query
            message = await query.message.reply_text(
                text=note_content,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )


        except Exception as e:
            print(e)
            message = await query.message.reply_text("Cannot view this note. Please view the latest version with /view_notes")
        
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
        await self._response_modifying_options(update, context, token)

    async def _preview_detail_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query_data = update.callback_query.data
        token = query_data.split(PAGE_DELIMITER)[1]
        await self._handle_preview(update, context, token)

    async def client_get_content(self, chat_id: int, token: str | None) -> str:
        return await self.client.get_note_content(chat_id, token)



