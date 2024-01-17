import json
import uuid
import bcrypt
import base64

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


def main():
    operators_filename = 'operators.json'
    operators = load_operators(operators_filename)

    # Przyjmowanie danych JSON z loginem i hasłem
    input_data = '{"username": "User1", "password": "ywFzCOiwxYuf"}'
    login_credentials = json.loads(input_data)

    username = login_credentials['username']
    password = login_credentials['password']

    # Weryfikacja użytkownika
    if authenticate_user(operators, username, password):
        # Generowanie i nadawanie session_token
        session_token = str(uuid.uuid4())
        print(f"User {username} authenticated. Session Token: {session_token}")

        # Dodanie session_token do danych operatora
        for operator in operators:
            if operator['username'] == username:
                operator['session_token'] = session_token

        # Zapisanie zaktualizowanej listy operatorów
        save_operators(operators_filename, operators)
    else:
        print("Authentication failed. Invalid username or password.")

if __name__ == "__main__":
    main()
