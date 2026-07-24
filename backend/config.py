import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BNS_PATH = os.path.join(BASE_DIR, "data", "bns.json")
GRAPH_PATH = os.path.join(BASE_DIR, "data", "legal_graph.json")
API_KEYS_FILE = os.path.join(BASE_DIR, "data", "api_keys.json")