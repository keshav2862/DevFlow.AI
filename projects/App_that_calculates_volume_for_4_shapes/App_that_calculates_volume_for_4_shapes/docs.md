# README.md

Shape Calculator
================

A Python module for calculating the volume and area of various shapes.

### Project Purpose

The Shape Calculator is a Python module designed to calculate the volume and area of various shapes, including cubes, spheres, cylinders, and cones. The module uses object-oriented programming to define classes for each shape, making it easy to extend and modify the code as needed.

### Installation and Usage

To use the Shape Calculator, simply clone the repository and run the `shape_calculator.py` file. Follow the prompts to choose a shape and enter its dimensions, and the module will calculate and display the volume and area.

### Example Usage

```
$ python shape_calculator.py
Shape Calculator
----------------
Choose a shape:
1. Cube
2. Sphere
3. Cylinder
4. Cone
Enter the number of your choice: 1
Enter the side length: 5
The volume of the Cube is: 125.0
The area of the Cube is: 150.0
```

### Dependencies

The Shape Calculator requires the `math` module, which is included in the Python standard library.

### Contributing

Contributions are welcome! If you'd like to add a new shape or improve the existing code, please submit a pull request.

---

# shape_calculator.py

```python
"""
Module for calculating the volume and area of various shapes.
"""

import math

class Shape:
    """
    Base class for shapes.

    Attributes:
        name (str): Name of the shape.
    """

    def __init__(self, name):
        """
        Initialize the shape.

        Args:
            name (str): Name of the shape.
        """
        self.name = name

    def calculate_volume(self):
        """
        Calculate the volume of the shape.

        Returns:
            float: Volume of the shape.
        """
        raise NotImplementedError("Subclass must implement this method")

    def calculate_area(self):
        """
        Calculate the area of the shape.

        Returns:
            float: Area of the shape.
        """
        raise NotImplementedError("Subclass must implement this method")


class Cube(Shape):
    """
    Class for calculating the volume and area of a cube.

    Attributes:
        side_length (float): Length of a side of the cube.
    """

    def __init__(self, side_length):
        """
        Initialize the cube.

        Args:
            side_length (float): Length of a side of the cube.
        """
        super().__init__("Cube")
        self.side_length = side_length

    def calculate_volume(self):
        """
        Calculate the volume of the cube.

        Returns:
            float: Volume of the cube.
        """
        return self.side_length ** 3

    def calculate_area(self):
        """
        Calculate the area of the cube.

        Returns:
            float: Area of the cube.
        """
        return 6 * (self.side_length ** 2)


class Sphere(Shape):
    """
    Class for calculating the volume and area of a sphere.

    Attributes:
        radius (float): Radius of the sphere.
    """

    def __init__(self, radius):
        """
        Initialize the sphere.

        Args:
            radius (float): Radius of the sphere.
        """
        super().__init__("Sphere")
        self.radius = radius

    def calculate_volume(self):
        """
        Calculate the volume of the sphere.

        Returns:
            float: Volume of the sphere.
        """
        return (4/3) * math.pi * (self.radius ** 3)

    def calculate_area(self):
        """
        Calculate the area of the sphere.

        Returns:
            float: Area of the sphere.
        """
        return 4 * math.pi * (self.radius ** 2)


class Cylinder(Shape):
    """
    Class for calculating the volume and area of a cylinder.

    Attributes:
        radius (float): Radius of the cylinder.
        height (float): Height of the cylinder.
    """

    def __init__(self, radius, height):
        """
        Initialize the cylinder.

        Args:
            radius (float): Radius of the cylinder.
            height (float): Height of the cylinder.
        """
        super().__init__("Cylinder")
        self.radius = radius
        self.height = height

    def calculate_volume(self):
        """
        Calculate the volume of the cylinder.

        Returns:
            float: Volume of the cylinder.
        """
        return math.pi * (self.radius ** 2) * self.height

    def calculate_area(self):
        """
        Calculate the area of the cylinder.

        Returns:
            float: Area of the cylinder.
        """
        return 2 * math.pi * self.radius * (self.radius + self.height)


class Cone(Shape):
    """
    Class for calculating the volume and area of a cone.

    Attributes:
        radius (float): Radius of the cone.
        height (float): Height of the cone.
    """

    def __init__(self, radius, height):
        """
        Initialize the cone.

        Args:
            radius (float): Radius of the cone.
            height (float): Height of the cone.
        """
        super().__init__("Cone")
        self.radius = radius
        self.height = height

    def calculate_volume(self):
        """
        Calculate the volume of the cone.

        Returns:
            float: Volume of the cone.
        """
        return (1/3) * math.pi * (self.radius ** 2) * self.height

    def calculate_area(self):
        """
        Calculate the area of the cone.

        Returns:
            float: Area of the cone.
        """
        return math.pi * self.radius * (self.radius + self.height)


def get_shape_class(shape_name):
    """
    Get the shape class based on the shape name.

    Args:
        shape_name (str): Name of the shape.

    Returns:
        class: Shape class.
    """
    shape_classes = {
        "cube": Cube,
        "sphere": Sphere,
        "cylinder": Cylinder,
        "cone": Cone
    }
    return shape_classes.get(shape_name.lower(), None)


def get_dimensions(shape_class):
    """
    Get the dimensions for the shape.

    Args:
        shape_class (class): Shape class.

    Returns:
        dict: Dimensions for the shape.
    """
    dimensions = {}
    if shape_class.__name__ == "Cube":
        dimensions["side_length"] = float(input("Enter the side length: "))
    elif shape_class.__name__ == "Sphere":
        dimensions["radius"] = float(input("Enter the radius: "))
    elif shape_class.__name__ == "Cylinder" or shape_class.__name__ == "Cone":
        dimensions["radius"] = float(input("Enter the radius: "))
        dimensions["height"] = float(input("Enter the height: "))
    return dimensions


def calculate_shape(shape_class, dimensions):
    """
    Calculate the volume and area of the shape.

    Args:
        shape_class (class): Shape class.
        dimensions (dict): Dimensions for the shape.

    Returns:
        tuple: Volume and area of the shape.
    """
    shape = shape_class(dimensions["side_length"] if shape_class.__name__ == "Cube" else dimensions["radius"] if shape_class.__name__ == "Sphere" else dimensions["radius"], dimensions["height"] if shape_class.__name__ == "Cylinder" or shape_class.__name__ == "Cone" else None)
    volume = shape.calculate_volume()
    area = shape.calculate_area()
    return volume, area


def main():
    """
    Main function for the shape calculator.

    Asks the user for the shape and its dimensions, and calculates and displays the volume and area.
    """
    try:
        print("Shape Calculator")
        print("----------------")

        while True:
            print("Choose a shape:")
            for i, shape in enumerate(["cube", "sphere", "cylinder", "cone"]):
                print(f"{i+1}. {shape.capitalize()}")
            choice = input("Enter the number of your choice: ")

            shape_class = get_shape_class(choice)
            if shape_class is None:
                print("Invalid choice. Please try again.")
                continue

            dimensions = get_dimensions(shape_class)
            volume, area = calculate_shape(shape_class, dimensions)
            print(f"The volume of the {shape_class.__name__} is: {volume}")
            print(f"The area of the {shape_class.__name__} is: {area}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
```