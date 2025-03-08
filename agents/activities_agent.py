import logging
from typing import Any
from agents.agent_base import AgentBase
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.base import RunnableLike
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

class ActivitiesAgent(AgentBase):
    def __init__(self, model: BaseChatModel, prompt: str) -> None:
        """
        Initialize the ActivitiesAgent.

        Args:
            model (BaseChatModel): The underlying language model to use for generating the personas.
        """
        self.__model: BaseChatModel = model
        self.__prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(prompt)
        self.__chain: RunnableSequence = self.__prompt | self.__model

    def __extract_response(self, response: str):
        response = response.split(f'```markdown')[1].split(f'```')[0]
        return response

    def node_action(self, state: Any) -> RunnableLike:
        """
        This function is called by the LangChain executor to generate a story based on the given task.

        Args:
            state (Any): The current state of the executor. Contains the task to generate a story for.

        Returns:
            RunnableLike: The updated state with the generated story and messages.
        """
        logging.info("---ACTIVITIES START---")
        response: BaseMessage = self.__chain.invoke({"relations": state["relations"], "plot": state["plot"], "personas": state["personas"]})
        activities: str = self.__extract_response(response.content)
        print(activities)
        logging.info("---ACTIVITIES END---")

        content: str = f"""
**Activities**

```
{activities}
```
"""

        return {**state, "activities": activities, "messages": [AIMessage(content=content)]}
        #return {**state, "activities": activities, "messages": [response]}
