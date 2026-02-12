import os
from crewai import Agent, Task, LLM

class CoderAgentFactory:
    """Generates production-ready Python code with docstrings and clean structure."""

    def __init__(self):
        self.llm = LLM(
            model="groq/llama-3.3-70b-versatile",  
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2,
            stream=True
        )

    def create(self) -> Agent:
        return Agent(
            role="CoderAgent",
            goal="Generate clean, modular, and well-documented Python code following PEP 8 standards.",
            backstory="A senior Python developer who writes maintainable, readable, and tested code.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def get_task(self, agent: Agent, prompt: str) -> Task:
        return Task(
            description=(
                f"You are to implement the following feature request in Python:\n\n"
                f"{prompt}\n\n"
                "Requirements:\n"
                "- Use clean, modular functions with clear separation of concerns.\n"
                "- Enforce STRICT type hinting (PEP 484) for all functions and classes.\n"
                "- Add inline docstrings for all public functions and classes.\n"
                "- Follow PEP 8 style guidelines.\n"
                "- Include robust error handling (try/except blocks).\n"
                "- Do NOT include test cases or example usage.\n"
                "- Output ONLY the raw Python code. No markdown, no explanations, no code fences."
            ),
            expected_output="Raw Python source code only. No markdown formatting.",
            agent=agent
        )
