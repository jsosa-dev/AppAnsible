from flask import render_template, request, jsonify, make_response
import paramiko
import ansible_runner
import subprocess
from config.db import Database

db = Database()

collection_host = "hosts"

def index():
    return render_template('index.html')

def dashboard():

    hosts = list(db.find_all('hosts'))
    return render_template('dashboard.html', hosts=hosts)

def inventory():
    return render_template('inventory.html')

def save_host():
    # Obtener datos del cuerpo de la solicitud POST
    ip = request.json.get('ip')
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')

    # Guardar los datos en la base de datos
    db.insert_one(collection_host, {
        "name": name,
        "ip": ip,
        "username": username,
        "password": password,
    })

    return jsonify({'success': True, 'message': 'Datos guardados correctamente'})

def save_group():
    name = request.json.get('name')
    db.insert_one(collection_group, {
        "name": name,
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

def execute_playbook():
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
