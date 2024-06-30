import sys
sys.dont_write_bytecode = True

from flask import Flask
from livereload import Server
from routes.routes import setup_routes

app = Flask(__name__)

# Configurar las rutas
setup_routes(app)

if __name__ == '__main__':
    app.debug = True  # Enable template auto-reload in Flask
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')  # Watch for changes in all HTML templates
    server.serve(host='0.0.0.0', port=5000)  # Start the server with live reload
