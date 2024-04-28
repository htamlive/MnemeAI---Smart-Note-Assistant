from telegram.ext import ConversationHandler
(
    NOTE_TEXT, REMIND_TEXT, 
    VIEW_NOTES,
    EDIT_NOTE_TITLE, EDIT_NOTE_DETAIL, DELETE_NOTE,
    PROMPTING,
    ) = range(7)

END = ConversationHandler.END