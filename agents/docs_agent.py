import os
from crewai import Agent, Task, LLM

class DocsAgentFactory:
    """Generates README.md and adds inline docstrings to given Python code."""

    def __init__(self):
        self.llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
            stream=True
        )

    def create(self) -> Agent:
        return Agent(
            role="DocsAgent",
            goal="Write a README.md and insert detailed docstrings in Python code.",
            backstory="A technical writer who creates clear developer documentation.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def get_task(self, agent: Agent, code: str) -> Task:
        return Task(
            description=(
                "Generate a README.md for the following Python project and then insert detailed inline docstrings.\n\n"
                f"{code}\n\n"
                "README Requirements:\n"
                "- Explain the project purpose.\n"
                "- Show installation and usage instructions.\n"
                "- Provide example commands or code.\n\n"
                "Docstring Requirements:\n"
                "- Use Google-style or reStructuredText format.\n"
                "- Include descriptions of parameters and return values."
            ),
            expected_output="A README.md followed by the updated Python code with inline docstrings.",
            agent=agent
        )
