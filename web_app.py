from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pokemon_service import PokemonService
from pokemon_api import PokeAPIClient
from models import Pokemon
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Pokemon service
pokemon_service = PokemonService(page_size=12)  # 12 for nice grid layout

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/api/pokemon')
def get_pokemon_list():
    """API endpoint to get paginated Pokemon list"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 12, type=int)
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Load Pokemon page
        pokemon_list, pagination_info = pokemon_service.load_pokemon_page(offset=offset)
        
        # Convert Pokemon objects to dictionaries
        pokemon_data = []
        for pokemon in pokemon_list:
            pokemon_dict = {
                'id': pokemon.id,
                'name': pokemon.name,
                'height': pokemon.get_height_meters(),
                'weight': pokemon.get_weight_kg(),
                'types': pokemon.types,
                'abilities': pokemon.abilities,
                'base_experience': pokemon.base_experience,
                'sprite_url': pokemon.sprite_url,
                'description': pokemon.description
            }
            pokemon_data.append(pokemon_dict)
        
        # Prepare response
        response = {
            'pokemon': pokemon_data,
            'pagination': {
                'current_page': pagination_info.current_page,
                'total_pages': pagination_info.total_pages,
                'has_next': pagination_info.has_next,
                'has_previous': pagination_info.has_previous,
                'total_count': pagination_info.count,
                'current_count': len(pokemon_data)
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error fetching Pokemon list: {e}")
        return jsonify({'error': 'Failed to fetch Pokemon list'}), 500

@app.route('/api/pokemon/<pokemon_name>')
def get_pokemon_details(pokemon_name):
    """API endpoint to get specific Pokemon details"""
    try:
        pokemon = pokemon_service.search_pokemon(pokemon_name)
        
        if pokemon:
            pokemon_dict = {
                'id': pokemon.id,
                'name': pokemon.name,
                'height': pokemon.get_height_meters(),
                'weight': pokemon.get_weight_kg(),
                'types': pokemon.types,
                'abilities': pokemon.abilities,
                'base_experience': pokemon.base_experience,
                'sprite_url': pokemon.sprite_url,
                'description': pokemon.description
            }
            return jsonify(pokemon_dict)
        else:
            return jsonify({'error': 'Pokemon not found'}), 404
            
    except Exception as e:
        logger.error(f"Error fetching Pokemon details for {pokemon_name}: {e}")
        return jsonify({'error': 'Failed to fetch Pokemon details'}), 500

@app.route('/api/search')
def search_pokemon():
    """API endpoint to search Pokemon"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        pokemon = pokemon_service.search_pokemon(query)
        
        if pokemon:
            pokemon_dict = {
                'id': pokemon.id,
                'name': pokemon.name,
                'height': pokemon.get_height_meters(),
                'weight': pokemon.get_weight_kg(),
                'types': pokemon.types,
                'abilities': pokemon.abilities,
                'base_experience': pokemon.base_experience,
                'sprite_url': pokemon.sprite_url,
                'description': pokemon.description
            }
            return jsonify({'pokemon': pokemon_dict, 'found': True})
        else:
            return jsonify({'found': False, 'message': f'Pokemon "{query}" not found'})
            
    except Exception as e:
        logger.error(f"Error searching for Pokemon: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎮 Starting Pokemon Viewer Web Application...")
    print("📱 Open your browser and navigate to: http://localhost:5000")
    print("🔄 The application will automatically load with lazy loading enabled")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)