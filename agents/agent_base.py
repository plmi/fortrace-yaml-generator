from typing import Any
from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import RunnableLike


class AgentBase(ABC):
    @abstractmethod
    def node_action(self, state: Any) -> RunnableLike:
        """
        Abstract method to be implemented by inheriting classes.
        This method should define the action to be taken by the agent given a state.
        
        :param state: The current state of the environment or context
        :return: A RunnableLike object that can be invoked
        """
        pass

    def create_system_prompt(self, prompt: str) -> ChatPromptTemplate:
        """
        Internal method to create a system prompt.
        
        :param prompt: The input prompt to be processed
        :return: The processed system prompt
        """
        return ChatPromptTemplate.from_strings(["system", prompt])