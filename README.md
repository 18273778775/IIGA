# Immune Genetic Algorithm (IGA) Flask Web Application

This project implements various Immune Genetic Algorithms (IGAs) and provides a Flask web application to run them, visualize results, and compare different algorithm variants.

## Project Overview

The core of the project lies in `algorithm.py`, which defines an abstract base class `ImmuneGeneticAlgorithm` and several concrete implementations:
*   `StandardImmuneGeneticAlgorithm`
*   `ImprovedImmuneGeneticAlgorithm` (with optional elite retention)
*   `TournamentSelectionIGA`
*   `AdaptiveMutationIGA`
*   `DiversityEnhancedIGA`
*   `OptimizedImmuneGeneticAlgorithm`

The Flask application (`app.py`, `main.py`) allows users to:
*   Run a selected IGA with specified parameters.
*   View plots of best and average fitness over generations.
*   Run Taguchi experiments to find optimal parameters for the `ImprovedImmuneGeneticAlgorithm`.
*   Compare the performance of two different IGA variants.

## Setup and Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create a Python virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        venv\\Scripts\\activate
        ```

4.  **Install dependencies:**
    The project dependencies are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Once the setup is complete, you can run the Flask application:

1.  **Start the Flask development server:**
    ```bash
    python main.py
    ```
    Alternatively, you can use the `flask` command (if Flask is installed globally or the virtual environment is active):
    ```bash
    flask run
    ```
    The application will typically be available at `http://127.0.0.1:5000` or `http://0.0.0.0:5000`.

2.  **Open your web browser** and navigate to the address shown in the terminal.

You should see the web interface where you can select algorithms, adjust parameters, and run simulations.

## Project Structure

```
.
├── README.md           # This file
├── algorithm.py        # Core IGA implementations
├── app.py              # Flask application logic (routes, views)
├── main.py             # Entry point to run the Flask app
├── models.py           # Placeholder for database models (currently unused)
├── pyproject.toml      # Project metadata and dependencies (PEP 621)
├── requirements.txt    # Pinned dependencies for pip
├── utils.py            # Utility functions
└── templates/          # HTML templates for the Flask app (implicitly used by render_template)
    └── index.html      # Main HTML page (Note: This file is not in the repo but is expected by app.py)
```

**Note on `templates/index.html`:** The Flask application (`app.py`) uses `render_template('index.html')`. This file was not present in the initial repository listing. For the application to run correctly, an `index.html` file needs to be present in a `templates` directory at the root of the project. You may need to create this file or restore it if it was part of the original Replit project but not committed.

## Contributing
(Add guidelines for contributing if this were an open project).
