import requests
import json
from typing import Dict, List, Optional
import time

class PokeAPIClient:
    """Client for interacting with the PokeAPI"""
    
    def __init__(self, base_url: str = "https://pokeapi.co/api/v2"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def get_pokemon_list(self, limit: int = 20, offset: int = 0) -> Dict:
        """
        Get a paginated list of Pokemon
        
        Args:
            limit: Number of Pokemon to fetch (default: 20)
            offset: Starting position (default: 0)
            
        Returns:
            Dict containing Pokemon list and pagination info
        """
        url = f"{self.base_url}/pokemon"
        params = {"limit": limit, "offset": offset}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching Pokemon list: {e}")
            return {"results": [], "count": 0, "next": None, "previous": None}
    
    def get_pokemon_details(self, pokemon_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific Pokemon
        
        Args:
            pokemon_name: Name or ID of the Pokemon
            
        Returns:
            Dict containing Pokemon details or None if not found
        """
        url = f"{self.base_url}/pokemon/{pokemon_name.lower()}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching Pokemon details for {pokemon_name}: {e}")
            return None
    
    def get_pokemon_species(self, pokemon_id: int) -> Optional[Dict]:
        """
        Get Pokemon species information for description
        
        Args:
            pokemon_id: ID of the Pokemon
            
        Returns:
            Dict containing species information or None if not found
        """
        url = f"{self.base_url}/pokemon-species/{pokemon_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching Pokemon species for ID {pokemon_id}: {e}")
            return None