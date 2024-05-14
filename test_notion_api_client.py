from pkg.notion_api.client import NotionClient

if __name__ == '__main__':
    client = NotionClient()
    
    # Auth via server, get app object
    # server = authorization_server.App()
    # print(client.set_session(server.app.notion_blueprint))
    ID = 2
    # print(client.auth_client.get_auth_url(ID))
    database_id = "39057a07ecf74585aa8580f5ba0e419a"
    
    print(client.get_user(ID))
    print(client.get_notes(ID))
    print(client.get_note_content(ID, 0))
    # print(client.register_database_id(ID, database_id))
    # print(client.get_database_id(ID))
    # print(client.register_page_database(2, "05633266620d4746822cdeb99ea28144", "Another one 2"))
    # print(client.get_notes(ID, database_id))
    # print(client.post_notes(ID, database_id, "Notion", "Knowledge Base"))
    # print(client.patch_notes(ID, database_id, 1, "Google Task", "Task manager"))
    # print(client.delete_notes(ID, database_id, 0))
    # print(client.delete_all_notes(ID, database_id))
    # print(client.query(ID, database_id, "What is a cow"))