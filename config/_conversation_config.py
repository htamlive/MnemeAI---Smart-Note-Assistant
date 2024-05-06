from telegram.ext import ConversationHandler
(
    NOTE_TEXT, REMIND_TEXT, 
    VIEW_NOTES, EDIT_NOTE_TITLE, EDIT_NOTE_DETAIL, DELETE_NOTE,
    VIEW_REMINDERS, EDIT_REMINDER_TITLE, EDIT_REMINDER_DETAIL, EDIT_REMINDER_TIME, DELETE_REMINDER,
    PROMPTING,
    ) = range(12)

END = ConversationHandler.END

from enum import Enum

class Commands(Enum):
    NOTE = "note"
    REMIND = "remind"
    VIEW_NOTES = "view_notes"
    VIEW_REMINDERS = "view_reminders"
    PROMPTING = "ah"

PATTERN_DELIMITER = "@"

class Patterns(Enum):
    EDIT_NOTE_TITLE = "edit_note_title" + PATTERN_DELIMITER
    EDIT_NOTE_DETAIL = "edit_note_detail" + PATTERN_DELIMITER
    DELETE_NOTE = "delete_note" + PATTERN_DELIMITER
    EDIT_REMINDER_TITLE = "edit_reminder_title" + PATTERN_DELIMITER
    EDIT_REMINDER_DETAIL = "edit_reminder_detail" + PATTERN_DELIMITER
    EDIT_REMINDER_TIME = "edit_reminder_time" + PATTERN_DELIMITER
    DELETE_REMINDER = "delete_reminder" + PATTERN_DELIMITER
    CONFIRM_DELETE_NOTE = "confirm_delete_note" + PATTERN_DELIMITER
    CANCEL_DELETE_NOTE = "cancel_delete_note" + PATTERN_DELIMITER
