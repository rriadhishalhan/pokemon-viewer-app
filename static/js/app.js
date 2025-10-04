// Pokemon Viewer JavaScript Application
class PokemonViewer {
    constructor() {
        this.currentPage = 1;
        this.isLoading = false;
        this.battleState = {
            pokemon1: null,
            pokemon2: null,
            currentTurn: 1, // Always start with player 1
            isActive: false,
            pokemonList: []
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadPokemonPage(1);
        this.loadPokemonList();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(link.dataset.section);
            });
        });

        // Pagination
        document.getElementById('prev-btn').addEventListener('click', () => {
            this.previousPage();
        });

        document.getElementById('next-btn').addEventListener('click', () => {
            this.nextPage();
        });

        // Search
        document.getElementById('search-btn').addEventListener('click', () => {
            this.searchPokemon();
        });

        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchPokemon();
            }
        });

        // Modal
        document.getElementById('pokemon-modal').addEventListener('click', (e) => {
            if (e.target.id === 'pokemon-modal' || e.target.classList.contains('modal-close')) {
                this.closeModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });

        // Battle event listeners
        document.getElementById('pokemon1-select')?.addEventListener('change', (e) => {
            this.loadBattlePokemon(e.target.value, 1);
        });

        document.getElementById('random-opponent-btn')?.addEventListener('click', () => {
            this.generateRandomOpponent();
        });

        document.getElementById('start-battle-btn')?.addEventListener('click', () => {
            this.startBattle();
        });

        document.getElementById('attack-btn')?.addEventListener('click', () => {
            this.performPlayerAttack();
        });

        document.getElementById('new-battle-btn')?.addEventListener('click', () => {
            this.resetBattle();
        });
    }

    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');
    }

    async loadPokemonPage(page = 1) {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showSkeletonLoading();

        try {
            const response = await fetch(`/api/pokemon?page=${page}&limit=12`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            this.currentPage = page;
            this.renderPokemonGrid(data.pokemon);
            this.updatePagination(data.pagination);
            this.hideLoading();

        } catch (error) {
            console.error('Error loading Pokemon:', error);
            this.showError('Failed to load Pokemon. Please try again.');
        } finally {
            this.isLoading = false;
        }
    }

    showSkeletonLoading() {
        const grid = document.getElementById('pokemon-grid');
        grid.innerHTML = '';
        
        // Create 12 skeleton cards (same as page size)
        for (let i = 0; i < 12; i++) {
            const skeletonCard = this.createSkeletonCard();
            grid.appendChild(skeletonCard);
        }
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('pokemon-grid').style.display = 'grid';
        document.getElementById('pagination').style.display = 'flex';
    }

    createSkeletonCard() {
        const card = document.createElement('div');
        card.className = 'skeleton-card';
        
        // Randomize number of type badges (1-2)
        const typeCount = Math.random() > 0.3 ? 2 : 1;
        const typeBadges = Array(typeCount).fill(0).map(() => 
            '<div class="skeleton skeleton-type"></div>'
        ).join('');
        
        card.innerHTML = `
            <div class="skeleton-header">
                <div class="skeleton skeleton-id"></div>
                <div class="skeleton skeleton-name"></div>
            </div>
            <div class="skeleton-image skeleton"></div>
            <div class="skeleton-types">
                ${typeBadges}
            </div>
            <div class="skeleton-stats">
                <div class="skeleton-stat-row">
                    <div class="skeleton skeleton-stat-label"></div>
                    <div class="skeleton skeleton-stat-value"></div>
                </div>
                <div class="skeleton-stat-row">
                    <div class="skeleton skeleton-stat-label"></div>
                    <div class="skeleton skeleton-stat-value"></div>
                </div>
                <div class="skeleton-stat-row">
                    <div class="skeleton skeleton-stat-label"></div>
                    <div class="skeleton skeleton-stat-value"></div>
                </div>
                <div class="skeleton-stat-row">
                    <div class="skeleton skeleton-stat-label"></div>
                    <div class="skeleton skeleton-stat-value"></div>
                </div>
            </div>
        `;
        
        return card;
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('pokemon-grid').style.display = 'none';
        document.getElementById('pagination').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('pokemon-grid').style.display = 'grid';
        document.getElementById('pagination').style.display = 'flex';
    }

    renderPokemonGrid(pokemonList) {
        const grid = document.getElementById('pokemon-grid');
        grid.innerHTML = '';

        pokemonList.forEach(pokemon => {
            const card = this.createPokemonCard(pokemon);
            grid.appendChild(card);
        });
    }

    createPokemonCard(pokemon) {
        const card = document.createElement('div');
        card.className = 'pokemon-card';
        card.onclick = () => this.showPokemonDetails(pokemon);

        const typeBadges = pokemon.types.map(type => 
            `<span class="type-badge type-${type}">${type}</span>`
        ).join('');

        card.innerHTML = `
            <div class="pokemon-header">
                <span class="pokemon-id">#${pokemon.id.toString().padStart(3, '0')}</span>
                <h3 class="pokemon-name">${pokemon.name}</h3>
            </div>
            <div class="pokemon-image">
                <img src="${pokemon.sprite_url || '/static/images/pokeball.png'}" 
                     alt="${pokemon.name}" 
                     onerror="this.src='/static/images/pokeball.png'">
            </div>
            <div class="pokemon-types">
                ${typeBadges}
            </div>
            <div class="pokemon-stats">
                <div class="stat-item">
                    <span class="stat-label">Height:</span>
                    <span class="stat-value">${pokemon.height.toFixed(1)}m</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Weight:</span>
                    <span class="stat-value">${pokemon.weight.toFixed(1)}kg</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Experience:</span>
                    <span class="stat-value">${pokemon.base_experience}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Abilities:</span>
                    <span class="stat-value">${pokemon.abilities.length}</span>
                </div>
            </div>
        `;

        return card;
    }

    updatePagination(pagination) {
        const pageInfo = document.getElementById('page-info');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        pageInfo.textContent = `Page ${pagination.current_page} of ${pagination.total_pages}`;
        
        prevBtn.disabled = !pagination.has_previous;
        nextBtn.disabled = !pagination.has_next;
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.loadPokemonPage(this.currentPage - 1);
        }
    }

    nextPage() {
        this.loadPokemonPage(this.currentPage + 1);
    }

    async searchPokemon() {
        const searchInput = document.getElementById('search-input');
        const query = searchInput.value.trim();

        if (!query) {
            this.showSearchMessage('Please enter a Pokemon name to search.');
            return;
        }

        this.showSearchLoading();

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.found) {
                this.renderSearchResult(data.pokemon);
            } else {
                this.showSearchMessage(data.message);
            }

        } catch (error) {
            console.error('Search error:', error);
            this.showSearchMessage('Search failed. Please try again.');
        }
    }

    showSearchLoading() {
        const resultsDiv = document.getElementById('search-results');
        const skeletonCard = this.createSkeletonCard();
        skeletonCard.style.maxWidth = '400px';
        skeletonCard.style.margin = '0 auto';
        
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(skeletonCard);
    }

    renderSearchResult(pokemon) {
        const resultsDiv = document.getElementById('search-results');
        const card = this.createPokemonCard(pokemon);
        card.style.maxWidth = '400px';
        card.style.margin = '0 auto';
        
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(card);
    }

    showSearchMessage(message) {
        const resultsDiv = document.getElementById('search-results');
        resultsDiv.innerHTML = `
            <div class="search-message">
                <p>${message}</p>
            </div>
        `;
    }

    showPokemonDetails(pokemon) {
        const modal = document.getElementById('pokemon-modal');
        const modalBody = document.getElementById('modal-body');

        const typeBadges = pokemon.types.map(type => 
            `<span class="type-badge type-${type}">${type}</span>`
        ).join('');

        const abilitiesList = pokemon.abilities.map(ability => 
            `<li>${ability.charAt(0).toUpperCase() + ability.slice(1)}</li>`
        ).join('');

        modalBody.innerHTML = `
            <div class="modal-pokemon">
                <div class="pokemon-header">
                    <span class="pokemon-id">#${pokemon.id.toString().padStart(3, '0')}</span>
                    <h2 class="pokemon-name">${pokemon.name}</h2>
                </div>
                
                <div class="pokemon-image">
                    <img src="${pokemon.sprite_url || '/static/images/pokeball.png'}" 
                         alt="${pokemon.name}"
                         onerror="this.src='/static/images/pokeball.png'">
                </div>

                <div class="pokemon-types">
                    ${typeBadges}
                </div>

                ${pokemon.description ? `
                    <div class="pokemon-description">
                        "${pokemon.description}"
                    </div>
                ` : ''}

                <div class="modal-stats">
                    <div class="modal-stat-group">
                        <h4>Physical Stats</h4>
                        <div class="stat-item">
                            <span class="stat-label">Height:</span>
                            <span class="stat-value">${pokemon.height.toFixed(1)} meters</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Weight:</span>
                            <span class="stat-value">${pokemon.weight.toFixed(1)} kg</span>
                        </div>
                    </div>

                    <div class="modal-stat-group">
                        <h4>Experience</h4>
                        <div class="stat-item">
                            <span class="stat-label">Base Experience:</span>
                            <span class="stat-value">${pokemon.base_experience}</span>
                        </div>
                    </div>

                    <div class="modal-stat-group">
                        <h4>Abilities</h4>
                        <ul style="list-style: none; padding: 0;">
                            ${abilitiesList}
                        </ul>
                    </div>
                </div>
            </div>
        `;

        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        const modal = document.getElementById('pokemon-modal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    showError(message) {
        const grid = document.getElementById('pokemon-grid');
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: white;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem; color: #fbbf24;"></i>
                <h3 style="margin-bottom: 1rem;">Oops! Something went wrong</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()" style="margin-top: 1rem;">
                    <i class="fas fa-refresh"></i> Try Again
                </button>
            </div>
        `;
        this.hideLoading();
    }
    
    // Battle Methods
    async loadPokemonList() {
        try {
            const response = await fetch('/api/pokemon-list');
            const data = await response.json();
            
            if (data.pokemon) {
                this.battleState.pokemonList = data.pokemon;
                this.populateDropdown(data.pokemon);
            }
        } catch (error) {
            console.error('Error loading Pokemon list:', error);
        }
    }
    
    populateDropdown(pokemonList) {
        const dropdown1 = document.getElementById('pokemon1-select');
        
        if (!dropdown1) return;
        
        pokemonList.forEach(pokemon => {
            const option1 = document.createElement('option');
            option1.value = pokemon;
            option1.textContent = pokemon.charAt(0).toUpperCase() + pokemon.slice(1);
            dropdown1.appendChild(option1);
        });
    }
    
    async generateRandomOpponent() {
        if (this.battleState.pokemonList.length === 0) return;
        
        const randomIndex = Math.floor(Math.random() * this.battleState.pokemonList.length);
        const randomPokemon = this.battleState.pokemonList[randomIndex];
        
        await this.loadBattlePokemon(randomPokemon, 2);
    }
    
    async loadBattlePokemon(pokemonName, playerNum) {
        if (!pokemonName) {
            this.clearPokemonPreview(playerNum);
            return;
        }
        
        try {
            const response = await fetch(`/api/battle/pokemon/${pokemonName}`);
            const pokemon = await response.json();
            
            if (response.ok) {
                this.battleState[`pokemon${playerNum}`] = {
                    ...pokemon,
                    max_hp: pokemon.stats.hp,
                    current_hp: pokemon.stats.hp
                };
                this.updatePokemonPreview(pokemon, playerNum);
                this.checkBattleReady();
            }
        } catch (error) {
            console.error('Error loading battle Pokemon:', error);
        }
    }
    
    updatePokemonPreview(pokemon, playerNum) {
        const preview = document.getElementById(`pokemon${playerNum}-preview`);
        if (!preview) return;
        
        const typeBadges = pokemon.types.map(type => 
            `<span class="type-badge type-${type}">${type}</span>`
        ).join('');
        
        preview.innerHTML = `
            <img src="${pokemon.sprite_url}" alt="${pokemon.name}" onerror="this.src='/static/images/pokeball.png'">
            <div class="preview-info">
                <div class="preview-name">${pokemon.name}</div>
                <div class="pokemon-types">${typeBadges}</div>
                <div class="preview-stats">
                    <div>HP: ${pokemon.stats.hp}</div>
                    <div>ATK: ${pokemon.stats.attack}</div>
                    <div>DEF: ${pokemon.stats.defense}</div>
                    <div>SPD: ${pokemon.stats.speed}</div>
                </div>
            </div>
        `;
    }
    
    clearPokemonPreview(playerNum) {
        const preview = document.getElementById(`pokemon${playerNum}-preview`);
        if (preview) {
            preview.innerHTML = '<p style="color: #888;">Select a Pokemon to see preview</p>';
        }
        this.battleState[`pokemon${playerNum}`] = null;
        this.checkBattleReady();
    }
    
    checkBattleReady() {
        const startBtn = document.getElementById('start-battle-btn');
        const ready = this.battleState.pokemon1 && this.battleState.pokemon2;
        
        if (startBtn) {
            startBtn.disabled = !ready;
        }
    }
    
    startBattle() {
        if (!this.battleState.pokemon1 || !this.battleState.pokemon2) return;
        
        // Reset HP
        this.battleState.pokemon1.current_hp = this.battleState.pokemon1.max_hp;
        this.battleState.pokemon2.current_hp = this.battleState.pokemon2.max_hp;
        
        // Player always starts first
        this.battleState.currentTurn = 1;
        this.battleState.isActive = true;
        
        // Show battle arena
        document.getElementById('battle-setup').style.display = 'none';
        document.getElementById('battle-arena').style.display = 'block';
        
        // Setup battle display
        this.setupBattleDisplay();
        this.updateTurnInfo();
        this.addBattleLog(`Battle begins! ${this.battleState.pokemon1.name} vs ${this.battleState.pokemon2.name}!`);
        this.addBattleLog(`${this.battleState.pokemon1.name}, it's your turn!`);
        
        // Enable attack button for player turn
        document.getElementById('attack-btn').disabled = false;
    }
    
    setupBattleDisplay() {
        // Setup Pokemon 1 (left side - back sprite)
        document.getElementById('pokemon1-name').textContent = this.battleState.pokemon1.name;
        document.getElementById('pokemon1-sprite').innerHTML = 
            `<img src="${this.battleState.pokemon1.back_sprite_url || this.battleState.pokemon1.sprite_url}" alt="${this.battleState.pokemon1.name}">`;
        this.updateHPBar(1);
        
        // Setup Pokemon 2 (right side - front sprite)
        document.getElementById('pokemon2-name').textContent = this.battleState.pokemon2.name;
        document.getElementById('pokemon2-sprite').innerHTML = 
            `<img src="${this.battleState.pokemon2.sprite_url}" alt="${this.battleState.pokemon2.name}">`;
        this.updateHPBar(2);
        
        // Clear battle log
        document.getElementById('battle-log').innerHTML = '';
    }
    
    updateTurnInfo() {
        const turnText = document.getElementById('turn-text');
        const turnArrow = document.getElementById('turn-arrow');
        
        if (this.battleState.currentTurn === 1) {
            turnText.textContent = 'Your Turn';
            turnArrow.className = 'turn-arrow left';
        } else {
            turnText.textContent = 'Opponent\'s Turn';
            turnArrow.className = 'turn-arrow right';
        }
    }
    
    updateHPBar(playerNum) {
        const pokemon = this.battleState[`pokemon${playerNum}`];
        const hpPercent = (pokemon.current_hp / pokemon.max_hp) * 100;
        
        const hpFill = document.getElementById(`pokemon${playerNum}-hp-fill`);
        const hpText = document.getElementById(`pokemon${playerNum}-hp-text`);
        
        if (hpFill) {
            hpFill.style.width = `${hpPercent}%`;
            hpFill.className = 'hp-fill';
            
            if (hpPercent <= 25) {
                hpFill.classList.add('low');
            } else if (hpPercent <= 50) {
                hpFill.classList.add('medium');
            }
        }
        
        if (hpText) {
            hpText.textContent = `${pokemon.current_hp}/${pokemon.max_hp}`;
        }
    }
    
    async performPlayerAttack() {
        if (!this.battleState.isActive || this.battleState.currentTurn !== 1) return;
        
        await this.performAttack(1, 2);
        
        // Switch to computer turn if battle is still active
        if (this.battleState.isActive) {
            this.battleState.currentTurn = 2;
            this.updateTurnInfo();
            document.getElementById('attack-btn').disabled = true;
            document.getElementById('computer-thinking').style.display = 'block';
            
            // Computer attacks after 2 seconds
            setTimeout(() => {
                this.performComputerAttack();
            }, 2000);
        }
    }
    
    async performComputerAttack() {
        if (!this.battleState.isActive || this.battleState.currentTurn !== 2) return;
        
        document.getElementById('computer-thinking').style.display = 'none';
        
        await this.performAttack(2, 1);
        
        // Switch back to player turn if battle is still active
        if (this.battleState.isActive) {
            this.battleState.currentTurn = 1;
            this.updateTurnInfo();
            document.getElementById('attack-btn').disabled = false;
        }
    }

    async performAttack(attackerNum, defenderNum) {
        const attacker = this.battleState[`pokemon${attackerNum}`];
        const defender = this.battleState[`pokemon${defenderNum}`];
        
        // Play attack animation
        this.playAttackAnimation(attackerNum);
        
        try {
            const response = await fetch('/api/battle/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    attacker: attacker,
                    defender: defender
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Update defender's HP
                this.battleState[`pokemon${defenderNum}`].current_hp = result.new_hp;
                
                setTimeout(() => {
                    // Play red blink hit animation
                    this.playRedBlinkAnimation(defenderNum);
                    
                    // Update HP bar
                    this.updateHPBar(defenderNum);
                    
                    // Add to battle log
                    this.addBattleLog(result.battle_log);
                    
                    // Check if battle is over
                    if (result.is_fainted) {
                        this.endBattle(attackerNum);
                    }
                }, 300);
            }
        } catch (error) {
            console.error('Error simulating attack:', error);
        }
    }
    
    playAttackAnimation(playerNum) {
        const sprite = document.getElementById(`pokemon${playerNum}-sprite`);
        if (sprite) {
            sprite.classList.add('attacking');
            setTimeout(() => {
                sprite.classList.remove('attacking');
            }, 600);
        }
    }
    
    playRedBlinkAnimation(playerNum) {
        const sprite = document.getElementById(`pokemon${playerNum}-sprite`);
        if (sprite) {
            sprite.classList.add('hit-red');
            setTimeout(() => {
                sprite.classList.remove('hit-red');
            }, 800);
        }
    }
    
    playHitAnimation(playerNum) {
        const sprite = document.getElementById(`pokemon${playerNum}-sprite`);
        if (sprite) {
            sprite.classList.add('hit');
            setTimeout(() => {
                sprite.classList.remove('hit');
            }, 600);
        }
    }
    
    addBattleLog(message) {
        const log = document.getElementById('battle-log');
        if (log) {
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = message;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }
    }
    
    endBattle(winnerNum) {
        this.battleState.isActive = false;
        const winner = this.battleState[`pokemon${winnerNum}`];
        
        this.addBattleLog(`${winner.name} wins the battle!`);
        
        // Add winner message to log
        const log = document.getElementById('battle-log');
        if (log) {
            const winnerEntry = document.createElement('div');
            winnerEntry.className = 'log-entry winner';
            winnerEntry.textContent = `🏆 ${winner.name} is victorious! 🏆`;
            log.appendChild(winnerEntry);
            log.scrollTop = log.scrollHeight;
        }
        
        // Hide attack button, show new battle button
        document.getElementById('attack-btn').style.display = 'none';
        document.getElementById('new-battle-btn').style.display = 'inline-block';
    }
    
    resetBattle() {
        // Reset battle state
        this.battleState = {
            pokemon1: null,
            pokemon2: null,
            currentTurn: 1,
            isActive: false,
            pokemonList: this.battleState.pokemonList // Keep the pokemon list
        };
        
        // Reset UI
        document.getElementById('battle-arena').style.display = 'none';
        document.getElementById('battle-setup').style.display = 'block';
        document.getElementById('attack-btn').style.display = 'inline-block';
        document.getElementById('new-battle-btn').style.display = 'none';
        document.getElementById('computer-thinking').style.display = 'none';
        
        // Reset dropdown
        document.getElementById('pokemon1-select').value = '';
        
        // Clear previews
        this.clearPokemonPreview(1);
        this.clearPokemonPreview(2);
    }
}

// Utility functions
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatNumber(num) {
    return num.toLocaleString();
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PokemonViewer();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}