from langchain.tools import tool
import datetime
import os

@tool
def note_taking_tool(note: str, filename: str = "notes.txt") -> str:
    """
    This tool allows you to take notes and save them to a file.

    Args:
        note: str: The note you want to save.
        filename: str: The name of the file to save the note to. Defaults to "notes.txt".

    Returns:
        A string confirming the note has been saved.
    """
    try:
        with open(filename, "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {note}\n")
        return f"Note '{note}' saved to '{filename}'"
    except Exception as e:
        return f"Error saving note: {e}"

@tool
def to_do_list_tool(task: str, filename: str = "to_do.txt") -> str:
    """
    This tool allows you to add tasks to a to-do list and save them to a file.

    Args:
        task: str: The task you want to add to the to-do list.
        filename: str: The name of the file to save the to-do list to. Defaults to "to_do.txt".

    Returns:
        A string confirming the task has been added to the to-do list.
    """
    try:
        with open(filename, "a") as f:
            f.write(f"- {task}\n")
        return f"Task '{task}' added to to-do list in '{filename}'"
    except Exception as e:
        return f"Error adding task: {e}"
