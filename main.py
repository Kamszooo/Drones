from flask import Flask, request
from PRNG import MT19937
from TRNG import generate_TRN
app = Flask(__name__)

# Przykładowa lokalizacja
current_location = {'latitude': 37.7749, 'longitude': -122.4194}

trn = generate_TRN(16)
mt19937_instance = MT19937(seed=trn)

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

    if 'latitude' in data and 'longitude' in data:
        new_location = {'latitude': data['latitude'], 'longitude': data['longitude']}
        current_location.update(new_location)
        return {'status': 'success', 'message': 'Location updated successfully'}
    else:
        return {'status': 'error', 'message': 'Invalid data format'}

if __name__ == '__main__':
    app.run(debug=True)
