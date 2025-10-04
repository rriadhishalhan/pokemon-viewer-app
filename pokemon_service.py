from pokemon_api import PokeAPIClient
from models import Pokemon, PaginationInfo
from typing import List, Tuple, Optional
import time

class PokemonService:
    """Service class for managing Pokemon data with lazy loading"""
    
    def __init__(self, page_size: int = 20):
        self.api_client = PokeAPIClient()
        self.page_size = page_size
        self.cached_pokemon: List[Pokemon] = []
        self.pagination_info: Optional[PaginationInfo] = None
        self.current_offset = 0
        
    def load_pokemon_page(self, offset: int = None) -> Tuple[List[Pokemon], PaginationInfo]:
        """
        Load a page of Pokemon with lazy loading
        
        Args:
            offset: Starting position (if None, uses current offset)
            
        Returns:
            Tuple of (Pokemon list, pagination info)
        """
        if offset is not None:
            self.current_offset = offset
        
        print(f"Loading Pokemon page at offset {self.current_offset}...")
        
        # Get Pokemon list from API
        response = self.api_client.get_pokemon_list(
            limit=self.page_size,
            offset=self.current_offset
        )
        
        # Create pagination info
        self.pagination_info = PaginationInfo(
            count=response.get('count', 0),
            next_url=response.get('next'),
            previous_url=response.get('previous'),
            current_offset=self.current_offset,
            current_limit=self.page_size
        )
        
        # Load Pokemon details for this page
        pokemon_list = []
        for pokemon_basic in response.get('results', []):
            pokemon_name = pokemon_basic['name']
            
            # Get detailed Pokemon data
            pokemon_details = self.api_client.get_pokemon_details(pokemon_name)
            if pokemon_details:
                pokemon = Pokemon.from_api_response(pokemon_details)
                
                # Get description from species endpoint
                species_data = self.api_client.get_pokemon_species(pokemon.id)
                if species_data and species_data.get('flavor_text_entries'):
                    # Get English description
                    for entry in species_data['flavor_text_entries']:
                        if entry['language']['name'] == 'en':
                            pokemon.description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                            break
                
                pokemon_list.append(pokemon)
            
            # Small delay to be respectful to the API
            time.sleep(0.1)
        
        return pokemon_list, self.pagination_info
    
    def load_next_page(self) -> Tuple[List[Pokemon], PaginationInfo]:
        """Load the next page of Pokemon"""
        if self.pagination_info and self.pagination_info.has_next:
            self.current_offset += self.page_size
            return self.load_pokemon_page()
        else:
            return [], self.pagination_info
    
    def load_previous_page(self) -> Tuple[List[Pokemon], PaginationInfo]:
        """Load the previous page of Pokemon"""
        if self.pagination_info and self.pagination_info.has_previous:
            self.current_offset = max(0, self.current_offset - self.page_size)
            return self.load_pokemon_page()
        else:
            return [], self.pagination_info
    
    def search_pokemon(self, name: str) -> Optional[Pokemon]:
        """
        Search for a specific Pokemon by name
        
        Args:
            name: Pokemon name to search for
            
        Returns:
            Pokemon object if found, None otherwise
        """
        print(f"Searching for Pokemon: {name}")
        
        pokemon_details = self.api_client.get_pokemon_details(name)
        if pokemon_details:
            pokemon = Pokemon.from_api_response(pokemon_details)
            
            # Get description
            species_data = self.api_client.get_pokemon_species(pokemon.id)
            if species_data and species_data.get('flavor_text_entries'):
                for entry in species_data['flavor_text_entries']:
                    if entry['language']['name'] == 'en':
                        pokemon.description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                        break
            
            return pokemon
        
        return None