# 🎮 Pokemon Viewer

A modern Python application that consumes the [PokeAPI](https://pokeapi.co/) to display Pokemon information with lazy loading functionality. Available in both **console interface** and **beautiful web interface**.

## ✨ Features

- **🌐 Web Interface**: Modern, responsive web application with beautiful UI
- **💻 Console Interface**: Rich terminal interface for command-line users
- **🔄 Lazy Loading**: Load Pokemon data on-demand with pagination to avoid overwhelming the API
- **✨ Skeleton Loading**: Beautiful animated skeleton cards during page transitions and searches
- **🔍 Search Function**: Find specific Pokemon by name in both interfaces
- **📱 Responsive Design**: Web interface works perfectly on desktop, tablet, and mobile
- **🎨 Beautiful Interface**: Rich console interface with colors, tables, and panels
- **📋 Detailed View**: View comprehensive Pokemon information including:
  - ID, Name, Height, Weight
  - Types and Abilities
  - Base Experience
  - Pokemon Description
  - Sprite Images (web interface)
- **📄 Pagination**: Shows current page, total pages, and navigation options
- **✨ Skeleton Loading**: Smooth animated placeholders during content loading
- **⚡ Fast Performance**: Optimized loading with API rate limiting
- **🛠️ Error Handling**: Graceful error handling for network issues and invalid inputs

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection (to fetch data from PokeAPI)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd pokemon-viewer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your interface:**

   **🌐 Web Interface (Recommended)**
   ```bash
   python web_app.py
   ```
   Then open your browser and navigate to: `http://localhost:5000`

   **💻 Console Interface**
   ```bash
   python main.py
   ```

   **🚀 Quick Start (Windows)**
   ```bash
   # For web interface
   run_web.bat
   
   # For console interface
   run.bat
   ```

## 📦 Dependencies

The application uses the following Python packages:

- **requests (2.31.0+)**: For making HTTP requests to the PokeAPI
- **rich (13.7.0+)**: Beautiful console formatting and interface
- **flask (3.0.0+)**: Web framework for the web interface
- **flask-cors (6.0.0+)**: Cross-origin resource sharing for API endpoints

## 🎯 Usage

### 🌐 Web Interface (Recommended)

The web interface provides the best user experience with:

- **Home Page**: Browse Pokemon with beautiful card layout and lazy loading
- **Skeleton Loading**: Animated placeholder cards during page transitions for seamless UX
- **Search Page**: Find specific Pokemon with instant search and skeleton preview
- **About Page**: Learn about the application and technology stack
- **Pokemon Details**: Click any Pokemon card to see detailed information in a modal
- **Responsive Design**: Works on all devices and screen sizes

#### Navigation
- **Browse**: Use pagination buttons to navigate through Pokemon pages
- **Search**: Enter Pokemon name in the search box and click search
- **Details**: Click any Pokemon card to see detailed information
- **Modal**: Click outside the modal or the X button to close

### 💻 Console Interface

When you start the console application, you'll see the main menu with three options:

1. **Browse Pokemon List**: Navigate through Pokemon with lazy loading
2. **Search for Pokemon**: Find a specific Pokemon by name
3. **Exit**: Close the application

#### Browse Mode

- **Navigation**: Use 'P' for Previous page, 'N' for Next page
- **View Details**: Press 'D' and enter a Pokemon ID to see detailed information
- **Back to Menu**: Press 'B' to return to the main menu

#### Search Mode

- Enter any Pokemon name (case-insensitive)
- View detailed information if found
- Returns to main menu after viewing

## 🏗️ Project Structure

```
pokemon-viewer/
│
├── main.py                    # Console application entry point
├── web_app.py                 # Web application entry point
├── pokemon_api.py             # PokeAPI client for HTTP requests
├── pokemon_service.py         # Business logic and lazy loading
├── pokemon_displayer.py       # Console interface and display logic
├── models.py                  # Data models (Pokemon, PaginationInfo)
├── config.py                  # Configuration settings
├── demo.py                    # Demo script to test functionality
├── requirements.txt           # Python dependencies
├── run.bat                    # Windows batch file for console app
├── run_web.bat               # Windows batch file for web app
├── README.md                  # This file
├── .gitignore                 # Git ignore file
│
├── templates/                 # HTML templates for web interface
│   └── index.html            # Main web page template
│
└── static/                    # Static files for web interface
    ├── css/
    │   └── style.css         # Main stylesheet
    └── js/
        ├── app.js            # Main JavaScript application
        └── sw.js             # Service worker for offline support
```

## 🔧 Architecture

### Components

1. **PokeAPIClient** (`pokemon_api.py`)
   - Handles all HTTP requests to the PokeAPI
   - Implements error handling and timeouts
   - Methods for fetching Pokemon list, details, and species information

2. **Pokemon & PaginationInfo Models** (`models.py`)
   - Data classes for structured Pokemon information
   - Pagination metadata for lazy loading
   - Helper methods for data conversion

3. **PokemonService** (`pokemon_service.py`)
   - Business logic layer
   - Implements lazy loading with pagination
   - Caching and state management
   - Search functionality

4. **Web Interface** (`web_app.py`, `templates/`, `static/`)
   - Flask web application with RESTful API
   - Modern, responsive HTML/CSS/JavaScript frontend
   - AJAX-based lazy loading and search
   - Modal dialogs for detailed Pokemon information

5. **Console Interface** (`pokemon_displayer.py`)
   - Rich console formatting
   - Menu navigation and user input handling
   - Progress indicators and loading states

### Lazy Loading Implementation

The application implements lazy loading through:

- **Pagination**: Loads only 12 Pokemon per page for web interface, 10 for console
- **Skeleton Loading**: Shows animated placeholder cards during data fetching for better UX
- **On-Demand Loading**: Fetches detailed information only when needed
- **API Rate Limiting**: Includes small delays between requests to be respectful to the API
- **Memory Efficient**: Doesn't load all Pokemon at once
- **AJAX Loading**: Web interface uses asynchronous requests for smooth user experience

## 🌐 Web API Endpoints

The web application exposes the following REST API endpoints:

- **GET `/`**: Main web page
- **GET `/api/pokemon?page={page}&limit={limit}`**: Get paginated Pokemon list
- **GET `/api/pokemon/{name}`**: Get specific Pokemon details
- **GET `/api/search?q={query}`**: Search for Pokemon by name

### Example API Usage

```javascript
// Get first page of Pokemon
fetch('/api/pokemon?page=1&limit=12')
  .then(response => response.json())
  .then(data => console.log(data));

// Search for Pikachu
fetch('/api/search?q=pikachu')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 🌐 PokeAPI Integration

### PokeAPI Endpoints Used

1. **Pokemon List**: `GET /pokemon?limit={limit}&offset={offset}`
   - Fetches paginated list of Pokemon
   - Used for browse mode pagination

2. **Pokemon Details**: `GET /pokemon/{name}`
   - Fetches detailed Pokemon information
   - Includes stats, types, abilities, sprites

3. **Pokemon Species**: `GET /pokemon-species/{id}`
   - Fetches Pokemon descriptions and flavor text
   - Used to get Pokemon descriptions in English

### Rate Limiting

The application implements respectful API usage:
- 0.1 second delay between detailed requests
- Timeout limits on all requests (10 seconds)
- Error handling for network failures
- Session reuse for connection pooling

## 🎨 User Interface

### 🌐 Web Interface Features

- **Modern Design**: Clean, colorful interface with Pokemon-themed styling
- **Card Layout**: Beautiful Pokemon cards with images, types, and stats
- **Skeleton Loading**: Smooth animated placeholders during page transitions and searches
- **Responsive Grid**: Adapts to different screen sizes automatically
- **Loading Indicators**: Smooth loading animations during API calls
- **Modal Dialogs**: Detailed Pokemon information in overlay windows
- **Navigation Menu**: Easy switching between Browse, Search, and About sections
- **Type Badges**: Color-coded Pokemon type indicators
- **Search Box**: Instant search with real-time feedback and skeleton preview

### 💻 Console Interface Features

- **Rich Tables**: Formatted Pokemon lists with colors and styling
- **Progress Indicators**: Loading spinners during API calls
- **Panels**: Bordered sections for better organization
- **Color Coding**: Different colors for different types of information
- **Interactive Prompts**: User-friendly input prompts with validation

### Display Elements

- **Pokemon List Table**: ID, Name, Types, Height, Weight, Experience
- **Pagination Info**: Current page, total pages, navigation options
- **Detailed View**: Comprehensive Pokemon information in formatted panels
- **Menu System**: Clear navigation with numbered options

## 🚨 Error Handling

The application handles various error scenarios:

- **Network Errors**: Graceful handling of connection issues
- **API Errors**: Proper error messages for API failures
- **Invalid Input**: Validation for user inputs
- **Pokemon Not Found**: Clear messages when Pokemon don't exist
- **Keyboard Interrupts**: Clean exit on Ctrl+C

## 🔄 Configuration

### Customizable Settings

You can modify these settings in the respective files:

- **Page Size**: Change `page_size` in `PokemonService` (default: 10)
- **API Timeout**: Modify timeout in `PokeAPIClient` (default: 10 seconds)
- **API Delay**: Adjust delay between requests in `PokemonService` (default: 0.1s)
- **Base URL**: Change PokeAPI base URL if needed

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Network Connection Issues**
   - Check internet connection
   - Verify PokeAPI is accessible: https://pokeapi.co/api/v2/pokemon

3. **Slow Loading**
   - This is normal due to API rate limiting
   - Reduce page size for faster loading

4. **Display Issues**
   - Ensure terminal supports Unicode characters
   - Try running in a different terminal

### Performance Tips

- Use smaller page sizes for faster navigation
- Search for specific Pokemon instead of browsing when possible
- The application caches current page data for better performance

## 🤝 Contributing

Feel free to contribute to this project by:

1. Reporting bugs
2. Suggesting new features
3. Submitting pull requests
4. Improving documentation

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [PokeAPI](https://pokeapi.co/) for providing the Pokemon data
- [Rich](https://github.com/Textualize/rich) for the beautiful console interface
- Pokemon fans and developers worldwide

## 📧 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section
2. Review the error messages for specific guidance
3. Ensure all dependencies are properly installed

---

**Happy Pokemon browsing! 🎮✨**