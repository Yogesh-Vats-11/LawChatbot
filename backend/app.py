from flask import Flask
from flask_cors import CORS

from routes.chat_routes import chat_bp
from routes.fir_routes import fir_bp
from routes.rti_routes import rti_bp
from routes.consumer_routes import consumer_bp
from routes.document_routes import document_bp
#dont add api thing right now {from routes.api_routes import api_bp}

app = Flask(__name__)
CORS(app)

app.register_blueprint(chat_bp)
app.register_blueprint(fir_bp)
app.register_blueprint(rti_bp)
app.register_blueprint(consumer_bp)
app.register_blueprint(document_bp)
#dont add api thing right now {app.register_blueprint(api_bp)}
@app.route("/")
def home():
    return {"status": "running", "system": "LegalAI Connected"}

if __name__ == "__main__":
    app.run(debug=True)