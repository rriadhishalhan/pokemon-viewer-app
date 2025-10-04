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
        
        # Get moves for special attacks
        moves = []
        for move_data in pokemon_details.get('moves', [])[:4]:  # Get first 4 moves
            move_name = move_data['move']['name']
            moves.append(move_name)
        
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
                'special-attack': stats.get('special-attack', 50),
                'special-defense': stats.get('special-defense', 50),
                'speed': stats.get('speed', 50)
            },
            'moves': moves,
            'defend_active': False,
            'attack_multiplier': 1.0,
            'defense_multiplier': 1.0
        }
        
        return jsonify(battle_data)
        
    except Exception as e:
        logger.error(f"Error fetching battle Pokemon {pokemon_name}: {e}")
        return jsonify({'error': 'Failed to fetch Pokemon battle data'}), 500

@app.route('/api/battle/computer-action', methods=['POST'])
def get_computer_action():
    """API endpoint to get computer's action choice"""
    try:
        data = request.get_json()
        computer_pokemon = data.get('computer_pokemon')
        player_pokemon = data.get('player_pokemon')
        
        # Calculate HP percentages for decision making
        computer_hp_percent = computer_pokemon['current_hp'] / computer_pokemon['max_hp']
        player_hp_percent = player_pokemon['current_hp'] / player_pokemon['max_hp']
        
        # AI decision logic with weights
        action_weights = {}
        
        # Always can attack
        action_weights['attack'] = 40
        
        # Heal if low on HP (below 35%)
        if computer_hp_percent < 0.35:
            action_weights['heal'] = 50
        else:
            action_weights['heal'] = 10
            
        # Defend if player has high attack stats or computer is low on HP
        player_attack = player_pokemon['stats']['attack']
        if player_attack > computer_pokemon['stats']['defense'] or computer_hp_percent < 0.25:
            action_weights['defend'] = 30
        else:
            action_weights['defend'] = 15
            
        # Special move if computer has good special attack
        if computer_pokemon['stats']['special-attack'] > computer_pokemon['stats']['attack']:
            action_weights['special'] = 35
        else:
            action_weights['special'] = 25
            
        # Don't heal if already at high HP
        if computer_hp_percent > 0.8:
            action_weights['heal'] = 5
            
        # Choose action based on weights
        actions = list(action_weights.keys())
        weights = list(action_weights.values())
        
        chosen_action = random.choices(actions, weights=weights, k=1)[0]
        
        # Generate action description
        action_descriptions = {
            'attack': "The opponent is preparing to attack!",
            'defend': "The opponent is taking a defensive stance!",
            'heal': "The opponent is focusing to recover!",
            'special': "The opponent is charging up a special move!"
        }
        
        return jsonify({
            'action': chosen_action,
            'description': action_descriptions[chosen_action]
        })
        
    except Exception as e:
        logger.error(f"Error getting computer action: {e}")
        return jsonify({'action': 'attack', 'description': 'The opponent attacks!'}), 500

@app.route('/api/battle/simulate', methods=['POST'])
def simulate_battle():
    """API endpoint to simulate a battle turn with different actions"""
    try:
        data = request.get_json()
        action = data.get('action', 'attack')
        attacker = data.get('attacker')
        defender = data.get('defender')
        
        result = {}
        
        if action == 'attack':
            # Standard attack action
            base_damage = attacker['stats']['attack'] * attacker.get('attack_multiplier', 1.0)
            random_factor = random.randint(-5, 5)
            defense = defender['stats']['defense'] * defender.get('defense_multiplier', 1.0)
            
            # Apply defend reduction if defender is defending
            damage = max(1, int(base_damage + random_factor - defense))
            if defender.get('defend_active', False):
                damage = int(damage * 0.5)
                result['defend_blocked'] = True
            
            new_hp = max(0, defender['current_hp'] - damage)
            
            result = {
                'action': 'attack',
                'damage': damage,
                'new_hp': new_hp,
                'is_fainted': new_hp <= 0,
                'battle_log': f"{attacker['name']} used Tackle! It dealt {damage} damage to {defender['name']}!"
            }
            
        elif action == 'defend':
            # Defend action - sets up damage reduction for next turn
            result = {
                'action': 'defend',
                'damage': 0,
                'new_hp': defender['current_hp'],
                'is_fainted': False,
                'defend_active': True,
                'battle_log': f"{attacker['name']} is defending! Incoming damage will be reduced next turn."
            }
            
        elif action == 'heal':
            # Heal action - restore 20% of max HP
            heal_amount = int(attacker['max_hp'] * 0.2)
            new_hp = min(attacker['max_hp'], attacker['current_hp'] + heal_amount)
            actual_heal = new_hp - attacker['current_hp']
            
            result = {
                'action': 'heal',
                'damage': 0,
                'heal_amount': actual_heal,
                'new_hp': new_hp,
                'is_fainted': False,
                'battle_log': f"{attacker['name']} used Heal! Restored {actual_heal} HP."
            }
            
        elif action == 'special':
            # Special move - enhanced damage using special attack
            base_damage = attacker['stats']['special-attack'] * attacker.get('attack_multiplier', 1.0)
            random_factor = random.randint(-3, 8)  # Higher variance for special moves
            defense = defender['stats']['special-defense'] * defender.get('defense_multiplier', 1.0)
            
            # Special moves do 1.3x damage
            damage = max(1, int((base_damage + random_factor - defense) * 1.3))
            if defender.get('defend_active', False):
                damage = int(damage * 0.5)
                result['defend_blocked'] = True
            
            new_hp = max(0, defender['current_hp'] - damage)
            
            # Get a random move name if available
            move_name = "Special Attack"
            if attacker.get('moves') and len(attacker['moves']) > 0:
                move_name = attacker['moves'][random.randint(0, len(attacker['moves']) - 1)].replace('-', ' ').title()
            
            result = {
                'action': 'special',
                'damage': damage,
                'new_hp': new_hp,
                'is_fainted': new_hp <= 0,
                'move_name': move_name,
                'battle_log': f"{attacker['name']} used {move_name}! It dealt {damage} damage to {defender['name']}!"
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