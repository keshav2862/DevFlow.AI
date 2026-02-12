```python
import pytest
from main import add, subtract, multiply, divide, Calculator

# Test add function
@pytest.mark.parametrize("num1, num2, expected", [
    (1, 2, 3),
    (-1, 2, 1),
    (1, -2, -1),
    (0, 0, 0),
    (1.5, 2.5, 4.0),
    (-1.5, 2.5, 1.0),
    (1.5, -2.5, -1.0),
])
def test_add(num1, num2, expected):
    assert add(num1, num2) == expected

def test_add_invalid_input():
    with pytest.raises(ValueError):
        add("a", 2)

# Test subtract function
@pytest.mark.parametrize("num1, num2, expected", [
    (1, 2, -1),
    (-1, 2, -3),
    (1, -2, 3),
    (0, 0, 0),
    (1.5, 2.5, -1.0),
    (-1.5, 2.5, -4.0),
    (1.5, -2.5, 4.0),
])
def test_subtract(num1, num2, expected):
    assert subtract(num1, num2) == expected

def test_subtract_invalid_input():
    with pytest.raises(ValueError):
        subtract("a", 2)

# Test multiply function
@pytest.mark.parametrize("num1, num2, expected", [
    (1, 2, 2),
    (-1, 2, -2),
    (1, -2, -2),
    (0, 0, 0),
    (1.5, 2.5, 3.75),
    (-1.5, 2.5, -3.75),
    (1.5, -2.5, -3.75),
])
def test_multiply(num1, num2, expected):
    assert multiply(num1, num2) == expected

def test_multiply_invalid_input():
    with pytest.raises(ValueError):
        multiply("a", 2)

# Test divide function
@pytest.mark.parametrize("num1, num2, expected", [
    (1, 2, 0.5),
    (-1, 2, -0.5),
    (1, -2, -0.5),
    (0, 1, 0),
    (1.5, 2.5, 0.6),
    (-1.5, 2.5, -0.6),
    (1.5, -2.5, -0.6),
])
def test_divide(num1, num2, expected):
    assert divide(num1, num2) == expected

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

def test_divide_invalid_input():
    with pytest.raises(ValueError):
        divide("a", 2)

# Test Calculator class
def test_calculator_init():
    calculator = Calculator()
    assert calculator is not None

@pytest.mark.parametrize("operation, num1, num2, expected", [
    ("+", 1, 2, 3),
    ("-", 1, 2, -1),
    ("*", 1, 2, 2),
    ("/", 1, 2, 0.5),
])
def test_calculator_calculate(operation, num1, num2, expected):
    calculator = Calculator()
    assert calculator.calculate(operation, num1, num2) == expected

def test_calculator_calculate_invalid_operation():
    calculator = Calculator()
    with pytest.raises(ValueError):
        calculator.calculate("^", 1, 2)

def test_calculator_calculate_invalid_input():
    calculator = Calculator()
    with pytest.raises(ValueError):
        calculator.calculate("+", "a", 2)

def test_calculator_calculate_divide_by_zero():
    calculator = Calculator()
    with pytest.raises(ZeroDivisionError):
        calculator.calculate("/", 1, 0)
```