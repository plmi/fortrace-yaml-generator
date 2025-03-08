import os
import logging
import streamlit as st
import ruamel.yaml as yaml
from ruamel.yaml import YAML
from dotenv import load_dotenv, find_dotenv
from typing import Dict, Any, Union
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatDeepInfra
from langchain_core.language_models.chat_models import BaseChatModel
from graphs.scenario_graph_2 import ScenarioAgent
from agents.persona_agent import PersonaAgent
from agents.plot_agent import PlotAgent
from agents.relations_agent import RelationsAgent   
from agents.activities_agent import ActivitiesAgent
from agents.yaml_agent import YamlAgent
from agents.persona_agent import PersonaAgent
from services.tools import (
    create_user,
    create_browser_action,
)
from langchain_deepseek import ChatDeepSeek


logging.getLogger().setLevel(logging.INFO)

# load environment variables
load_dotenv(find_dotenv())
os.environ["OPENAI_KEY"] = st.secrets.get("OPENAI_KEY", "")

def load_configuration() -> Dict[str, Any]:
    """Load the configuration."""
    with open("./configuration.yaml", "r") as f:
        yaml = YAML(typ='safe', pure=True)
        return yaml.load(f)


def save_configuration(configuration: Dict[str, Union[str, list[str]]]) -> None:
    """Save the configuration."""
    # use ruamel.yaml instead of pyyaml as latter can't save multi-line strings with '|'
    with open("./configuration.yaml", "w") as file:
        yaml = YAML(typ='safe', pure=True)
        yaml.default_flow_style = False
        yaml.default_style = '|'
        yaml.dump(configuration, file)


def initialize_session_state(configuration: Dict[str, Union[str, list[str]]]) -> None:
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # st.session_state.messages = [
        #     {"role": "assistant", "content": "How may I help you?"}
        # ]
    if "model_choice" not in st.session_state:
        st.session_state.model_choice = configuration["app"]["default_model"]
    if "temperature" not in st.session_state:
        st.session_state.temperature = configuration["app"]["default_temperature"]
    if "api_key" not in st.session_state:
        st.session_state.api_key = st.secrets.get("OPENAI_KEY", "")
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = os.getenv("SYSTEM_PROMPT", "")
    if "title" not in st.session_state:
        st.session_state.title = configuration["app"]["title"]
    if "models" not in st.session_state:
        st.session_state.models = configuration["app"]["models"]
    for prompt_key in configuration["prompts"]:
        if prompt_key not in st.session_state:
            st.session_state[prompt_key] = configuration["prompts"][prompt_key]
    for index, (_, model_value) in enumerate(configuration["prompt_models"].items()):
        session_key = f"{index}_model"
        #print(f'session_key: {session_key}')
        if session_key not in st.session_state:
            st.session_state[session_key] = model_value
            #print(model_value)
    for index, (_, temperature_value) in enumerate(configuration["temperatures"].items()):
        temperature_key = f"{index}_temperature"
        if temperature_key not in st.session_state:
            st.session_state[temperature_key] = temperature_value


def initialize_assistant():
    """
    Initialize the ScenarioAssistant with the selected model and prompts.

    The selected model is determined by the user selection in the sidebar.
    The prompts are loaded from the configuration file.

    The ScenarioAssistant is stored in the session state as 'assistant'.
    """
    st.session_state.scenario_agent = ScenarioAgent(
        PersonaAgent(model=get_model(st.session_state['0_model'], st.session_state['0_temperature']), prompt=st.session_state.persona_prompt),
        PlotAgent(model=get_model(st.session_state['1_model'], st.session_state['1_temperature']), prompt=st.session_state.plot_prompt),
        RelationsAgent(model=get_model(st.session_state['2_model'], st.session_state['2_temperature']), prompt=st.session_state.relations_prompt),
        ActivitiesAgent(model=get_model(st.session_state['3_model'], st.session_state['3_temperature']), prompt=st.session_state.activities_prompt),
        YamlAgent(model=get_model(st.session_state['4_model'], st.session_state['4_temperature']), prompt=st.session_state.yaml_prompt),
    )

def get_model(model_name: str, temperature: float = 0) -> BaseChatModel:
    """Get the chat model based on user selection."""
    print('initialize model {} with temperature {}'.format(model_name, temperature))
    try:
        if model_name in [
            "gpt-4o-mini",
            "o1-preview",
            "o1-mini",
            "o3-mini",
            "",
        ]:
            print('initialize model_name:', model_name)
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=st.session_state.api_key,
            )
        elif model_name in [
            "DeepSeek-R1"
        ]:
            os.environ["DEEPINFRA_API_TOKEN"] = st.secrets.get("DEEPINFRA_API_TOKEN", "")
            os.environ["DEEPSEEK_API_KEY"] = st.secrets.get("DEEPSEEK_API_KEY", "")
            # return ChatDeepInfra(model_id="deepseek-ai/DeepSeek-R1", temperature=temperature)
            return ChatDeepSeek(
                model="deepseek-chat",
                temperature=temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )
    except Exception as e:
        st.error(f"Error initializing model: {str(e)}")

