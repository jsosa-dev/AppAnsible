from flask import Flask, render_template, request, jsonify, make_response
import paramiko
from pymongo import MongoClient
from livereload import Server
import ansible_runner
import subprocess


app = Flask(__name__)

# Conectar a MongoDB
client = MongoClient("mongodb://mongo:27017/")  # Asegúrate de que esta URI sea correcta para tu configuración
db = client["ansiblewebdb"]  # Nombre de tu base de datos
collection = db["auth-master"]  # Nombre de tu colección

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    names = collection.distinct("name")
    return render_template('dashboard.html', names=names)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/save', methods=['POST'])
def save_to_db():
    # Obtener datos del cuerpo de la solicitud POST
    ip = request.json.get('ip')
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')

    # Guardar los datos en la base de datos
    collection.insert_one({
        "name": name,
        "ip": ip,
        "username": username,
        "password": password,
    })

    return jsonify({'success': True, 'message': 'Datos guardados correctamente'})

@app.route('/ssh', methods=['POST'])
def ssh_command():
    # Obtener el nombre del cuerpo de la solicitud POST
    name = request.json.get('name')
    command = request.json.get('command')

    # Buscar los datos de conexión en la base de datos
    record = collection.find_one({"name": name})

    if not record:
        return jsonify({'success': False, 'error': 'Registro no encontrado'})

    ip = record['ip']
    username = record['username']
    password = record['password']

    # Establecer conexión SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ip, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if error:
            return jsonify({'success': False, 'error': error.strip()})
        else:
            return jsonify({'success': True, 'output': output.strip()})

    except paramiko.AuthenticationException:
        return jsonify({'success': False, 'error': 'Authentication failed'})
    except paramiko.SSHException as e:
        return jsonify({'success': False, 'error': f'SSH connection error: {str(e)}'})
    finally:
        client.close()

@app.route('/ex_playbook', methods=['POST'])
def execute_playbook():
    # Obtener el nombre del cuerpo de la solicitud POST
    name = request.json.get('name')
    command = request.json.get('command')

    # Buscar los datos de conexión en la base de datos
    record = collection.find_one({"name": name})

    if not record:
        return jsonify({'success': False, 'error': 'Registro no encontrado'})

    ip = record['ip']
    username = record['username']
    password = record['password']

    try:

        subprocess.run(['apt-get', 'update'], check=True)
        subprocess.run(['apt-get', 'install', 'sshpass'], check=True)
  
        # Definir la tarea de Ansible
        tasks = [
            {
                'name': 'Obtener hostname',
                'hosts': 'all',
                'gather_facts': 'no',
                'tasks': [
                    {
                        'name': 'Ejecutar comando hostname',
                        'command': command
                    }
                ]
            }
        ]

        # Definir el inventario dinámico
        inventory = {
            'all': {
                'hosts': {
                    ip: {
                        'ansible_user': username,
                        'ansible_ssh_pass': password,
                        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
                    }
                }
            }
        }

        # Ejecutar la tarea de Ansible
        result = ansible_runner.run(
            private_data_dir='/tmp/', 
            inventory=inventory, 
            playbook=tasks,
            quiet=False,)

        resultado = result.stdout
        response = make_response(resultado)
        response.headers['Content-Type'] = 'text/plain'
        return response

    except Exception as e:
        return jsonify({'success': False, 'errores': str(e)})

if __name__ == '__main__':
    app.debug = True  # Enable template auto-reload in Flask
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')  # Watch for changes in all HTML templates
    server.serve(host='0.0.0.0', port=5000)  # Start the server with live reload
