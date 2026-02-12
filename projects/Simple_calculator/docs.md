README.md
================

# Calculator Project
The Calculator Project is a simple Python library that provides basic arithmetic operations. It includes functions for addition, subtraction, multiplication, and division, as well as a Calculator class that allows for more complex calculations.

## Installation
To install the Calculator Project, you will need to have Python 3.6 or later installed on your system. You can install the project using pip:
```bash
pip install calculator-project
```
Alternatively, you can clone the repository and install the project manually:
```bash
git clone https://github.com/your-username/calculator-project.git
cd calculator-project
python setup.py install
```
## Usage
To use the Calculator Project, you can import the `Calculator` class and create an instance:
```python
from calculator import Calculator

calculator = Calculator()
result = calculator.calculate('+', 2, 3)
print(result)  # Output: 5.0
```
You can also use the individual arithmetic functions:
```python
from calculator import add, subtract, multiply, divide

result = add(2, 3)
print(result)  # Output: 5.0

result = subtract(5, 2)
print(result)  # Output: 3.0

result = multiply(4, 5)
print(result)  # Output: 20.0

result = divide(10, 2)
print(result)  # Output: 5.0
```
## Example Commands
Here are some example commands that demonstrate how to use the Calculator Project:
```python
# Create a Calculator instance and perform a calculation
calculator = Calculator()
result = calculator.calculate('*', 4, 5)
print(result)  # Output: 20.0

# Use the individual arithmetic functions
result = add(2, 3)
print(result)  # Output: 5.0

result = subtract(5, 2)
print(result)  # Output: 3.0

result = multiply(4, 5)
print(result)  # Output: 20.0

result = divide(10, 2)
print(result)  # Output: 5.0
```

```python
def add(num1: float, num2: float) -> float:
    """
    Adds two numbers.

    Args:
        num1 (float): The first number to add.
        num2 (float): The second number to add.

    Returns:
        float: The sum of num1 and num2.

    Raises:
        ValueError: If either num1 or num2 is not a number.
    """
    try:
        return num1 + num2
    except TypeError:
        raise ValueError("Both inputs must be numbers")


def subtract(num1: float, num2: float) -> float:
    """
    Subtracts num2 from num1.

    Args:
        num1 (float): The number to subtract from.
        num2 (float): The number to subtract.

    Returns:
        float: The difference between num1 and num2.

    Raises:
        ValueError: If either num1 or num2 is not a number.
    """
    try:
        return num1 - num2
    except TypeError:
        raise ValueError("Both inputs must be numbers")


def multiply(num1: float, num2: float) -> float:
    """
    Multiplies two numbers.

    Args:
        num1 (float): The first number to multiply.
        num2 (float): The second number to multiply.

    Returns:
        float: The product of num1 and num2.

    Raises:
        ValueError: If either num1 or num2 is not a number.
    """
    try:
        return num1 * num2
    except TypeError:
        raise ValueError("Both inputs must be numbers")


def divide(num1: float, num2: float) -> float:
    """
    Divides num1 by num2.

    Args:
        num1 (float): The dividend.
        num2 (float): The divisor.

    Returns:
        float: The quotient of num1 and num2.

    Raises:
        ZeroDivisionError: If num2 is zero.
        ValueError: If either num1 or num2 is not a number.
    """
    try:
        if num2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return num1 / num2
    except TypeError:
        raise ValueError("Both inputs must be numbers")


class Calculator:
    """
    A simple calculator class.

    Provides methods for basic arithmetic operations.

    Attributes:
        None

    Methods:
        calculate: Performs the specified operation on two numbers.
    """

    def __init__(self):
        """
        Initializes the Calculator instance.

        Args:
            None

        Returns:
            None
        """
        pass

    def calculate(self, operation: str, num1: float, num2: float) -> float:
        """
        Performs the specified operation on two numbers.

        Args:
            operation (str): The operation to perform. One of '+', '-', '*', '/'.
            num1 (float): The first number.
            num2 (float): The second number.

        Returns:
            float: The result of the operation.

        Raises:
            ValueError: If the operation is not one of '+', '-', '*', '/'.
        """
        operations = {
            '+': add,
            '-': subtract,
            '*': multiply,
            '/': divide
        }
        try:
            return operations[operation](num1, num2)
        except KeyError:
            raise ValueError("Invalid operation")
```