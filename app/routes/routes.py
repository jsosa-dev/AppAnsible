from src.controllers import (
    dashboard,
    task,
    execute_playbook,
    index,
    about,
    save_host,
    save_task,
    inventory,
    ssh_command,
)
def setup_routes(app):
    app.add_url_rule('/', view_func=index)
    app.add_url_rule('/dashboard', view_func=dashboard)
    app.add_url_rule('/about', view_func=about)
    app.add_url_rule('/inventory', view_func=inventory)
    app.add_url_rule('/task', view_func=task)
    app.add_url_rule('/save_host', view_func=save_host, methods=['POST'])
    app.add_url_rule('/save_task', view_func=save_task, methods=['POST'])
    app.add_url_rule('/ssh', view_func=ssh_command, methods=['POST'])
    app.add_url_rule('/ex_playbook', view_func=execute_playbook, methods=['POST'])
