import random
import string

import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Flag to enable or disable SSL verification
VERIFY_SSL = False

# HTML template with Pico.css
HTML = """
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
        <input type="number" id="min_length" name="min_length" value="{{ min_length }}" min="8" max="128">
        <br><br>
        <label for="add_number">Add Random Number:</label>
        <input type="checkbox" role="switch" id="add_number" name="add_number" {% if add_number %}checked{% endif %}>
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
      </article>
    </main>
  </body>
</html>
"""

def fetch_words(min_length: int):
    """
    Fetch English words from the Datamuse API.

    Returns:
        List of English words.
    """
    url = "https://random-word-api.vercel.app/api?words=1"
    words_list = []
    passphrase_conditions_met = False
    while not passphrase_conditions_met:
      try:
          # Fetch words from the API
          response = requests.get(url, verify=VERIFY_SSL)

          # Check if the response is successful
          response.raise_for_status()

          # Extract the first key of JSON response as a string, as long as the word length is greater than 2
          word = response.json()[0]
          if word and len(word) > 2:
              words_list.append(word)

      except requests.RequestException as e:
          print(f"Error fetching words: {e}")
          return []
      
      # Check if the total length of the words is greater than or equal to the minimum length
      if len(words_list) >= 2 and len("".join(words_list)) >= min_length:
        passphrase_conditions_met = True
        print(f"Words: {words_list}")

    return words_list


def generate_passphrase(words: list, add_number: bool):
    """
    Generate a passphrase using two random words from the list.

    Args:
        words: List of English words.
        min_length: Minimum length of the passphrase.
        add_number: Whether to add a random number at the end.

    Returns:
        Passphrase string.
    """
    passphrase = ""

    words = [word.capitalize() for word in words]

    # Join the words with a hyphen and replace spaces with hyphens (-)
    passphrase = "-".join(words).replace(" ", "-")

    if add_number:
        # Add a random number at the end of the passphrase, with a length of 2 digits
        random_number = "".join(random.choices(string.digits, k=2))
        passphrase += f"-{random_number}"
    return passphrase


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Render the HTML template and generate a passphrase.

    Returns:
        Rendered HTML template.
    """
    # Initialize variables
    passphrase = None
    error = None
    min_length = 16
    add_number = True

    # Handle POST request initiated by the user's form submission
    if request.method == "POST":
        # Get the minimum length and add_number values from the form
        min_length = int(request.form.get("min_length", 16))
        add_number = (
            "add_number" in request.form
        )

        # Fetch words from the API
        words = fetch_words(min_length)

        # Generate a passphrase using the fetched words
        if words:
            passphrase = generate_passphrase(words, add_number)
        else:
            error = "Failed to fetch words. Please try again."

    return render_template_string(
        HTML,
        passphrase=passphrase,
        error=error,
        min_length=min_length,
        add_number=add_number
    )


if __name__ == "__main__":
    app.run(debug=True)
