from enum import Enum

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    ORANGE = 'orange'
    PURPLE = 'purple'
    GRAY = 'gray'
    BLACK = 'black'
    YELLOW = 'yellow'
    # Add more as needed

    def __str__(self):
        return self.value  # So we can safely pass it to matplotlib
