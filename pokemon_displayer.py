from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from pokemon_service import PokemonService
from models import Pokemon, PaginationInfo
from typing import List, Optional
import os

class PokemonDisplayer:
    """Class for displaying Pokemon data in a beautiful console interface"""
    
    def __init__(self):
        self.console = Console()
        self.pokemon_service = PokemonService(page_size=10)  # Smaller page size for better UX
        
    def display_pokemon_list(self, pokemon_list: List[Pokemon], pagination_info: PaginationInfo):
        """Display a list of Pokemon in a formatted table"""
        
        if not pokemon_list:
            self.console.print("[yellow]No Pokemon found![/yellow]")
            return
        
        # Create main table
        table = Table(title=f"🎮 Pokemon List - Page {pagination_info.current_page} of {pagination_info.total_pages}")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Name", style="magenta", width=15)
        table.add_column("Types", style="green", width=20)
        table.add_column("Height", style="blue", width=8)
        table.add_column("Weight", style="red", width=8)
        table.add_column("Experience", style="yellow", width=10)
        
        for pokemon in pokemon_list:
            types_str = ", ".join([f"[bold]{t.title()}[/bold]" for t in pokemon.types])
            table.add_row(
                str(pokemon.id),
                pokemon.name,
                types_str,
                f"{pokemon.get_height_meters():.1f}m",
                f"{pokemon.get_weight_kg():.1f}kg",
                str(pokemon.base_experience)
            )
        
        self.console.print(table)
        
        # Display pagination info
        pagination_text = f"Showing {len(pokemon_list)} Pokemon (Total: {pagination_info.count})"
        if pagination_info.has_previous or pagination_info.has_next:
            navigation_options = []
            if pagination_info.has_previous:
                navigation_options.append("[bold green]P[/bold green]revious")
            if pagination_info.has_next:
                navigation_options.append("[bold green]N[/bold green]ext")
            pagination_text += f" | Navigation: {' | '.join(navigation_options)}"
        
        self.console.print(Panel(pagination_text, style="blue"))
    
    def display_pokemon_details(self, pokemon: Pokemon):
        """Display detailed information about a Pokemon"""
        
        # Create the main info panel
        info_lines = [
            f"[bold cyan]ID:[/bold cyan] {pokemon.id}",
            f"[bold cyan]Name:[/bold cyan] {pokemon.name}",
            f"[bold cyan]Height:[/bold cyan] {pokemon.get_height_meters():.1f} meters",
            f"[bold cyan]Weight:[/bold cyan] {pokemon.get_weight_kg():.1f} kg",
            f"[bold cyan]Base Experience:[/bold cyan] {pokemon.base_experience}",
        ]
        
        if pokemon.types:
            types_str = ", ".join([f"[bold green]{t.title()}[/bold green]" for t in pokemon.types])
            info_lines.append(f"[bold cyan]Types:[/bold cyan] {types_str}")
        
        if pokemon.abilities:
            abilities_str = ", ".join([f"[bold yellow]{a.title()}[/bold yellow]" for a in pokemon.abilities])
            info_lines.append(f"[bold cyan]Abilities:[/bold cyan] {abilities_str}")
        
        if pokemon.description:
            info_lines.append(f"[bold cyan]Description:[/bold cyan] {pokemon.description}")
        
        if pokemon.sprite_url:
            info_lines.append(f"[bold cyan]Sprite URL:[/bold cyan] {pokemon.sprite_url}")
        
        info_text = "\n".join(info_lines)
        
        self.console.print(Panel(
            info_text,
            title=f"🎯 {pokemon.name} Details",
            border_style="green"
        ))
    
    def show_menu(self):
        """Display the main menu"""
        menu_text = """
[bold blue]🎮 Pokemon Viewer Menu[/bold blue]

[bold green]1.[/bold green] Browse Pokemon List (with lazy loading)
[bold green]2.[/bold green] Search for a specific Pokemon
[bold green]3.[/bold green] Exit

Choose an option (1-3):
        """
        
        self.console.print(Panel(menu_text, border_style="blue"))
    
    def browse_pokemon(self):
        """Browse Pokemon with lazy loading and pagination"""
        self.console.print("\n[bold blue]🔄 Loading Pokemon...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Fetching Pokemon data...", total=None)
            
            try:
                pokemon_list, pagination_info = self.pokemon_service.load_pokemon_page(offset=0)
                progress.update(task, completed=100)
            except Exception as e:
                self.console.print(f"[bold red]Error loading Pokemon: {e}[/bold red]")
                return
        
        while True:
            self.console.clear()
            self.display_pokemon_list(pokemon_list, pagination_info)
            
            # Show options
            options = []
            if pagination_info.has_previous:
                options.append("[bold]P[/bold] - Previous page")
            if pagination_info.has_next:
                options.append("[bold]N[/bold] - Next page")
            options.append("[bold]D[/bold] - View Pokemon details")
            options.append("[bold]B[/bold] - Back to main menu")
            
            self.console.print(f"\nOptions: {' | '.join(options)}")
            
            choice = Prompt.ask("Enter your choice").lower()
            
            if choice == 'p' and pagination_info.has_previous:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Loading previous page...", total=None)
                    pokemon_list, pagination_info = self.pokemon_service.load_previous_page()
                    
            elif choice == 'n' and pagination_info.has_next:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Loading next page...", total=None)
                    pokemon_list, pagination_info = self.pokemon_service.load_next_page()
                    
            elif choice == 'd':
                try:
                    pokemon_id = IntPrompt.ask("Enter Pokemon ID to view details")
                    pokemon = next((p for p in pokemon_list if p.id == pokemon_id), None)
                    if pokemon:
                        self.console.clear()
                        self.display_pokemon_details(pokemon)
                        Prompt.ask("\nPress Enter to continue")
                    else:
                        self.console.print("[bold red]Pokemon not found in current page![/bold red]")
                        Prompt.ask("Press Enter to continue")
                except ValueError:
                    self.console.print("[bold red]Please enter a valid number![/bold red]")
                    Prompt.ask("Press Enter to continue")
                    
            elif choice == 'b':
                break
            else:
                self.console.print("[bold red]Invalid choice![/bold red]")
                Prompt.ask("Press Enter to continue")
    
    def search_pokemon(self):
        """Search for a specific Pokemon"""
        pokemon_name = Prompt.ask("\nEnter Pokemon name to search")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Searching for {pokemon_name}...", total=None)
            pokemon = self.pokemon_service.search_pokemon(pokemon_name)
        
        if pokemon:
            self.console.clear()
            self.display_pokemon_details(pokemon)
        else:
            self.console.print(f"[bold red]Pokemon '{pokemon_name}' not found![/bold red]")
        
        Prompt.ask("\nPress Enter to continue")
    
    def run(self):
        """Main application loop"""
        self.console.print(Panel(
            "[bold blue]🎮 Welcome to Pokemon Viewer![/bold blue]\n"
            "Browse and search Pokemon using the PokeAPI with lazy loading",
            border_style="green"
        ))
        
        while True:
            self.show_menu()
            
            try:
                choice = IntPrompt.ask("Enter your choice")
                
                if choice == 1:
                    self.browse_pokemon()
                elif choice == 2:
                    self.search_pokemon()
                elif choice == 3:
                    self.console.print("\n[bold green]Thanks for using Pokemon Viewer! 👋[/bold green]")
                    break
                else:
                    self.console.print("[bold red]Invalid choice! Please enter 1, 2, or 3.[/bold red]")
                    Prompt.ask("Press Enter to continue")
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[bold yellow]Goodbye! 👋[/bold yellow]")
                break
            except Exception as e:
                self.console.print(f"[bold red]An error occurred: {e}[/bold red]")
                Prompt.ask("Press Enter to continue")