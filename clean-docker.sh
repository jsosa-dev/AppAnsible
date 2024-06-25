#!/bin/bash
# Script para detener y limpiar todos los recursos de Docker

# Detener todos los contenedores en ejecución
echo "Deteniendo todos los contenedores..."
docker stop $(docker ps -aq)

# Eliminar todos los contenedores detenidos
echo "Eliminando todos los contenedores detenidos..."
docker rm $(docker ps -aq)

# Eliminar todas las imágenes
echo "Eliminando todas las imágenes..."
docker rmi $(docker images -q)

# Eliminar todos los volúmenes no utilizados
echo "Eliminando todos los volúmenes no utilizados..."
docker volume prune -f

# Eliminar todas las redes no utilizadas
echo "Eliminando todas las redes no utilizadas..."
docker network prune -f

echo "Limpieza completa de Docker realizada."
