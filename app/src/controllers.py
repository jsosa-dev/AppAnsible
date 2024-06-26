from flask import render_template, request, jsonify, make_response
import paramiko
import ansible_runner
import subprocess
import yaml
from cryptography.fernet import Fernet
import base64
import os
import re
import uuid
from config.db import Database
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('KEY')
cipher_suite = Fernet(key)
cipher_suite = Fernet(key)

db = Database()

collection_host = "hosts"
collection_task = "tasks"

def initialize_default_data():
    print("Se inserta informacion de inicio")
    default_task = [
        {"name": "Obtener version de python", "path": "27d7d7ee-52a0-4ede-93dc-f5a74eb6d79f.yml"},
        {"name": "Obtener la hora del servidor", "path": "354a9613-59d8-4b84-bd4c-970fa10d8b1f.yml"},
        {"name": "Obtener hostname del servidor", "path": "e42d12a9-010a-4f70-8d46-8dfc6e6ae338.yml"},
        {"name": "Obtener lista de usuarios", "path": "5411aa8f-8e3e-4107-9456-0833e6080644.yml"},
        {"name": "Instalar y ejecutar apache (Compatible con Debian y Centos)", "path": "c85e891c-27e2-4982-8cf0-c86a4d356e37.yml"},
    ]

    for task_data in default_task:
        existing_host = db.find_one(collection_task, {"name": task_data["name"]})
        if not existing_host:
            db.insert_one(collection_task, {
                "name": task_data["name"],
                "path": task_data["path"],
            })

initialize_default_data()

def index():
    return render_template('index.html')

def about():
    return render_template('about.html')

def dashboard():
    hosts = list(db.find_all('hosts'))
    tasks = list(db.find_all('tasks'))
    return render_template('dashboard.html', hosts=hosts, tasks=tasks)

def task():
    return render_template('task.html')


def inventory():
    return render_template('inventory.html')

def save_host():
    # Obtener datos del cuerpo de la solicitud POST
    ip = request.json.get('ip')
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')
    encrypted_password = cipher_suite.encrypt(password.encode('utf-8'))

    # Guardar los datos en la base de datos
    db.insert_one(collection_host, {
        "name": name,
        "ip": ip,
        "username": username,
        "password": encrypted_password.decode('utf-8'),
    })

    return jsonify({'success': True, 'message': 'Datos guardados correctamente'})

def ssh_command():
    # Obtener el nombre del cuerpo de la solicitud POST
    name = request.json.get('name')
    command = request.json.get('command')

    # Buscar los datos de conexión en la base de datos
    record = db.find_one(collection_name, {"name": name})

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


UPLOAD_FOLDER = 'static/playbooks'
ALLOWED_EXTENSIONS = {'yml', 'yaml'} 
PATH_INVENTORY = 'static/playbooks/host.ini'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_task():
    name = request.form.get('name')
    hosts = request.form.get('hosts')  # Assuming you get the hosts dynamically

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400
        if file:
            filename = str(uuid.uuid4()) + '.yml'
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            # Read the YAML content to modify hosts section
            with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as f:
                yaml_content = f.read()

            # Modify the hosts section dynamically
            # yaml_content = yaml_content.replace('hosts: tu_servidor', f'hosts: web-inventory')
            yaml_content = re.sub(r'^\s*hosts:\s+.+$', f'  hosts: web_inventory', yaml_content, flags=re.MULTILINE)
            # Write the modified content back to the file
            with open(os.path.join(UPLOAD_FOLDER, filename), 'w') as f:
                f.write(yaml_content)

            db.insert_one(collection_task, {"name": name, "path": filename})
            return jsonify({"message": "Archivo cargado y guardado exitosamente"}), 200

    return jsonify({"error": "No se proporcionó archivo"}), 400

def execute_playbook():

    try:
        resultado = ""
        tasks = request.json.get('tasks')
        hosts = request.json.get('hosts')        
        if not tasks:
            return jsonify({"error": "No tasks provided"}), 400

        with open(PATH_INVENTORY, 'w', encoding='utf-8') as host_file:
            host_file.write('[web_inventory]\n')
            for host in hosts:
                ip = host['ip']
                host_id = host['id']
                db_host = db.find_one('hosts', {'_id': ObjectId(host_id)})
                if db_host:
                    username = db_host.get('username', 'root')  # usuario por defecto si no se encuentra
                    encrypted_password = db_host.get('password')
                    decrypted_password = cipher_suite.decrypt(encrypted_password.encode('utf-8')).decode('utf-8')
                    #password = db_host.get('password', 'root')  # contraseña por defecto si no se encuentra
                    host_file.write(f"{ip} ansible_user={username} ansible_ssh_pass={decrypted_password}\n")        

                else:
                    return jsonify({"error": f"Host with ID {host_id} not found"}), 404
        results = []

        for task in tasks:
            playbook_path = "static/playbooks/" + task['path']

            ansible_command = [
                'ansible-playbook',
                playbook_path,
                '-i', PATH_INVENTORY,
            ]

            result = subprocess.run(ansible_command, capture_output=True, text=True)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if result.returncode == 0:
                results.append(result.stdout)
                
                #resultado = result.stdout
                resultado += result.stdout 
                respo = make_response(resultado)
                respo.headers['Content-Type'] = 'text/plain'

            else:
                results.append({"task": task, "status": "error", "stderr": stderr})
                respo = make_response(results)
                respo.headers['Content-Type'] = 'text/plain'

        return respo

    except Exception as e:
        return jsonify({'success': False, 'errores': str(e)})

    finally:
        '''
            if os.path.exists(PATH_INVENTORY):
            os.remove(PATH_INVENTORY)
        '''