from flask import Flask, render_template, request, jsonify
import paramiko

from livereload import Server


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/ssh', methods=['POST'])
def ssh_command():
    # Obtener datos del cuerpo de la solicitud POST
    ip = request.json.get('ip')
    username = request.json.get('username')
    password = request.json.get('password')
    command = request.json.get('command')

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

if __name__ == '__main__':
    # app.run(port=5000, debug=True, host="0.0.0.0")
    app.debug = True  # Enable template auto-reload in Flask
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')  # Watch for changes in all HTML templates
    #server.serve()
    server.serve(host='0.0.0.0', port=5000)  # Start the server with live reload


    #app.run(debug=True)
