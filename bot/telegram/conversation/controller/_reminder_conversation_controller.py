
from ._conversation_controller import ConversationController
from config import Patterns, EDIT_REMINDER_DETAIL, EDIT_REMINDER_TITLE, DELETE_REMINDER, VIEW_REMINDERS, REMIND_TEXT, EDIT_REMINDER_TIME
from telegram.ext import CallbackQueryHandler
from ..reminder_conversation.modify_reminder_conversation import EditReminderDetailConversation, EditReminderTitleConversation, DeleteReminderConversation
from ..note_conversation.modify_note_conversation import ModifyNoteConversation
from ..reminder_conversation._view_reminders_conversation import ViewRemindersConversation
from ..reminder_conversation._remind_conversation import RemindConversation

from config import Commands, REMINDER_PAGE_CHAR
from telegram.ext import CommandHandler

class ReminderConversationController(ConversationController):
    def __init__(self, client) -> None:
        super().__init__(client)

        self.factory: dict[int, ModifyNoteConversation] = {
            VIEW_REMINDERS: ViewRemindersConversation(VIEW_REMINDERS, EDIT_REMINDER_TITLE, EDIT_REMINDER_DETAIL, self.client),
            EDIT_REMINDER_DETAIL: EditReminderDetailConversation(EDIT_DETAIL=EDIT_REMINDER_DETAIL, client=self.client),
            EDIT_REMINDER_TITLE: EditReminderTitleConversation(EDIT_TITLE=EDIT_REMINDER_TITLE, client=self.client),
            EDIT_REMINDER_TIME: EditReminderDetailConversation(EDIT_DETAIL=EDIT_REMINDER_TIME, client=self.client),
            DELETE_REMINDER: DeleteReminderConversation(DELETE_REMINDER,VIEW_REMINDERS=VIEW_REMINDERS, client=self.client),
            REMIND_TEXT: RemindConversation(REMIND_TEXT, self.client),
        }

    def get_states_dict(self, command_handler):
        return {
                REMIND_TEXT: [command_handler] + self.factory[REMIND_TEXT].states,

                VIEW_REMINDERS: [
                    command_handler,
                ] + self.get_callbacks() + self.factory[VIEW_REMINDERS].states,

                EDIT_REMINDER_TITLE:
                    [command_handler] 
                    + self.get_callbacks()
                    + self.factory[EDIT_REMINDER_TITLE].states
                    + self.factory[VIEW_REMINDERS].states,

                EDIT_REMINDER_DETAIL:
                    [command_handler] 
                    + self.get_callbacks()
                    + self.factory[EDIT_REMINDER_DETAIL].states
                    + self.factory[VIEW_REMINDERS].states,

                DELETE_REMINDER:
                    [command_handler] 
                    + self.get_callbacks()
                    + self.factory[DELETE_REMINDER].states
                    + self.factory[VIEW_REMINDERS].states,

                EDIT_REMINDER_TIME:
                    [command_handler] 
                    + self.get_callbacks()
                    + self.factory[EDIT_REMINDER_TIME].states          
            }
    
    def get_callbacks(self):
        return [
            CallbackQueryHandler(self.factory[EDIT_REMINDER_TITLE].start_conversation, pattern=f'^{Patterns.EDIT_REMINDER_TITLE.value}'),
            CallbackQueryHandler(self.factory[EDIT_REMINDER_DETAIL].start_conversation, pattern=f'^{Patterns.EDIT_REMINDER_DETAIL.value}'),
            CallbackQueryHandler(self.factory[DELETE_REMINDER].start_conversation, pattern=f'^{Patterns.DELETE_REMINDER.value}'),
        ]
    
    def get_entry_points(self):
        return [
            CommandHandler(Commands.REMINDER.value, self.factory[REMIND_TEXT].start_conversation),
            CommandHandler(Commands.VIEW_REMINDERS.value, self.factory[VIEW_REMINDERS].start_conversation),
        ] + self.get_callbacks()
    
    def share_preview_page_callback(self, application) -> None:
        application.add_handler(CallbackQueryHandler(self.factory[VIEW_REMINDERS].previewing_pages.preview_page_callback, pattern=f'^{REMINDER_PAGE_CHAR}#'))