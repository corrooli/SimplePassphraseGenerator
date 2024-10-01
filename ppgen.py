from flask import Flask, render_template_string, request
import requests
import random
import string

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
        <input type="number" id="min_length" name="min_length" value="{{ min_length }}" min="8" max="100">
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

def fetch_words():
    """
    Fetch English words from the Datamuse API.

    Returns:
        List of English words.
    """
    url = "https://api.datamuse.com/words?ml=word&max=10&v=en"
    try:
        response = requests.get(url, verify=VERIFY_SSL)
        response.raise_for_status()
        english_words = [word['word'] for word in response.json() if len(word['word']) > 2]
        return english_words
    except requests.RequestException as e:
        print(f"Error fetching words: {e}")
        return []

def generate_passphrase(words: list, min_length: int, add_number: bool):
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
    while len(passphrase.replace(" ", "-")) < min_length:
        if len(words) < 2:
            return "Not enough words to generate a passphrase."
        selected_words = random.sample(words, 2)
        selected_words = [word.capitalize() for word in selected_words]
        passphrase = '-'.join(selected_words).replace(" ", "-")
        if len(passphrase) >= min_length:
            break
    if add_number:
        random_number = ''.join(random.choices(string.digits, k=2))
        passphrase += f"-{random_number}"
    return passphrase

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Render the HTML template and generate a passphrase.
    
    Returns:
        Rendered HTML template.
    """
    passphrase = None
    error = None
    min_length = 16
    add_number = True

    if request.method == 'POST':
        min_length = int(request.form.get('min_length', 16))
        add_number = 'add_number' in request.form  # Checkbox will be in form data only if checked
        words = fetch_words()
        if words:
            passphrase = generate_passphrase(words, min_length, add_number)
        else:
            error = "Failed to fetch words. Please try again."
    
    return render_template_string(HTML, passphrase=passphrase, error=error, min_length=min_length, add_number=add_number)

if __name__ == '__main__':
    app.run(debug=True)
