from src.controllers import (
    dashboard,
    execute_playbook,
    index,
    save_host,
    save_group,
    inventory,
    ssh_command,
)
def setup_routes(app):
    app.add_url_rule('/', view_func=index)
    app.add_url_rule('/dashboard', view_func=dashboard)
    app.add_url_rule('/inventory', view_func=inventory)
    app.add_url_rule('/save_host', view_func=save_host, methods=['POST'])
    app.add_url_rule('/ssh', view_func=ssh_command, methods=['POST'])
    app.add_url_rule('/ex_playbook', view_func=execute_playbook, methods=['POST'])
