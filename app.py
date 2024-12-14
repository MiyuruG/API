# app.py - Meme Image API with Direct Image Routes
import os
import random
import re
from flask import Flask, render_template, jsonify, send_from_directory, Response

app = Flask(__name__)

# Directory for local memes
MEMES_FOLDER = 'memes'

# Supported image file extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def get_local_memes():
    """
    Scan the memes folder and return a list of supported image files
    """
    memes = []
    for filename in os.listdir(MEMES_FOLDER):
        # Check file extension
        if os.path.splitext(filename)[1].lower() in SUPPORTED_EXTENSIONS:
            memes.append(filename)
    return memes


def find_closest_match(keyword, meme_list):
    """
    Find the closest matching meme filename based on the keyword
    Uses simple string matching with regex
    """
    # Create a case-insensitive regex pattern
    pattern = re.compile(re.escape(keyword.lower()), re.IGNORECASE)

    # First, try exact matches
    exact_matches = [m for m in meme_list if keyword.lower() in m.lower()]
    if exact_matches:
        return exact_matches[0]

    # Then try partial matches
    partial_matches = [m for m in meme_list if pattern.search(m)]
    return partial_matches[0] if partial_matches else None


@app.route('/')
def index():
    """Render the main index page"""
    return render_template('index.html')


@app.route('/random-meme-img')
def random_meme_img():
    """
    Serve a random meme image directly
    """
    local_memes = get_local_memes()

    if not local_memes:
        return jsonify({'error': 'No memes found in the folder'}), 404

    # Select a random meme
    selected_meme = random.choice(local_memes)

    # Full path to the meme
    meme_path = os.path.join(MEMES_FOLDER, selected_meme)

    # Determine mime type based on file extension
    ext = os.path.splitext(selected_meme)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_types.get(ext, 'application/octet-stream')

    # Open and read the image file
    try:
        with open(meme_path, 'rb') as f:
            image_binary = f.read()

        return Response(image_binary, content_type=mime_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/meme-by-title-img/<keyword>')
def meme_by_title_img(keyword):
    """
    Find and serve a meme image matching the keyword
    """
    # Get all local memes
    local_memes = get_local_memes()

    # Find the closest matching meme
    try:
        selected_meme = find_closest_match(keyword, local_memes)

        if not selected_meme:
            return jsonify({'error': 'No memes found matching the keyword'}), 404

        # Full path to the meme
        meme_path = os.path.join(MEMES_FOLDER, selected_meme)

        # Determine mime type based on file extension
        ext = os.path.splitext(selected_meme)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'application/octet-stream')

        # Open and read the image file
        with open(meme_path, 'rb') as f:
            image_binary = f.read()

        return Response(image_binary, content_type=mime_type)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Existing routes from previous implementation remain the same
@app.route('/random-meme')
def random_meme():
    """Fetch a random meme from the local memes folder"""
    local_memes = get_local_memes()

    if not local_memes:
        return jsonify({'error': 'No memes found in the folder'}), 404

    # Select a random meme
    selected_meme = random.choice(local_memes)

    return jsonify({
        'url': f'/memes/{selected_meme}',
        'title': selected_meme,
        'source': 'Local Meme Collection'
    })


@app.route('/meme-by-title/<keyword>')
def meme_by_title(keyword):
    """Find memes matching the keyword in their filename"""
    # Get all local memes
    local_memes = get_local_memes()

    # Find the closest matching meme
    selected_meme = find_closest_match(keyword, local_memes)

    if not selected_meme:
        return jsonify({'error': 'No memes found matching the keyword'}), 404

    return jsonify({
        'url': f'/memes/{selected_meme}',
        'title': selected_meme,
        'source': 'Local Meme Collection'
    })


@app.route('/memes/<filename>')
def serve_meme(filename):
    """Serve meme images from the memes folder"""
    return send_from_directory(MEMES_FOLDER, filename)


if __name__ == '__main__':
    # Ensure memes folder exists
    os.makedirs(MEMES_FOLDER, exist_ok=True)
    app.run(debug=True)