"""
Minimalistic Passphrase Generator using Flask and Pico.css.

This script generates a passphrase using two random English words fetched from the Vercel Random Word API.
The user can specify the minimum length of the passphrase and whether to add a random number at the end.
The generated passphrase is displayed to the user on the webpage.

The Flask web application uses a simple HTML template with Pico.css for styling.
Everything is contained in a single Python script for simplicity.

Author: Oliver Corrodi
Released under the GNU General Public License v3.0
"""

import random
import string

import re  # Import regex module for password strength checking

import requests
from flask import Flask, render_template_string, request

# Initialize the Flask app.
app = Flask(__name__)

# Flag to enable or disable SSL verification
VERIFY_SSL: bool = False

# HTML template with Pico.css
HTML: str = """
<!doctype html>
<html lang="en">
	<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Passphrase Generator</title>
	<!-- Include Pico.css from a CDN -->
	<link rel="stylesheet" href="https://unpkg.com/@picocss/pico@1.*/css/pico.min.css">
	</head>
	<body>
	<main class="container">
	<h1>Passphrase Generator</h1>
	<form method="post">
		<label for="min_length">Minimum Length:</label>
		<input type="number" id="min_length" name="min_length" value="{{ min_length }}" min="3" max="16">
		<br><br>
		<input type="checkbox" role="switch" id="add_number" name="add_number" {% if add_number %}checked{% endif %}>
		<label for="add_number">Add Random Number</label>
		<br><br>
		<input type="checkbox" role="switch" id="add_special" name="add_special" {% if add_special %}checked{% endif %}>
		<label for="add_special">Add Special Character</label>
		<br><br>
		<button type="submit">Generate Passphrase</button>
	</form>
	<article>
	{% if passphrase %}
		<p><strong>{{ passphrase }}</strong></p>
	{% endif %}
	{% if error %}
		<h2>Error:</h2>
		<p><strong>{{ error }}</strong></p>
	{% endif %}
	{% if strength %}
		<p><strong>Strength:</strong> {{ strength }}</p>
	{% endif %}
	</article>
	</main>
	</body>
</html>
"""


def fetch_words(min_length: int) -> list:
    """
    Fetch English words from the Datamuse API.

    Args:
        min_length: Minimum length of the passphrase.

    Returns:
        List of English words.
    """
    url: str = f"https://random-word-api.vercel.app/api?words={min_length}"
    words_list: list = []
    try:
		# Fetch words from the API
        response = requests.get(url, verify=VERIFY_SSL)

		# Check if the response is successful
        response.raise_for_status()
		
		# Extract the words from the response, API delivers data like ["grub","craftsman","tinkling","gumdrop","daily","twiddle","shorts","anthem","yin","obligate","scalping","immorally"]
        words_list = response.json()
        print(response.json())

    except requests.RequestException as e:
        print(f"Error fetching words: {e}")
        return []

    return words_list


def generate_passphrase(words: list, add_number: bool, add_special: bool) -> str:
    """
    Generate a passphrase using two random words from the list.

    Args:
        words: List of English words.
        add_number: Whether to add a random number at the end.
        add_special: Whether to add a special character at the end.

    Returns:
        Passphrase string.
    """
    passphrase: str = ""

    words: list = [word.capitalize() for word in words]

    # Join the words with a hyphen and replace spaces with hyphens (-)
    passphrase = "-".join(words).replace(" ", "-")

    if add_number:
        # Add a 2-digit random number at the end of the passphrase
        random_number = "".join(random.choices(string.digits, k=2))
        passphrase += random_number
    if add_special:
        # Add a special character if specified
        special_char = random.choice(["#", "!"])
        passphrase += special_char
    return passphrase


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """
    Render the HTML template and generate a passphrase.

    Returns:
        Rendered HTML template.
    """
    # Initialize variables
    passphrase = None
    error = None
    min_length = 3
    add_number = True
    add_special = False
    strength = None

    # Handle POST request initiated by the user's form submission
    if request.method == "POST":
        # Get the minimum length and add_number values from the form
        min_length = int(request.form.get("min_length", 3))
        add_number = "add_number" in request.form
        add_special = "add_special" in request.form  # Retrieve add_special option

        # Fetch words from the API
        words = fetch_words(min_length)

        # Generate a passphrase using the fetched words
        if words:
            passphrase = generate_passphrase(words, add_number, add_special)
            strength = check_password_strength(passphrase)  # Check passphrase strength
            print(f"Generated Passphrase: {passphrase}")
            print(f"Password Strength: {strength}")
        else:
            error = "Failed to fetch words. Please try again."

    return render_template_string(
        HTML,
        passphrase=passphrase,
        error=error,
        min_length=min_length,
        add_number=add_number,
        add_special=add_special,
        strength=strength,
    )


def check_password_strength(passphrase: str) -> str:
    """
    Check the strength of the passphrase and return a descriptive rating.
    Criteria:
    - Length: longer is stronger
    - Contains uppercase and lowercase letters
    - Contains digits
    - Contains special characters

    Args:
        passphrase: Passphrase string.

    Returns:
        Strength rating: "Weak", "Medium", or "Strong".
    """
    length = len(passphrase)
    has_upper = bool(re.search(r"[A-Z]", passphrase))
    has_lower = bool(re.search(r"[a-z]", passphrase))
    has_digit = bool(re.search(r"\d", passphrase))
    has_special = bool(
        re.search(r"[^\w\s-]", passphrase)
    )  # Special characters other than hyphens

    # Scoring logic
    score = sum([has_upper, has_lower, has_digit, has_special])

    # Evaluate based on length and score
    if length >= 12 and score == 4:
        return "Strong"
    if length >= 8 and score >= 3:
        return "Medium"
    return "Weak"


# Entry point for the application. Runs the Flask app.
if __name__ == "__main__":
    app.run(debug=True)
