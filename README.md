# Simple Passphrase Generator
This is a simple passphrase generator that generates a passphrase based on a list of words. The list of words is taken from the DataMuse API. The user can specify the number of words in the passphrase and the number of passphrases to generate. The passphrases are generated using the random module in Python.
It runs on Flask and can be deployed to any cloud or local server.

## Installation
To install the required packages, run the following command:
```bash
pip install -r requirements.txt
```

## Important
- The program requires an internet connection to access the DataMuse API.
- This program is early in development and is not fully secure. It is recommended to use a more secure passphrase generator for sensitive information.
- The DataMuse API has a limit of 1000 requests per hour. If the limit is reached, the program will not be able to generate passphrases.

## Usage
To use the passphrase generator, run the following command:
```
python3 passphrase_generator.py
```
The user will be prompted to enter the number of words in the passphrase and the number of passphrases to generate. The passphrases will be displayed on the screen.