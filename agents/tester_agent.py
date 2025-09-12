import os
from crewai import Agent, Task, LLM

class TesterAgentFactory:
    """Generates pytest-compatible unit tests for given Python code."""

    def __init__(self):
        self.llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
            stream=True
        )

    def create(self) -> Agent:
        return Agent(
            role="TesterAgent",
            goal="Generate pytest-compatible unit tests covering normal and edge cases.",
            backstory="A QA engineer skilled in writing thorough and maintainable Python test cases.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def get_task(self, agent: Agent, code: str) -> Task:
        return Task(
            description=(
                "Write pytest-compatible unit tests for the following Python code.\n\n"
                f"{code}\n\n"
                "Requirements:\n"
                "- Use pytest framework.\n"
                "- Cover normal cases, edge cases, and error handling.\n"
                "- Each test should have a clear and descriptive name.\n"
                "- Do NOT modify the original code."
            ),
            expected_output="A complete pytest module with multiple test functions.",
            agent=agent
        )
