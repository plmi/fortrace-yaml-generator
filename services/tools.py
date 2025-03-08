#!/usr/bin/env python3

import yaml
from langchain_core.tools import tool


# https://python.langchain.com/docs/how_to/custom_tools/
@tool(parse_docstring=True)
def create_user(action: str, name: str, password: str, switch_to: bool, artifact_type: str, needle: bool) -> dict:
    """
    Creates a YAML structure for a user with the given parameters.

    Args:
        action: The action to be performed. Possible values are "create", "delete", or "switch_to".
        name: The name of the user to perform the action on. Default is "fortrace".
        password: The password for the user. Default is None.
        switch_to: A boolean indicating whether to switch to the user. Default is False.
        artifact_type: The type of artifact to add to the report. Possible values are "NEEDLE" or empty string. Default is empty string.
        needle: If True, the user action should not be logged later; if False, it will be logged.

    Returns:
        dict: The YAML representation of the user data.
    
    Raises:
        ValueError: If `user_type` is not 'add' or 'update'.
    """
    
    data = {
        'fortrace.usermanagement:': {
            'action': action,
            'name': name,
            'password': password,
            'switch_to': switch_to,
            'artifact_type': artifact_type,
        }
    }
    
    return yaml.dump(data, default_flow_style=False)

@tool(parse_docstring=True)
def create_browser_action(action: str, url: str, artifact_type: str = "") -> dict:
    """
    Creates a YAML structure for a browser action with the given parameters.

    Args:
        action: The action to be performed. Possible values are "open", "browse_to", and "close".
        url: The URL to browse to. Required if action is "browse_to". Default is None.
        artifact_type: The type of artifact to add to the report. Possible values are "NEEDLE" or empty string. Default is empty string.

    Returns:
        str: The YAML representation of the browser action data.
    """

    data = {
        'fortrace.browser': {
            'action': action,
            'url': url,
            'artifact_type': artifact_type
        }
    }
    
    return yaml.dump(data, default_flow_style=False)