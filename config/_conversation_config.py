from telegram.ext import ConversationHandler
(
    NOTE_TEXT, REMIND_TEXT, 
    VIEW_NOTES, EDIT_NOTE_TITLE, EDIT_NOTE_DETAIL, DELETE_NOTE,
    VIEW_REMINDERS, EDIT_REMINDER_TITLE, EDIT_REMINDER_DETAIL, EDIT_REMINDER_TIME, DELETE_REMINDER,
    PROMPTING,
    NOTION_REQ_DB, NOTION_REQ_PAGE,
    TIMEZONE_REQ,
    QUERY_KNOWLEDGE
    ) = range(16)

END = ConversationHandler.END

from enum import Enum

class Commands(Enum):
    NOTE = "note"
    REMINDER = "remind"
    VIEW_NOTES = "view_notes"
    VIEW_REMINDERS = "view_reminders"
    PROMPTING = "ah"
    NOTION_REQ_DB = "notion_db"
    NOTION_REQ_PAGE = "notion_page"
    TIMEZONE_REQ = "timezone"
    QUERY_KNOWLEDGE = "query_knowledge"

PATTERN_DELIMITER = "@"
PAGE_DELIMITER = "#"
REMINDER_PAGE_CHAR = "r"
NOTE_PAGE_CHAR = "n"
DETAIL_NOTE_CHAR = "dn"
DETAIL_REMINDER_CHAR = "dr"

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
    CONFIRM_DELETE_REMINDER = "confirm_delete_reminder" + PATTERN_DELIMITER
    CANCEL_DELETE_REMINDER = "cancel_delete_reminder" + PATTERN_DELIMITER
