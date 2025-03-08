from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class Scenario2GraphState(TypedDict):
    """
    Represents the state of a forensic scenario graph.

    This class encapsulates various components of a forensic scenario, including its story,
    task, available actions, user activities, model messages, and YAML representation.

    Attributes:
        story (str): A story of a forensic scenario used as context.
        task (str): The main task or objective to be accomplished in this scenario.
        actions (str): A string describing the available actions in the scenario.
        activities (list[str]): A list of user activities extracted from the scenario.
        messages (Annotated[list, add_messages]): A list of messages from the model.
        yaml (str): A YAML representation of the scenario's configuration or data.
    """
    count: int
    """A story of a forensic scenario used as context"""
   
    personas: str
    """The main task or objective to be accomplished in this scenario."""

    relations: str
    """The main task or objective to be accomplished in this scenario."""
   
    plot: str
    """A string describing the available actions in the scenario."""

    activities: list[str]
    """A list of user activites extracted from the scenario"""

    messages: Annotated[list, add_messages]
    """A list of messages from the model"""

    yaml: str
    """A YAML representation of the scenario's configuration or data."""
