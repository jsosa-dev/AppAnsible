# Utiliza una imagen base de Python
FROM python:3.12.4-bullseye

# Establece el directorio de trabajo
WORKDIR /main

# Copia los archivos de la aplicación a la imagen
COPY ./ /main/
COPY requirements.txt /main

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Instala herramienta de ping
RUN apt-get update && \
    apt-get install -y iputils-ping

# Instala sshpass
RUN apt-get install -y sshpass

# Exponer el puerto que usa la aplicación Flask
EXPOSE 5000

# Define el comando para correr la aplicación
#CMD ["flask", "run"]
CMD ["python", "app.py"]
