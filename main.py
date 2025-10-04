#!/usr/bin/env python3
"""
Pokemon Viewer Application

A Python application that consumes the PokeAPI to display Pokemon
in a list with lazy loading functionality.

Author: Pokemon Viewer
Date: 2025
"""

from pokemon_displayer import PokemonDisplayer
import sys

def main():
    """Main entry point of the application"""
    try:
        app = PokemonDisplayer()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()