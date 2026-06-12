"""
Entity for text formating and color console output
"""

from typing import Final

dark_link_color: Final[str] = '#6cb4ee'
builtin_colors_light: Final[dict[str, str]] = {
    'yellow': '#ffeb6b',
    'green': '#c0ed72',
    'blue': '#add8ff',
    'red': '#ffb0ca',
    'purple': '#d9b2ff',
}
builtin_colors_dark: Final[dict[str, str]] = {
    'yellow': '#906e00',
    'green': '#306f50',
    'blue': '#265589',
    'red': '#a23e5a',
    'purple': '#505088',
}

builtin_decorations: Final[dict] = {
    'wavy': {
        'text-decoration-style': 'wavy',
        'text-decoration-color': 'red',
        'text-decoration-line': 'underline'
    },
    'strikeout': {'text-decoration-line': 'line-through', 'text-decoration-color': 'red'},
}


class Format:
    """
    Utility class for text formater
    Includes print functions in different colors and underline technology.
    """
    underline_end: Final[str] = '\033[0m'
    underline_start: Final[str] = '\033[4m'

    @staticmethod
    def prRed(string: str):
        print("\033[91m {}\033[00m".format(string))

    @staticmethod
    def prGreen(string: str):
        print("\033[92m {}\033[00m".format(string))

    @staticmethod
    def prYellow(string: str):
        print("\033[93m {}\033[00m".format(string))

    @staticmethod
    def prCyan(string: str):
        print("\033[96m {}\033[00m".format(string))

    @staticmethod
    def prLightGray(string: str):
        print("\033[97m {}\033[00m".format(string))
