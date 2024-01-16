import json

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')  # Konwersja bajtów na tekst przy serializacji
        return super().default(obj)

def bytes_decoder(obj):
    if '__bytes__' in obj:
        return obj['__bytes__'].encode('utf-8')  # Konwersja tekst na bajty przy deserializacji
    return obj

# Przykładowe dane
text_data = {'message': 'Hello, World!', 'binary_data': b'\x48\x65\x6c\x6c\x6f'}

# Zakodowanie do JSON
json_data = json.dumps(text_data, cls=BytesEncoder)
print("Zakodowane JSON:", json_data)

# Odkodowanie z JSON
decoded_data = json.loads(json_data, object_hook=bytes_decoder)
print("Odkodowane dane:", decoded_data)