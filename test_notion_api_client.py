from pkg.notion_api.client import NotionClient

if __name__ == '__main__':
    client = NotionClient()
    
    # Auth via server, get app object
    # server = authorization_server.App()
    # print(client.set_session(server.app.notion_blueprint))
    
    database_id = ""
    
    print(client.get_notes(database_id))
    print(client.post_notes(database_id, "Notion", "Knowledge Base"))
    print(client.patch_notes(database_id, 1, "Google Task", "Task manager"))
    print(client.delete_notes(database_id, 0))
    print(client.delete_all_notes(database_id))