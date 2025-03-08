import logging
from typing import Any
from agents.agent_base import AgentBase
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.base import RunnableLike
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.messages import HumanMessage, AIMessage

class RelationsAgent(AgentBase):
    def __init__(self, model: BaseChatModel, prompt: str) -> None:
        """
        Initialize the PlotAgent.

        Args:
            model (BaseChatModel): The underlying language model to use for generating the relations.
        """
        self.__model: BaseChatModel = model
        self.__prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(prompt)
        self.__chain: RunnableSequence = self.__prompt | self.__model

    def __extract_response(self, response: str, marker: str):
        response = response.split(f'<{marker}>')[1].split(f'</{marker}>')[0]
        return response

    def node_action(self, state: Any) -> RunnableLike:
        """
        This function is called by the LangChain executor to generate a story based on the given task.

        Args:
            state (Any): The current state of the executor. Contains the task to generate a story for.

        Returns:
            RunnableLike: The updated state with the generated story and messages.
        """
        logging.info("---RELATIONS START---")
        response: BaseMessage = self.__chain.invoke({"plot": state["plot"], "personas": state["personas"]})
        relations: str = self.__extract_response(response.content, 'mermaid_diagram')
        print('relations')
        print(relations)
        logging.info("---RELATIONS END---")
        content: str = f"""
**Relations**

{relations}
"""

        #return {**state, "relations": relations, "messages": [response]}
        return {**state, "relations": relations, "messages": [AIMessage(content=content)]}
