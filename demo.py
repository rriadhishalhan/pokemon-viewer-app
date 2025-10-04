#!/usr/bin/env python3
"""
Demo script to test Pokemon Viewer functionality
"""

from pokemon_api import PokeAPIClient
from pokemon_service import PokemonService
from models import Pokemon
from rich.console import Console

def test_api_connection():
    """Test basic API connection"""
    console = Console()
    console.print("[bold blue]Testing API connection...[/bold blue]")
    
    client = PokeAPIClient()
    
    # Test basic Pokemon list
    result = client.get_pokemon_list(limit=5, offset=0)
    if result and result.get('results'):
        console.print("[green]✓ API connection successful[/green]")
        console.print(f"Found {result['count']} total Pokemon")
        return True
    else:
        console.print("[red]✗ API connection failed[/red]")
        return False

def test_pokemon_details():
    """Test Pokemon details fetching"""
    console = Console()
    console.print("[bold blue]Testing Pokemon details...[/bold blue]")
    
    client = PokeAPIClient()
    
    # Test with Pikachu
    details = client.get_pokemon_details("pikachu")
    if details:
        pokemon = Pokemon.from_api_response(details)
        console.print(f"[green]✓ Successfully loaded {pokemon.name}[/green]")
        console.print(f"  ID: {pokemon.id}")
        console.print(f"  Types: {', '.join(pokemon.types)}")
        console.print(f"  Height: {pokemon.get_height_meters():.1f}m")
        console.print(f"  Weight: {pokemon.get_weight_kg():.1f}kg")
        return True
    else:
        console.print("[red]✗ Failed to load Pokemon details[/red]")
        return False

def test_pagination():
    """Test pagination functionality"""
    console = Console()
    console.print("[bold blue]Testing pagination...[/bold blue]")
    
    service = PokemonService(page_size=3)
    
    try:
        pokemon_list, pagination_info = service.load_pokemon_page(offset=0)
        console.print(f"[green]✓ Loaded page with {len(pokemon_list)} Pokemon[/green]")
        console.print(f"  Page: {pagination_info.current_page}/{pagination_info.total_pages}")
        console.print(f"  Has next: {pagination_info.has_next}")
        console.print(f"  Has previous: {pagination_info.has_previous}")
        
        # Test next page
        if pagination_info.has_next:
            pokemon_list, pagination_info = service.load_next_page()
            console.print(f"[green]✓ Loaded next page with {len(pokemon_list)} Pokemon[/green]")
        
        return True
    except Exception as e:
        console.print(f"[red]✗ Pagination test failed: {e}[/red]")
        return False

def test_search():
    """Test search functionality"""
    console = Console()
    console.print("[bold blue]Testing search functionality...[/bold blue]")
    
    service = PokemonService()
    
    # Test search for popular Pokemon
    test_names = ["pikachu", "charizard", "blastoise"]
    
    for name in test_names:
        pokemon = service.search_pokemon(name)
        if pokemon:
            console.print(f"[green]✓ Found {pokemon.name} (ID: {pokemon.id})[/green]")
        else:
            console.print(f"[red]✗ Could not find {name}[/red]")
            return False
    
    return True

def main():
    """Run all tests"""
    console = Console()
    
    console.print(Panel(
        "[bold cyan]Pokemon Viewer Demo & Test Suite[/bold cyan]\n"
        "Testing core functionality...",
        border_style="blue"
    ))
    
    tests = [
        ("API Connection", test_api_connection),
        ("Pokemon Details", test_pokemon_details),
        ("Pagination", test_pagination),
        ("Search", test_search)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        console.print(f"\n[bold yellow]Running {test_name} test...[/bold yellow]")
        if test_func():
            passed += 1
        console.print()
    
    # Summary
    console.print(Panel(
        f"[bold]Test Results: {passed}/{total} tests passed[/bold]\n"
        f"{'[green]All tests passed! ✓[/green]' if passed == total else '[yellow]Some tests failed[/yellow]'}",
        border_style="green" if passed == total else "yellow"
    ))
    
    if passed == total:
        console.print("\n[bold green]🎉 Your Pokemon Viewer is ready to use![/bold green]")
        console.print("Run 'python main.py' to start the application.")
    else:
        console.print("\n[bold yellow]⚠️  Please check your internet connection and try again.[/bold yellow]")

if __name__ == "__main__":
    from rich.panel import Panel
    main()