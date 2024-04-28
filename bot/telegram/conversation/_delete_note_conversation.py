from telegram import (
    Update, CallbackQuery
)
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
)

from telegram import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
from ._edit_note_conversation import EditNoteConversation

from client import Client


class DeleteNoteConversation(EditNoteConversation):
    def __init__(self, DELETE_NOTE: int, VIEW_NOTES, client: Client, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.DELETE_NOTE = DELETE_NOTE
        self.VIEW_NOTES = VIEW_NOTES
        self._states = [CallbackQueryHandler(self.handle_confirmation)]
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()

        note_idx = query.data.split('@')[1]
        keyboard = [
                [InlineKeyboardButton("Yes, delete it", callback_data=f'confirm_delete_note@{note_idx}')],
                [InlineKeyboardButton("No, go back", callback_data=f'cancel_delete_note@{note_idx}')]
            ]
        await query.edit_message_text(text="Are you really sure you want to delete?", reply_markup=InlineKeyboardMarkup(keyboard))

        return self.DELETE_NOTE
        
    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query: CallbackQuery = update.callback_query
        await query.answer()

        

        if query.data.startswith('confirm_delete_note@'):
            chat_id = query.message.chat_id

            note_idx = query.data.split('@')[1]
            await self.client.delete_note(chat_id, note_idx)
            await self.on_finish_edit(update, context)

            return ConversationHandler.END
        elif query.data.startswith('cancel_delete_note@'):
            note_idx = query.data.split('@')[1]
            await self.restore_note_content(query, note_idx)

            return self.VIEW_NOTES
    
    async def restore_note_content(self, query: CallbackQuery, note_idx: str) -> None:
        chat_id = query.message.chat_id
        note_content = self.client.get_note_content(chat_id, note_idx)
        keyboard = self.get_modifying_option_keyboard(note_idx)
        await query.edit_message_text(
            text=note_content,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )


    def get_modifying_option_keyboard(self, note_idx: str) -> list:
        keyboard = [
            [
                InlineKeyboardButton('Edit Title', callback_data=f'edit_note_title@{note_idx}'),
                InlineKeyboardButton('Edit Detail', callback_data=f'edit_note_detail@{note_idx}'),
                InlineKeyboardButton('Delete', callback_data=f'delete_note@{note_idx}')
            ],
            [InlineKeyboardButton('Back', callback_data='back')]
        ]
        return keyboard
        