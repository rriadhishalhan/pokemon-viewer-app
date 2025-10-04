// Pokemon Viewer JavaScript Application
class PokemonViewer {
    constructor() {
        this.currentPage = 1;
        this.isLoading = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadPokemonPage(1);
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
        this.showLoading();

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
        resultsDiv.innerHTML = `
            <div class="search-message">
                <div class="loading-spinner"></div>
                <p>Searching...</p>
            </div>
        `;
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