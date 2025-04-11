# Advanced Post-Tax Income Calculator (Flet)

This application calculates the estimated Gross Pre-Tax Annual Income required to achieve a user-specified Desired Annual Post-Tax Income, considering various US taxes and deductions. It is built using the Flet framework (Python).

## Prerequisites

*   Python 3.7 or newer
*   pip (Python package installer)

## Installation

1.  **Clone the repository (if applicable) or ensure you have the `tax_calculator.py` file.**
2.  **Navigate to the project directory in your terminal:**
    ```bash
    cd /path/to/your/TaxCalc # Replace with the actual path
    ```
3.  **Create and activate a virtual environment (recommended):**
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

You can run this application either as a native desktop app or as a web app in your browser.

### Run as Desktop App

Execute the following command in your terminal (ensure your virtual environment is activated):

```bash
flet run tax_calculator.py
```

This will launch the calculator as a standard desktop window.

### Run as Web App

Execute the following command in your terminal (ensure your virtual environment is activated):

```bash
flet run -w tax_calculator.py
```

This will start a local web server and typically open the application automatically in your default web browser. If it doesn't open automatically, the terminal output will provide a URL (usually `http://localhost:8550` or similar) that you can navigate to.
