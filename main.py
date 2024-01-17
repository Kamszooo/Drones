from flask import Flask, request
from PRNG import MT19937
from TRNG import generate_TRN

import json
import uuid
import bcrypt
import base64
app = Flask(__name__)


def load_operators(filename):
    try:
        with open(filename, 'r') as json_file:
            operators = json.load(json_file)
        return operators
    except FileNotFoundError:
        return []


def save_operators(filename, operators):
    with open(filename, 'w') as json_file:
        json.dump(operators, json_file, indent=2)


def authenticate_user(operators, username, password):
    for operator in operators:
        if operator['username'] == username:
            decoded_salt = base64.b64decode(operator['salt'])
            hashed_attempt = bcrypt.hashpw(password.encode('utf-8'), decoded_salt)
            encoded_original_hash = base64.b64decode(operator['hashed_password'])
            return hashed_attempt == encoded_original_hash
    return False


operators = load_operators('operators.json')
active_tokens = {}

# Przykładowa lokalizacja
current_location = {'X': 50, 'Y': 50}
next_waypoint = {}

mt19937_instance = MT19937(seed=generate_TRN(32))
#TO DO gdy przejdzie przez polowę internal states generate new trn and new instance of mt19937

for _ in range(3):
    print(mt19937_instance.extract_number())


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/api/get_location', methods=['GET'])
def get_location():
    return {'location': current_location}

@app.route('/api/set_location', methods=['POST'])
def set_location():
    data = request.get_json()
    print("data[token]: " + str(data['token']))
    print("jest inny niz obecne w active_tokens: " + str(active_tokens.values()))
    if data['token'] in active_tokens.values():
        if 100 >= data['X'] >= 0 and 100 >= data['Y'] >= 0:
            new_location = {'X': data['X'], 'Y': data['Y']}
            current_location.update(new_location)
            return {'status': 'success', 'message': 'Location updated successfully'}
        else:
            return {'status': 'error', 'message': 'Invalid data format'}
    else:
        return {'status': 'error', 'message': 'Invalid token'}

@app.route('/api/set_next_waypoint', methods=['POST'])
def set_next_waypoint():
    data = request.get_json()
    print(active_tokens.values())
    if data['token'] in active_tokens.values():
        if 100 >= data['X'] >= 0 and 100 >= data['Y'] >= 0:
            new_waypoint = {'X': data['X'], 'Y': data['Y']}
            next_waypoint.update(new_waypoint)
            return {'status': 'success', 'message': 'Next planned waypoint updated successfully'}
        else:
            return {'status': 'error', 'message': 'Invalid data format'}
    else:
        return {'status': 'error', 'message': 'Invalid token'}

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    global mt19937_instance
    global active_tokens
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username_received = data['username']
        password_received = data['password']

        if authenticate_user(operators, username_received, password_received):
            if mt19937_instance.get_state_fraction() > 0.01: # TO DO CHANGE

                mt19937_instance = MT19937(seed=generate_TRN(32))
                print("Created a new instance of MT19937")
            # Generowanie i nadawanie session_token
            session_token = mt19937_instance.extract_number()
            active_tokens[username_received] = session_token
            print(active_tokens)
            ''' 
            # Dodanie session_token do danych operatora
            for operator in operators:
                if operator['username'] == username_received:
                    operator['session_token'] = session_token '''

            return "User " + username_received + " authenticated. Session Token: " + str(active_tokens[username_received])

            # Zapisanie zaktualizowanej listy operatorów
         #   save_operators('operators.json', operators)
        else:
            return "Authentication failed. Invalid username or password."

if __name__ == '__main__':
    app.run(debug=True)
