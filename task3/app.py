import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# MonsterAPI credentials
MONSTER_API_KEY = 'your_monster_api_key'

# Whisper API endpoint
WHISPER_API_URL = 'https://api.monsterapi.com/v1/speech-to-text/whisper-large-v2'

# Stable Diffusion API endpoint
STABLE_DIFFUSION_API_URL = 'https://api.monsterapi.com/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image'


def transcribe_audio(file):
    """Transcribe audio to text using Whisper API."""
    headers = {'Authorization': f'Bearer {MONSTER_API_KEY}'}
    files = {'file': file}
    response = requests.post(WHISPER_API_URL, headers=headers, files=files)
    if response.status_code == 200:
        return response.json().get('text', '')
    return None


def generate_image(prompt):
    """Generate image from text using Stable Diffusion API."""
    headers = {'Authorization': f'Bearer {MONSTER_API_KEY}'}
    data = {'text_prompts': [{'text': prompt, 'weight': 1}], 'width': 1024, 'height': 1024}
    response = requests.post(STABLE_DIFFUSION_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('image_url', '')
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return render_template('index.html', error='No file part')
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return render_template('index.html', error='No selected file')
    if audio_file:
        # Transcribe audio to text
        transcript = transcribe_audio(audio_file)
        if not transcript:
            return render_template('index.html', error='Failed to transcribe audio')

        # Generate image from transcript
        image_url = generate_image(transcript)
        if not image_url:
            return render_template('index.html', error='Failed to generate image')

        return render_template('result.html', transcript=transcript, image_url=image_url)


if __name__ == '__main__':
    app.run(debug=True)
