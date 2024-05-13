from ._conversation_controller import ConversationController
from telegram.ext import (
    CallbackQueryHandler, CommandHandler
)
from config import Patterns, EDIT_NOTE_DETAIL, EDIT_NOTE_TITLE, DELETE_NOTE, VIEW_NOTES, NOTE_TEXT, Commands, NOTE_PAGE_CHAR
from ..note_conversation.modify_note_conversation import EditNoteTitleConversation, EditNoteDetailConversation, DeleteNoteConversation, ModifyNoteConversation
from ..note_conversation._view_notes_conversation import ViewNotesConversation
from ..note_conversation._note_conversation import NoteConversation

class NoteConversationController(ConversationController):
    
    def __init__(self, client) -> None:
        super().__init__(client)



        self.factory: dict[int, ModifyNoteConversation] = {}
        self.factory[EDIT_NOTE_DETAIL] = EditNoteDetailConversation(EDIT_DETAIL=EDIT_NOTE_DETAIL, client=client)
        self.factory[EDIT_NOTE_TITLE] = EditNoteTitleConversation(EDIT_TITLE=EDIT_NOTE_TITLE, client=client)
        self.factory[DELETE_NOTE] = DeleteNoteConversation(DELETE_NOTE=DELETE_NOTE, VIEW_NOTES=VIEW_NOTES, client=client)
        self.factory[VIEW_NOTES] = ViewNotesConversation(VIEW_NOTES, EDIT_NOTE_TITLE, EDIT_NOTE_DETAIL, self.client)
        self.factory[NOTE_TEXT] = NoteConversation(NOTE_TEXT, client)

    def get_callbacks(self) -> list[CallbackQueryHandler]:
        return [
            CallbackQueryHandler(self.factory[EDIT_NOTE_TITLE].start_conversation, pattern=f'^{Patterns.EDIT_NOTE_TITLE.value}'),
            CallbackQueryHandler(self.factory[EDIT_NOTE_DETAIL].start_conversation, pattern=f'^{Patterns.EDIT_NOTE_DETAIL.value}'),
            CallbackQueryHandler(self.factory[DELETE_NOTE].start_conversation, pattern=f'^{Patterns.DELETE_NOTE.value}'),
        ]
    
    def get_entry_points(self) -> list[CommandHandler]:
        return [
            CommandHandler(Commands.NOTE.value, self.factory[NOTE_TEXT].start_conversation),
            CommandHandler(Commands.VIEW_NOTES.value, self.factory[VIEW_NOTES].start_conversation),
        ] + self.get_callbacks() + self.factory[VIEW_NOTES].states
    

    def get_states_dict(self, command_handler) -> dict:
        return {
            NOTE_TEXT: [command_handler] + self.factory[NOTE_TEXT].states,
            VIEW_NOTES: [command_handler] + self.get_callbacks() + self.factory[VIEW_NOTES].states,
            EDIT_NOTE_TITLE: 
                    [command_handler]
                    + self.get_callbacks()
                    + self.factory[EDIT_NOTE_TITLE].states
                    + self.factory[VIEW_NOTES].states,
                EDIT_NOTE_DETAIL:
                    [command_handler] 
                    + self.get_callbacks()
                    + self.factory[EDIT_NOTE_DETAIL].states
                    + self.factory[VIEW_NOTES].states,
                DELETE_NOTE:
                    [command_handler] 
                    + self.get_callbacks()
                    + self.factory[DELETE_NOTE].states
                    + self.factory[VIEW_NOTES].states,
        }
    
    def share_preview_page_callback(self, application) -> None:
        application.add_handler(CallbackQueryHandler(self.factory[VIEW_NOTES].previewing_pages._preview_page_callback, pattern=f'^{NOTE_PAGE_CHAR}#'))
    
