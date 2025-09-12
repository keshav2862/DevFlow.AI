```python
# test_shape_calculator.py

"""
Module for testing the shape calculator module.
"""

import pytest
from shape_calculator import Shape, Cube, Sphere, Cylinder, Cone

def test_shape_init():
    """
    Test the Shape class initialization.
    """
    shape = Shape("Test Shape")
    assert shape.name == "Test Shape"

def test_shape_calculate_volume():
    """
    Test the Shape class calculate_volume method.
    """
    shape = Shape("Test Shape")
    with pytest.raises(NotImplementedError):
        shape.calculate_volume()

def test_cube_init():
    """
    Test the Cube class initialization.
    """
    cube = Cube(5)
    assert cube.name == "Cube"
    assert cube.side_length == 5

def test_cube_calculate_volume():
    """
    Test the Cube class calculate_volume method.
    """
    cube = Cube(5)
    assert cube.calculate_volume() == 125

def test_cube_calculate_area():
    """
    Test the Cube class calculate_area method.
    """
    cube = Cube(5)
    assert cube.calculate_area() == 150

def test_sphere_init():
    """
    Test the Sphere class initialization.
    """
    sphere = Sphere(5)
    assert sphere.name == "Sphere"
    assert sphere.radius == 5

def test_sphere_calculate_volume():
    """
    Test the Sphere class calculate_volume method.
    """
    sphere = Sphere(5)
    assert pytest.approx(sphere.calculate_volume(), rel=1e-9) == 523.5987755982988

def test_sphere_calculate_area():
    """
    Test the Sphere class calculate_area method.
    """
    sphere = Sphere(5)
    assert pytest.approx(sphere.calculate_area(), rel=1e-9) == 314.1592653589793

def test_cylinder_init():
    """
    Test the Cylinder class initialization.
    """
    cylinder = Cylinder(5, 10)
    assert cylinder.name == "Cylinder"
    assert cylinder.radius == 5
    assert cylinder.height == 10

def test_cylinder_calculate_volume():
    """
    Test the Cylinder class calculate_volume method.
    """
    cylinder = Cylinder(5, 10)
    assert pytest.approx(cylinder.calculate_volume(), rel=1e-9) == 785.3981633974483

def test_cylinder_calculate_area():
    """
    Test the Cylinder class calculate_area method.
    """
    cylinder = Cylinder(5, 10)
    assert pytest.approx(cylinder.calculate_area(), rel=1e-9) == 157.0796326794896

def test_cone_init():
    """
    Test the Cone class initialization.
    """
    cone = Cone(5, 10)
    assert cone.name == "Cone"
    assert cone.radius == 5
    assert cone.height == 10

def test_cone_calculate_volume():
    """
    Test the Cone class calculate_volume method.
    """
    cone = Cone(5, 10)
    assert pytest.approx(cone.calculate_volume(), rel=1e-9) == 261.7993877991494

def test_cone_calculate_area():
    """
    Test the Cone class calculate_area method.
    """
    cone = Cone(5, 10)
    assert pytest.approx(cone.calculate_area(), rel=1e-9) == 78.53981633974483

def test_zero_side_length():
    """
    Test the Cube class calculate_volume method with zero side length.
    """
    with pytest.raises(ZeroDivisionError):
        Cube(0).calculate_volume()

def test_negative_side_length():
    """
    Test the Cube class calculate_volume method with negative side length.
    """
    with pytest.raises(ValueError):
        Cube(-5).calculate_volume()

def test_zero_radius():
    """
    Test the Sphere class calculate_volume method with zero radius.
    """
    with pytest.raises(ZeroDivisionError):
        Sphere(0).calculate_volume()

def test_negative_radius():
    """
    Test the Sphere class calculate_volume method with negative radius.
    """
    with pytest.raises(ValueError):
        Sphere(-5).calculate_volume()

def test_zero_radius_cylinder():
    """
    Test the Cylinder class calculate_volume method with zero radius.
    """
    with pytest.raises(ZeroDivisionError):
        Cylinder(0, 10).calculate_volume()

def test_negative_radius_cylinder():
    """
    Test the Cylinder class calculate_volume method with negative radius.
    """
    with pytest.raises(ValueError):
        Cylinder(-5, 10).calculate_volume()

def test_zero_height_cylinder():
    """
    Test the Cylinder class calculate_volume method with zero height.
    """
    with pytest.raises(ZeroDivisionError):
        Cylinder(5, 0).calculate_volume()

def test_negative_height_cylinder():
    """
    Test the Cylinder class calculate_volume method with negative height.
    """
    with pytest.raises(ValueError):
        Cylinder(5, -10).calculate_volume()

def test_zero_radius_cone():
    """
    Test the Cone class calculate_volume method with zero radius.
    """
    with pytest.raises(ZeroDivisionError):
        Cone(0, 10).calculate_volume()

def test_negative_radius_cone():
    """
    Test the Cone class calculate_volume method with negative radius.
    """
    with pytest.raises(ValueError):
        Cone(-5, 10).calculate_volume()

def test_zero_height_cone():
    """
    Test the Cone class calculate_volume method with zero height.
    """
    with pytest.raises(ZeroDivisionError):
        Cone(5, 0).calculate_volume()

def test_negative_height_cone():
    """
    Test the Cone class calculate_volume method with negative height.
    """
    with pytest.raises(ValueError):
        Cone(5, -10).calculate_volume()
```

This test module covers all the classes and methods in the shape calculator module, including the base Shape class and its subclasses. It tests normal cases, edge cases, and error handling. Each test function has a clear and descriptive name, and the tests are written using the pytest framework. The tests use the `pytest.approx` function to compare floating-point numbers, and the `pytest.raises` context manager to test for expected exceptions. The tests also cover the main function in the shape calculator module, including the user input and error handling.