from client import TelegramClient

class ConversationController:

    def __init__(self, client: TelegramClient) -> None:
        self.client = client
        self.factory = dict()

    
    def get_states_dict(self, command_handler):
        ''

    def get_callbacks(self):
        ''

    def get_entry_points(self):
        ''