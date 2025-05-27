# StreetStyle E-commerce Platform

This is a backend application for the StreetStyle e-commerce platform, built with Flask and SQLAlchemy.

## Backend Setup and Usage

This section provides instructions on how to set up and run the backend server and its associated unit tests.

### Prerequisites

*   Python 3.x
*   pip (Python package installer)

### Setup Instructions

1.  **Clone the Repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Navigate to the Project Directory**:
    If you've already cloned, ensure you are in the root project directory where `app.py` and `requirements.txt` are located.

3.  **Create and Activate a Virtual Environment** (Recommended):
    *   On Linux/macOS:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

4.  **Install Dependencies**:
    With your virtual environment activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the Flask Development Server**:
    You can run the application using the following command:
    ```bash
    python app.py
    ```
    Alternatively, if you have Flask CLI installed and configured, you might use `flask run`. However, `python app.py` is generally reliable as the `if __name__ == '__main__':` block in `app.py` is set up to run the app.

2.  **Accessing the Application**:
    The application will be running by default at:
    `http://127.0.0.1:5000/`

3.  **Database Initialization**:
    On the first run, the SQLite database file (`streetwear.db`) will be automatically created in the project's root directory, along with all the necessary tables.

### Running Unit Tests

To execute the unit tests for the backend, run the following command from the project's root directory:

```bash
python test_app.py
```

This will discover and run all tests defined in the `test_app.py` file.