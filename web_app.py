from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pokemon_service import PokemonService
from pokemon_api import PokeAPIClient
from models import Pokemon
import logging
import random

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

@app.route('/battle')
def battle_page():
    """Battle simulator page route"""
    return render_template('battle.html')

@app.route('/api/pokemon-list')
def get_pokemon_names():
    """API endpoint to get a list of Pokemon names for dropdowns"""
    try:
        # Get first 151 Pokemon (original generation) for dropdown
        response = pokemon_service.api_client.get_pokemon_list(limit=151, offset=0)
        pokemon_names = [pokemon['name'] for pokemon in response.get('results', [])]
        return jsonify({'pokemon': pokemon_names})
    except Exception as e:
        logger.error(f"Error fetching Pokemon names: {e}")
        return jsonify({'error': 'Failed to fetch Pokemon names'}), 500

@app.route('/api/battle/pokemon/<pokemon_name>')
def get_battle_pokemon(pokemon_name):
    """API endpoint to get Pokemon battle stats"""
    try:
        pokemon_details = pokemon_service.api_client.get_pokemon_details(pokemon_name)
        if not pokemon_details:
            return jsonify({'error': 'Pokemon not found'}), 404
        
        # Extract stats for battle
        stats = {}
        for stat in pokemon_details.get('stats', []):
            stat_name = stat['stat']['name']
            stat_value = stat['base_stat']
            stats[stat_name] = stat_value
        
        battle_data = {
            'id': pokemon_details.get('id'),
            'name': pokemon_details.get('name', '').title(),
            'sprite_url': pokemon_details.get('sprites', {}).get('front_default'),
            'back_sprite_url': pokemon_details.get('sprites', {}).get('back_default'),
            'types': [type_info['type']['name'] for type_info in pokemon_details.get('types', [])],
            'stats': {
                'hp': stats.get('hp', 50),
                'attack': stats.get('attack', 50),
                'defense': stats.get('defense', 50),
                'speed': stats.get('speed', 50)
            }
        }
        
        return jsonify(battle_data)
        
    except Exception as e:
        logger.error(f"Error fetching battle Pokemon {pokemon_name}: {e}")
        return jsonify({'error': 'Failed to fetch Pokemon battle data'}), 500

@app.route('/api/battle/simulate', methods=['POST'])
def simulate_battle():
    """API endpoint to simulate a battle turn"""
    try:
        data = request.get_json()
        attacker = data.get('attacker')
        defender = data.get('defender')
        
        # Calculate damage: base_attack + random_factor - opponent_defense
        base_damage = attacker['stats']['attack']
        random_factor = random.randint(-5, 5)
        defense = defender['stats']['defense']
        damage = max(1, base_damage + random_factor - defense)  # Minimum 1 damage
        
        # Calculate new HP
        new_hp = max(0, defender['current_hp'] - damage)
        
        result = {
            'damage': damage,
            'new_hp': new_hp,
            'is_fainted': new_hp <= 0,
            'battle_log': f"{attacker['name']} used Tackle! It dealt {damage} damage to {defender['name']}!"
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error simulating battle: {e}")
        return jsonify({'error': 'Battle simulation failed'}), 500

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