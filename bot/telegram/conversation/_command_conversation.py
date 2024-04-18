from telegram.ext import MessageHandler
from telegram import Update
from telegram.ext import ContextTypes

class CommandConversation:
    def __init__(self) -> None:
        self._states : list[MessageHandler] = []

    @property
    def states(self) -> list[MessageHandler]:
        return self._states
    
    async def start_conservation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        raise NotImplementedError
    