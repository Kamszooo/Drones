import json
import base64
import random
import string
import bcrypt

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        return super().default(obj)

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_passes(user_index):
    username = f'User{user_index}'
    password = generate_random_string(12)

    salt, hashed_password = hash_password(password)
    print(salt)

    # Wyświetlanie informacji przed zapisem do pliku JSON
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Salt: {salt}")
    print(f"Hashed Password: {hashed_password}")
    print()

    return {'username': username, 'password': password, 'salt': salt, 'hashed_password': hashed_password}

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return salt, hashed_password

# Generowanie 6 par loginu i hasła
users_credentials = [generate_passes(i) for i in range(1, 2)]


with open("auxiliary.txt", 'w') as auxiliary_file:
    auxiliary_file.write('This file is generated only for your convenience during testing, so you know what your user password is, \n without the need to copy it on creation from the console. \n It plays no role in the application. In real-world your password shall be set by you and NEVER TO BE STORED by the application. \n \n Therefore, the original passes were NOT saved to  operators.json, which is the file used by the app. \n \n  IT ONLY STORES HASHES! \n \n')
    json.dump([{k: v for k, v in user.items()} for user in users_credentials], auxiliary_file, indent=2, cls=BytesEncoder)
# Zapisywanie do pliku JSON z użyciem niestandardowego kodera
with open("operators.json", 'w') as json_file:
    # Usunięcie oryginalnych haseł przed zapisem do pliku JSON
    json.dump([{k: v for k, v in user.items() if k != 'password'} for user in users_credentials], json_file, indent=2, cls=BytesEncoder)

print(f"Users salts and passwords hashes saved to operators.json")
print(f"\n For your convenience during teting, orginal passes were saved to 'auxiliary.txt' so you know what your user password is, without the need to copy it right now from the console. \n In real-world your password shall be set by you and  is NEVER TO BE STORED by the application. \n Therefore, the original passes were NOT saved to  'operators.json', which is used by the app!")