# Pokemon Viewer App - AI Coding Instructions

## Architecture Overview

This is a dual-interface Pokemon application with **strict separation of concerns**:

- **API Layer**: `pokemon_api.py` - Raw PokeAPI HTTP client with session reuse
- **Service Layer**: `pokemon_service.py` - Business logic, lazy loading, and caching 
- **Display Layers**: `pokemon_displayer.py` (console) + `web_app.py` (web) - Interface-specific presentation
- **Models**: `models.py` - Dataclasses with API response conversion methods

## Critical Patterns

### Lazy Loading Implementation
The app uses **pagination-based lazy loading** to avoid overwhelming the PokeAPI:
- Console: 10 Pokemon per page via `PokemonService(page_size=10)`
- Web: 12 Pokemon per page for grid layout via `PokemonService(page_size=12)`
- **Always include 0.1s delay** between detailed API requests in service layer
- Use `offset` calculation: `(page - 1) * limit` for API pagination

### Data Flow Pattern
```
PokeAPIClient → PokemonService → Interface Layer
     ↓              ↓                ↓
Raw HTTP      Business Logic    Display Logic
```

### API Response Handling
- Use `Pokemon.from_api_response(data)` for standardized model creation
- **Always fetch species data separately** for Pokemon descriptions
- Filter English descriptions: `entry['language']['name'] == 'en'`
- Handle metric conversions: height (decimeters→meters), weight (hectograms→kg)

## Development Workflows

### Running the Application
```bash
# Web interface (recommended)
python web_app.py  # or run_web.bat on Windows

# Console interface  
python main.py     # or run.bat on Windows
```

### Configuration Changes
All settings centralized in `config.py`:
- API timeouts and delays
- Page sizes and display settings
- Cache configuration

### Adding New Features
1. **API changes**: Modify `PokeAPIClient` methods
2. **Business logic**: Update `PokemonService` 
3. **Data models**: Extend `models.py` dataclasses
4. **UI changes**: Update both `pokemon_displayer.py` AND `web_app.py`

## Web Interface Specifics

### Flask API Endpoints
- `GET /api/pokemon?page={page}&limit={limit}` - Paginated list
- `GET /api/pokemon/{name}` - Specific Pokemon details  
- `GET /api/search?q={query}` - Search functionality

### Frontend Architecture (`static/js/app.js`)
- Class-based structure: `PokemonViewer` with modal handling
- AJAX-based pagination and search
- Progressive enhancement with service worker (`sw.js`)

## Console Interface Specifics

### Rich Library Usage
- Use `Table` for Pokemon lists with consistent column widths
- Use `Panel` for detailed views and menus
- Use `Progress` with `SpinnerColumn` for loading states
- Handle keyboard interrupts gracefully with try/catch

### Navigation Pattern
- Menu-driven with numbered choices
- Letter-based shortcuts in browse mode (P/N/D/B)
- Always provide "Press Enter to continue" for user acknowledgment

## Error Handling Conventions

- API errors: Return `None` or empty lists, log errors to console
- Network timeouts: 10-second timeout on all requests
- User input: Validate and re-prompt rather than crashing
- Graceful degradation: App continues working with partial data

## Testing & Debugging

- Use `demo.py` for quick functionality testing
- Check `run.bat` includes demo execution before main app
- Web app runs with `debug=True` for development
- Console app uses Rich's built-in error formatting