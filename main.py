import threading
import time
from sched import scheduler

from flask import Flask, request, render_template, redirect, url_for
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

drawn_numbers = []

# Początkowa lokalizacja
current_location = {'X': 50, 'Y': 50}
next_waypoint = {'X': 51, 'Y': 49}

mt19937_instance = MT19937(seed=generate_TRN(32))
#TO DO gdy przejdzie przez polowę internal states generate new trn and new instance of mt19937

# Funkcja do generowania nowej lokalizacji

def updating():
  #  global current_location
   # global next_waypoint
    # global mt19937_instance

    while True:
        global next_waypoint
        global current_location
        global mt19937_instance
        print("Next waypoint po śnie:" + str(next_waypoint))
        print("Current location:  " + str(current_location))
        print("Next waypoint:  " + str(next_waypoint))
        # Generowanie nowych współrzędnych
        if mt19937_instance.get_state_fraction() > 0.02:  # TO DO CHANGE
            mt19937_instance = MT19937(seed=generate_TRN(32))
            print("Created a new instance of MT19937")
        new_random = mt19937_instance.extract_number()
        drawn_numbers.append(new_random)
        new_x = new_random / 4294967295 * 100 #maximal number possible to drawn is 2^32-1 = 4294967295
        new_random = mt19937_instance.extract_number()
        drawn_numbers.append(new_random)
        new_y = new_random / 4294967295 * 100

        # Aktualizacja lokalizacji
        current_location = next_waypoint
        next_waypoint = {'X': new_x, 'Y': new_y}

        # Wydruk dla celów debugowania
        print(f"Current location changed to the previous next waypoint and set at {current_location}. New next waypoint drawn at: {next_waypoint}")
        print("Next waypoint przed snem:" + str(next_waypoint))
        # Oczekaj 4 sekundy przed następnym generowaniem lokalizacji
        time.sleep(10)

# Uruchomienie funkcji w osobnym wątku
location_thread = threading.Thread(target=updating)
location_thread.start()

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/api/get_location', methods=['GET'])
def get_location():
    return {'location': current_location}

@app.route('/api/get_next_waypoint', methods=['GET'])
def get_next_waypoint():
    return {'next_waypoint': next_waypoint}

@app.route('/api/set_location', methods=['POST'])
def set_location():
    data = request.get_json()
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
            if mt19937_instance.get_state_fraction() > 0.02: # TO DO CHANGE

                mt19937_instance = MT19937(seed=generate_TRN(32))
                print("Created a new instance of MT19937")
            # Generowanie i nadawanie session_token
            session_token = mt19937_instance.extract_number()
            drawn_numbers.append(session_token)
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    global mt19937_instance
    global active_tokens
    if request.method == 'POST':
        username_received = request.form['username']
        password_received = request.form['password']

        if authenticate_user(operators, username_received, password_received):
            # Utwórz sesję użytkownika i przekieruj go do strony głównej lub innej docelowej strony
            if mt19937_instance.get_state_fraction() > 0.02:
                mt19937_instance = MT19937(seed=generate_TRN(32))
                print("Created a new instance of MT19937")

            session_token = mt19937_instance.extract_number()
            drawn_numbers.append(session_token)
            active_tokens[username_received] = session_token

            return render_template('login.html', feedback="User " + username_received + " authenticated. Session Token: " + str(active_tokens[username_received]))

        else:
            # Jeżeli uwierzytelnianie nie powiedzie się, można przekierować użytkownika z powrotem do strony logowania z komunikatem
            return render_template('login.html', message='Invalid username or password')

    return render_template('login.html')


@app.route('/api/leak', methods=['GET'])
def leak():
    return drawn_numbers

if __name__ == '__main__':
    app.run()


'''
if __name__ == '__main__':
    ssl_cert_path = 'C:\\Users\\Wszemir\\dronessystem.mt.crt'
    ssl_key_path = 'C:\\Users\\Wszemir\\dronessystem.mt.key'

    app.run(host='0.0.0.0', ssl_context=(ssl_cert_path, ssl_key_path))


'''