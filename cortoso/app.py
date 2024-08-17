from flask import Flask, request, render_template
import requests, os, uuid
from dotenv import load_dotenv

load_dotenv()  # Loads values from .env file

app = Flask(__name__)

languages = ["English", "Italian", "Japanese", "Russian", "German"]

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", languages=languages)

@app.route('/', methods=['POST'])
def index_post():
    original_text = request.form['text']
    target_language = request.form['language']

    key = os.getenv('KEY')
    endpoint = os.getenv('ENDPOINT')
    location = os.getenv('LOCATION')

    # Language code mapping
    language_code = {
        "English": "en",
        "Italian": "it",
        "Japanese": "ja",
        "Russian": "ru",
        "German": "de"
    }
    target_language_code = language_code.get(target_language, "en")  # Default to English if unknown

    path = '/translate?api-version=3.0'
    target_language_parameter = '&to=' + target_language_code
    constructed_url = endpoint + path + target_language_parameter

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': original_text}]

    try:
        # Print the constructed URL for debugging
        print(f"Constructed URL: {constructed_url}")

        # Make the API request
        translator_request = requests.post(constructed_url, headers=headers, json=body)
        translator_request.raise_for_status()  # Raises an HTTPError for bad responses
        translator_response = translator_request.json()

        # Check if the response structure is as expected
        if translator_response and isinstance(translator_response, list):
            translated_text = translator_response[0]['translations'][0]['text']
        else:
            translated_text = "Unexpected response format."
    except requests.exceptions.HTTPError as e:
        translated_text = "HTTP error occurred: " + str(e)
    except (KeyError, IndexError) as e:
        translated_text = "Error parsing response: " + str(e)
    except Exception as e:
        translated_text = "An unexpected error occurred: " + str(e)

    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )

if __name__ == '__main__':
    app.run()
