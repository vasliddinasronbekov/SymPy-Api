from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sympy as sp
import pytesseract
from PIL import Image
import io
import numpy as np
import cv2
import re
import matplotlib.pyplot as plt
import base64

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # CORS sozlamalari

# OCR sozlash
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_bytes):
    """Rasmni OCR uchun tayyorlash"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return thresh

def extract_math_from_image(image_bytes):
    """Rasmdan matematik ifodani ajratib olish"""
    processed_img = preprocess_image(image_bytes)
    custom_config = r'--oem 3 --psm 6 -l eng+equ'
    text = pytesseract.image_to_string(processed_img, config=custom_config)
    text = text.replace('?', '=').replace('§', '5').replace('¢', 'c')
    return text.strip()

def solve_math_problem(problem_text):
    """Matematik masalani yechish"""
    try:
        variables = list(set(re.findall(r'[a-zA-Z]', problem_text)) - set(['e', 'i', 'π']))
        
        if not variables:
            safe_dict = {k: v for k, v in vars(math).items() if not k.startswith('__')}
            safe_dict.update({'abs': abs, 'min': min, 'max': max})
            return str(eval(problem_text.replace('^', '**'), {"__builtins__": None}, safe_dict))
        
        if '=' in problem_text:
            lhs, rhs = problem_text.split('=', 1)
            expr = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
        else:
            expr = sp.sympify(problem_text)
        
        solutions = sp.solve(expr)
        return str(solutions)
    except Exception as e:
        return f"Xatolik: {str(e)}"

@app.route('/api/solve', methods=['POST', 'OPTIONS'])
def api_solve():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        if 'image' in request.files:
            image = request.files['image']
            problem_text = extract_math_from_image(image.read())
        else:
            data = request.get_json()
            problem_text = data.get('text', '')
        
        solution = solve_math_problem(problem_text)
        
        response = jsonify({
            'problem': problem_text,
            'solution': solution,
            'image_used': 'image' in request.files
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)