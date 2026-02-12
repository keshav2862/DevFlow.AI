```python
def add(num1: float, num2: float) -> float:
    """
    Adds two numbers.

    Args:
        num1 (float): The first number.
        num2 (float): The second number.

    Returns:
        float: The sum of num1 and num2.
    """
    try:
        return num1 + num2
    except TypeError:
        raise ValueError("Both inputs must be numbers")


def subtract(num1: float, num2: float) -> float:
    """
    Subtracts num2 from num1.

    Args:
        num1 (float): The first number.
        num2 (float): The second number.

    Returns:
        float: The difference between num1 and num2.
    """
    try:
        return num1 - num2
    except TypeError:
        raise ValueError("Both inputs must be numbers")


def multiply(num1: float, num2: float) -> float:
    """
    Multiplies two numbers.

    Args:
        num1 (float): The first number.
        num2 (float): The second number.

    Returns:
        float: The product of num1 and num2.
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
    """

    def __init__(self):
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