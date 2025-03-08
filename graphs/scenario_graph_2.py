import logging
from agents.plot_agent import PlotAgent
from agents.persona_agent import PersonaAgent
from agents.relations_agent import RelationsAgent
from agents.activities_agent import ActivitiesAgent
from agents.yaml_agent import YamlAgent
from langgraph.graph import END, StateGraph, START
from models.scenario_2_graph_state import Scenario2GraphState

class ScenarioAgent:
    def __init__(
        self,
        persona_agent: PersonaAgent,
        plot_agent: PlotAgent,
        relations_agent: RelationsAgent,
        activities_agent: ActivitiesAgent,
        yaml_agent: YamlAgent,
    ) -> None:
        self.__persona_agent = persona_agent
        self.__plot_agent = plot_agent
        self.__relations_agent = relations_agent
        self.__activities_agent = activities_agent
        self.__yaml_agent = yaml_agent
        self.__workflow = None

    def __is_interactive(self):
        """
        Check if the script is running in an interactive environment.

        This function uses the "magic" variable __main__.__file__ to check if the script is running in an
        interactive environment (i.e. Jupyter notebook, Python shell, etc.). If the script is running in an
        interactive environment, __main__.__file__ will not exist and this function will return True.

        Returns:
            bool: True if the script is running in an interactive environment, False otherwise.
        """
        import __main__ as main
        return not hasattr(main, '__file__')

    def __show_workflow(self) -> None:
        """
        Show the compiled workflow graph as a mermaid diagram.

        This will display an interactive SVG diagram of the state machine in the
        Jupyter notebook. If the Jupyter notebook is not running, this will not
        produce any output.

        This is useful for debugging and understanding the flow of the state
        machine.
        """
        from IPython.display import Image, display
        diagram = Image(self.__workflow.get_graph().draw_mermaid_png())
        display(diagram)

    def __compile(self) -> None:
        """
        Compile the state machine graph if it has not been compiled yet.

        This is called automatically when invoke is called. It creates the
        state machine graph and compiles it into a runnable state machine.

        The graph is defined as follows:
        - START -> story_generator
        - story_generator -> activity_extractor
        - activity_extractor -> action_creator
        - action_creator -> tools (if there are tool calls)
        - tools -> action_creator
        - action_creator -> yaml_composer (if there are no tool calls)
        - yaml_composer -> END

        The state machine is then compiled and stored in the __workflow attribute.
        The graph is also visualized as a mermaid diagram using the __show_workflow
        method.

        This method is idempotent, meaning it can be called multiple times without
        effect.
        """
        if self.__workflow:
            return
        logging.info("---GRAPH COMPILE START---")
        workflow = StateGraph(Scenario2GraphState)

        # add nodes
        workflow.add_node("persona_agent", self.__persona_agent.node_action)
        workflow.add_node("plot_agent", self.__plot_agent.node_action)
        workflow.add_node("relations_agent", self.__relations_agent.node_action)
        workflow.add_node("activities_agent", self.__activities_agent.node_action)
        workflow.add_node("yaml_agent", self.__yaml_agent.node_action)

        # add edges
        workflow.add_edge(START, "persona_agent")
        workflow.add_edge("persona_agent", "plot_agent")
        workflow.add_edge("plot_agent", "relations_agent")
        workflow.add_edge("relations_agent", "activities_agent")
        workflow.add_edge("activities_agent", "yaml_agent")
        workflow.add_edge("yaml_agent", END)

        self.__workflow = workflow.compile()
        if self.__is_interactive():
            self.__show_workflow()
        print("---GRAPH COMPILE END---")

    def invoke(self, message: str):
        """
        Run the scenario graph given a message.

        This method will invoke the workflow given the provided message. If the
        workflow has not been compiled yet, it will call __compile to compile it.

        Args:
            message (str): The message to process.

        Returns:
            A dictionary containing the updated state after processing the message.

        """
        if not self.__workflow:
            self.__compile()
        return self.__workflow.invoke({"count": 1, "messages": []})

    def stream(self, message: str):
        """
        Stream the scenario graph given a message.

        This method will invoke the workflow given the provided message and
        stream the output as a generator. If the workflow has not been compiled
        yet, it will call __compile to compile it.

        Args:
            message (str): The message to process.

        Yields:
            A dictionary containing the updated state after processing the
            message.

        """
        if not self.__workflow:
            self.__compile()
        return self.__workflow.stream({"count": 1, "messages": []}, stream_mode="values")
