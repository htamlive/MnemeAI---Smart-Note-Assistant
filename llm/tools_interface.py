def get_note(queries_str: str) -> List[str]:
    """
    Extracts note text from a string containing multiple notes.

    Args:
    queries_str (str): A string containing multiple notes separated by a delimiter.

    Returns:
    List[str]: A list of strings containing individual note texts.

    Notes:
    - Assumes that each note is separated by a specific delimiter.
    - If the input string is empty, return an empty list.
    - If no notes are found, return an empty list.

    Example:
    >>> get_note("school work")
    ['', 'Do CS311 homework']
    """
    pass

def add_note(title: str, content: str) -> str:
    """
    Adds a note with a title and content.

    Args:
    title (str): The title of the note.
    content (str): The content or text of the note.

    Returns:
    (str): A message indicating the note has been added.

    Example:
    >>> add_note("Ideas", "Brainstorm project ideas")
    """
    pass

def create_task(title: str, body: str, datetime) -> str:
    """
    Creates a task with a title, body, and due datetime.

    Args:
    title (str): The title of the task.
    body (str): Additional body or description for the task.
    datetime: The due date and time for the task.

    Returns:
    (str): "pong" the function will returns "pong" when the reminder time has arrived

    Notes:
    - The datetime argument should be provided in a format understandable by the program.
    - This function may perform operations like saving the task to a database or scheduling it in a system.
    - If any argument is missing or invalid, the function may raise an error or handle it according to its implementation.

    Example:
    >>> create_task("Finish report", "Review and submit by end of the week.", "2024-05-10 23:59")
    """
    pass

def delete_task(task_name: str) -> str:
    """
    Deletes a task with the given name.

    Args:
    task_name (str): The name or identifier of the task to be deleted.

    Returns:
    (str): A message indicating the task has been deleted.

    Notes:
    - The task deletion may involve removing it from a database or marking it as completed.
    - If the task does not exist, the function may return an appropriate message or handle the case accordingly.

    Example:
    >>> delete_task("Finish report")
    """
    pass
