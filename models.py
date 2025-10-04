from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Pokemon:
    """Data class representing a Pokemon"""
    id: int
    name: str
    height: int
    weight: int
    types: List[str]
    abilities: List[str]
    base_experience: int
    sprite_url: Optional[str] = None
    description: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict) -> 'Pokemon':
        """Create Pokemon instance from API response"""
        types = [type_info['type']['name'] for type_info in data.get('types', [])]
        abilities = [ability['ability']['name'] for ability in data.get('abilities', [])]
        
        sprite_url = None
        sprites = data.get('sprites', {})
        if sprites and sprites.get('front_default'):
            sprite_url = sprites['front_default']
        
        return cls(
            id=data.get('id', 0),
            name=data.get('name', '').title(),
            height=data.get('height', 0),
            weight=data.get('weight', 0),
            types=types,
            abilities=abilities,
            base_experience=data.get('base_experience', 0),
            sprite_url=sprite_url
        )
    
    def get_height_meters(self) -> float:
        """Convert height from decimeters to meters"""
        return self.height / 10.0
    
    def get_weight_kg(self) -> float:
        """Convert weight from hectograms to kilograms"""
        return self.weight / 10.0

@dataclass
class PaginationInfo:
    """Data class for pagination information"""
    count: int
    next_url: Optional[str]
    previous_url: Optional[str]
    current_offset: int
    current_limit: int
    
    @property
    def has_next(self) -> bool:
        return self.next_url is not None
    
    @property
    def has_previous(self) -> bool:
        return self.previous_url is not None
    
    @property
    def current_page(self) -> int:
        return (self.current_offset // self.current_limit) + 1
    
    @property
    def total_pages(self) -> int:
        return (self.count + self.current_limit - 1) // self.current_limit