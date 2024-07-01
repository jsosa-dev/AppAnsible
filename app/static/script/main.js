let selectedHosts = [];

// Seleccion de elementos de UI
const modalHost = document.getElementById('modalHost');
const btnHost = document.getElementById('btnHost');
const btnCancelHost = document.getElementById('btnCancelHost');
const taskContainer = document.getElementById('taskBannersContainer');
const hostContainer = document.getElementById('hostBannersContainer');
const logMessage = document.getElementById("logMessage");
const loader = document.getElementById('loader');

let selectedTasks = [];
let btnPlay = document.getElementById("btnPlay");
let path, name = ""

btnHost.addEventListener("click", e => modalHost.showModal());
btnCancelHost.addEventListener("click", () => modalHost.close());

document.querySelectorAll('.btn-agregar-host').forEach(button => {
    button.addEventListener('click', function () {
        const ip = this.closest('div').getAttribute('data-ip');
        const id = this.closest('div').getAttribute('data-id');
        const container = document.getElementById('hostBannersContainer');

        const banner = document.createElement('nord-banner');
        banner.setAttribute('variant', 'info');
        banner.innerHTML = `IP: ${ip} <a href="#">Learn more</a>`;
        container.appendChild(banner);

        selectedHosts.push({ ip: ip, id: id });

        if (document.getElementById('bannerHost')) document.getElementById('bannerHost').classList.add('hidden');
        this.closest('div').classList.add('hidden');
    });
});


btnTask.addEventListener("click", e => modalTask.showModal());
btnCancelTask.addEventListener("click", () => modalTask.close());

document.querySelectorAll('.btn-agregar-task').forEach(button => {
    button.addEventListener('click', function () {

        path = this.closest('div').getAttribute('data-path');
        name = this.closest('div').getAttribute('data-name');
        selectedTasks.push({ name: name, path: path });

        const taskBanner = document.createElement('nord-banner');
        taskBanner.setAttribute('variant', 'info');
        taskBanner.innerHTML = `Nombre: ${name}`;
        taskContainer.appendChild(taskBanner);
        if (document.getElementById('bannerTask')) document.getElementById('bannerTask').classList.add('hidden');
        this.closest('div').classList.add('hidden');

        //modalTask.close(); // Cierra el modal al terminar
    });
});


btnPlay.addEventListener("click", e => {
    modalConfirm.close()
    logMessage.innerHTML = ""; // Limpia el mensaje de registro
    loader.classList.remove('hidden')
    logMessage.classList.add('hidden')
    postData('/ex_playbook', { tasks: selectedTasks, hosts: selectedHosts })
        .then(response => {

            if (response.includes("error")) {
                logMessage.removeAttribute('variant');
                logMessage.setAttribute('variant', 'danger');
            } else {
                logMessage.removeAttribute('variant');
                logMessage.setAttribute('variant', 'success');
            }

            formattedResponse = response
                .replace(/\*/g, '<span class="text-[#000] font-bold">-</span>')
                .replace(/\n/g, '<br>');

            logMessage.innerHTML = formattedResponse;


            resetUI()
        })
        .catch(error => {
            console.error('Error al enviar datos:', error);
            resetUI()
        })
        .finally(() => {
            loader.classList.add('hidden')
            logMessage.classList.remove('hidden')
        });
    ;
});


function resetUI() {
    selectedHosts = [];
    selectedTasks = [];
    taskContainer.innerHTML = ""; // Limpiar contenedor de tareas
    hostContainer.innerHTML = "";
    taskContainer.innerHTML = "";

    document.querySelectorAll('.btn-agregar-host, .btn-agregar-task').forEach(button => {
        button.closest('div').classList.remove('hidden');
    });

    document.getElementById('bannerHost').classList.remove('hidden')
    document.getElementById('bannerTask').classList.remove('hidden')

    if (modalHost.open) {
        modalHost.close();
    }

    if (modalTask.open) {
        modalTask.close();
    }
}


