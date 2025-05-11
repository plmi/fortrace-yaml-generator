import os
import json
import logging
from typing import Any
from langchain.schema import Document
from agents.agent_base import AgentBase
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.base import RunnableLike
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema.messages import AIMessage

class YamlAgent(AgentBase):
    def __init__(self, model: BaseChatModel, prompt: str) -> None:
        """
        Initialize the YamlAgent.

        Args:
            model (BaseChatModel): The underlying language model to use for generating the personas.
        """
        self.__model: BaseChatModel = model
        self.__original_prompt: str = prompt
        self.__prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(prompt)

    def __extract_response(self, response: str, marker: str):
        response = response.split(f'<{marker}>')[1].split(f'</{marker}>')[0]
        return response

    def __create_index(self, directory: str):
        documents = []
        for filename in os.listdir(directory):
            # print(filename)
            if filename.endswith(".json"):
                with open(os.path.join(directory, filename), "r") as f:
                    schema = json.load(f)
                    # print(json.dumps(schema))
                    # print(type(schema))
                    module = schema["module"]
                    for function in schema["functions"]:
                        # Create a document for each function
                        # print(function)
                        # print(type(json.dumps(function)))
                        page_content = json.dumps(function)
                        # page_content = f"{module}: {function['action']} - {function['description']}"
                        metadata = {
                            "module": module,
                            "action": function["action"],
                            "examples": function["examples"],
                            "properties": function["properties"],
                            "description": function["description"]
                        }
                        documents.append(Document(page_content=page_content, metadata=metadata))

        print(f'Created {len(documents)} documents')
        embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.environ["OPENAI_KEY"],
        )

        # Create a vector store
        vector_store = FAISS.from_documents(documents, embeddings)

        # Save the vector store (optional)
        vector_store.save_local("vector_store")

    def __create_vector_storage(self):
        # Generate embeddings
        embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.environ["OPENAI_KEY"],
        )

        print(os.path.abspath("../vector_store"))

        # Load the vector store with dangerous deserialization allowed
        return FAISS.load_local(
            "/app/vector_store",
            embeddings,
            allow_dangerous_deserialization=True
        )

    def __create_qa_chain(self, vector_store):
        # Create the RetrievalQA chain with the custom prompt
        retriever = vector_store.as_retriever(search_kwargs={"k": 100})
        return RetrievalQA.from_chain_type(
            llm=self.__model,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": self.__prompt}
        )

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
        logging.info("---YAML START---")
        # setup vector store
        vector_store = self.__create_vector_storage()

        # prepare prompt
        self.__original_prompt = self.__original_prompt.replace('{plot}', state['plot'])
        personas: str = state['personas'].replace('{', '{{').replace('}', '}}')
        self.__original_prompt = self.__original_prompt.replace('{personas}', personas)
        self.__original_prompt = self.__original_prompt.replace('{relations}', state['relations'])
        self.__original_prompt = self.__original_prompt.replace('{activities}', state['activities'])
        self.__prompt = ChatPromptTemplate.from_template(self.__original_prompt)

        qa_chain = self.__create_qa_chain(vector_store)

        # generate yaml
        query: str = f'Which module functions are necessary to replicate the system activities in the table below?\n\n{state["activities"]}'
        response = qa_chain.invoke({'query': query})
        print(response)

        yaml = self.__extract_response(response['result'], 'final_yaml')
        content: str = f"""
**ForTrace YAML Configuration**

```yaml
{yaml}
```
"""
        logging.info("---YAML END---")
        #return {**state, "yaml": yaml, "messages": [response['result']]}
        return {**state, "yaml": yaml, "messages": [AIMessage(content=content)]}
