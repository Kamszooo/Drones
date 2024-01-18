import threading
import time
from flask import Flask, request, render_template
from PRNG import MT19937
from TRNG import generate_TRN
import json
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

# Initial location
current_location = {'X': 50, 'Y': 50, 'Z': 50}
next_waypoint = {'X': 51, 'Y': 49, 'Z': 49}

#generate instance of the PRNG Twister with the seed drawn by TRNG
mt19937_instance = MT19937(seed=generate_TRN(32))


def updating():
  #  every 5 secund drawn move from the location to the next waypoint and draw new next waypoint
    while True:
        global next_waypoint
        global current_location
        global mt19937_instance
 #       print("Next waypoint po śnie:" + str(next_waypoint))
        print("Current location:  " + str(current_location))
        print("Next waypoint:  " + str(next_waypoint))


        if mt19937_instance.get_state_fraction() > 0.5:  # when PRNG has run through more than half of its internal states, create a new instance with the fresh seed
            mt19937_instance = MT19937(seed=generate_TRN(32))
            print("Created a new instance of MT19937")
        new_random = mt19937_instance.extract_number()
        drawn_numbers.append(new_random)
        new_x = new_random / 4294967295 * 100 # the maximum number possible to drawn is 2^32-1 = 4294967295
        new_random = mt19937_instance.extract_number()
        drawn_numbers.append(new_random)
        new_y = new_random / 4294967295 * 100
        new_random = mt19937_instance.extract_number()
        drawn_numbers.append(new_random)
        new_z = new_random / 4294967295 * 100

        # update location and new next waypoint
        current_location = next_waypoint
        next_waypoint = {'X': new_x, 'Y': new_y, 'Z': new_z}


        print(f"Current location changed to the previous next waypoint and set at {current_location}. New next waypoint drawn at: {next_waypoint}")
     #   print("Next waypoint before 5 s sleep:" + str(next_waypoint))
        time.sleep(5)

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
        if 100 >= data['X'] >= 0 and 100 >= data['Y'] >= 0 and 100 >= data['Z'] >= 0:
            new_location = {'X': data['X'], 'Y': data['Y'], 'Z': data['Z']}
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
        if 100 >= data['X'] >= 0 and 100 >= data['Y'] >= 0 and 100 >= data['Z'] >= 0:
            new_waypoint = {'X': data['X'], 'Y': data['Y'], 'Z': data['Z']}
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
            if mt19937_instance.get_state_fraction() > 0.5: # when PRNG has run through more than half of its internal states, create a new instance with the fresh seed

                mt19937_instance = MT19937(seed=generate_TRN(32))
                print("Created a new instance of MT19937")
            session_token = mt19937_instance.extract_number() #generate the session token
            drawn_numbers.append(session_token)
            active_tokens[username_received] = session_token
            print(active_tokens)

            return "User " + username_received + " authenticated. Session Token: " + str(active_tokens[username_received])
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
            if mt19937_instance.get_state_fraction() > 0.5: # when PRNG has run through more than half of its internal states, create a new instance with the fresh seed
                mt19937_instance = MT19937(seed=generate_TRN(32))
                print("Created a new instance of MT19937")

            session_token = mt19937_instance.extract_number()
            drawn_numbers.append(session_token)
            active_tokens[username_received] = session_token

            return render_template('login.html', feedback="User " + username_received + " authenticated. Session Token: " + str(active_tokens[username_received]))

        else:
            return render_template('login.html', message='Invalid username or password')

    return render_template('login.html')


@app.route('/api/leak', methods=['GET'])
def leak():
    return drawn_numbers



if __name__ == '__main__':
    app.run()


''' The run version with SSL certificates:
if __name__ == '__main__':
    ssl_cert_path = 'C:\\Users\\Wszemir\\dronessystem.mt.crt'
    ssl_key_path = 'C:\\Users\\Wszemir\\dronessystem.mt.key'

    app.run(host='0.0.0.0', ssl_context=(ssl_cert_path, ssl_key_path))
'''