def render_sidebar(configuration: Dict[str, Union[str, list[str]]]) -> None:
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.title(st.session_state.title)
        st.write(
            # "This chatbot converts a forensic scenario into a YAML file for ForTrace."
            "Create a synthetic YAML configuration for ForTrace."
        )

        st.subheader("Configuration")

        if st.session_state.model_choice != "ollama-3.1":
            st.text_input(
                "Enter your OpenAI API Key",
                type="password",
                key="api_key",
                on_change=initialize_assistant,
            )

        render_prompt_config(configuration)


def render_chat_messages() -> None:
    """Render the chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input() -> None:
    """Handle user input and generate response via button click."""
    st.markdown(
        """
        <style>
        div.stButton > button {
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Replace st.chat_input with a button.
    if st.button(
        "Generate scenario",
        disabled=not st.session_state.api_key,
    ):
        # Use the same prompt text as before.
        # prompt = "Generate a forensic scenario related to Star Wars."
        # st.session_state.messages.append({"role": "user", "content": prompt})
        
        # with st.chat_message("user"):
        #     st.write(prompt)

        with st.chat_message("assistant"):
            try:
                # Stream the response from your scenario agent.
                for chunk in st.session_state.scenario_agent.stream(''):
                    if len(chunk["messages"]) > 0:
                        # Extract the latest message from the chunk.
                        message = chunk["messages"][-1].content
                        st.write(message)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": message}
                        )
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

def handle_user_input1() -> None:
    """Handle user input and generate response."""
    if prompt := st.chat_input(
        disabled=not st.session_state.api_key
        and st.session_state.model_choice != "ollama-3.1",
        placeholder="Generate a forensic scenario related to Star Wars.",
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            try:
                for chunk in st.session_state.scenario_agent.stream(prompt):
                # for chunk in st.session_state.assistant.stream(prompt):
                    if len(chunk["messages"]) > 0:
                        message = st.write(chunk["messages"][-1].content)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": message}
                        )
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

def get_session_state_by_key(key: str) -> Any:
    if key == 'persona_prompt':
        return st.session_state['persona_prompt']
    elif key == 'plot_prompt':
        return st.session_state['plot_prompt']
    elif key == 'relations_prompt':
        return st.session_state['relations_prompt']
    elif key == 'activities_prompt':
        return st.session_state['activities_prompt']
    elif key == 'yaml_prompt':
        return st.session_state['yaml_prompt']
    raise ValueError(f"Unknown key: {key}")


def render_prompt_config(configuration: Dict[str, Union[str, list[str]]]) -> None:
    """Render the prompt configuration section."""
    st.header("Prompt Configuration")

    prompts: Dict[str, str] = {
        # need to be the same keys as in the YAML
        'persona_prompt': 'Persona',
        'plot_prompt': 'Plot',
        'relations_prompt': 'Relations',
        'activities_prompt': 'Activities',
        'yaml_prompt': 'YAML',
    }
    tabs = st.tabs(prompts.values())

    for index, (key, value) in enumerate(prompts.items()):
        with tabs[index]:
             # Initialize session state for model selection if not already present.
            print(index)
            model_state_key = f"{index}_model"
            # if model_state_key not in st.session_state:
            #     st.session_state[model_state_key] = "gpt-4o-mini"

            # Create a selectbox to choose the model.
            selected_model = st.selectbox(
                "Select a model",
                options=st.session_state.models,
                key=model_state_key,
                on_change=initialize_assistant,
            )
            # -------------------------------
            # Temperature slider
            # -------------------------------
            # Create a unique key for the temperature slider in session state.
            temp_state_key = f"{index}_temperature"

            selected_temp = st.slider(
                "Sampling Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state[temp_state_key],
                step=0.05,
                key=temp_state_key,
                on_change=initialize_assistant,
            )

            st.session_state[key] = st.text_area(
                'Prompt',
                value=st.session_state[key],
                height=550,
                # unique index required when using multiple st.text_area controls
                key=index
            )

    if st.button("Save Changes"):
        for prompt_key in prompts.keys():
            configuration["prompts"][prompt_key] = st.session_state[prompt_key]
        
        save_configuration(configuration)
        st.success("Configuration updated successfully!", icon="💾")


configuration: Dict[str, Union[str, list[str]]] = {}

def main() -> None:
    """Main function to run the Streamlit app."""
    configuration = load_configuration()
    initialize_session_state(configuration)
    st.set_page_config(page_title=st.session_state.title)
    initialize_assistant()

    render_sidebar(configuration)
    render_chat_messages()
    handle_user_input()


if __name__ == "__main__":
    main()
