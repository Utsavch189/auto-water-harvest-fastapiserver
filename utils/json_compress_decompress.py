import gzip
import json

def compress(python_dict:dict):
    json_data = json.dumps(python_dict)
    return gzip.compress(json_data.encode('utf-8'))

def decompress(compressed_data:bytes):
    decompressed_data = gzip.decompress(compressed_data)
    return json.loads(decompressed_data.decode('utf-8'))