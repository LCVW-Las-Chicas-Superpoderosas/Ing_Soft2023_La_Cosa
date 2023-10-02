# La Cosa: Versión Web (Backend)

## Grupo Chicas Super Poderosas

## Descripción

Este es el backend del proyecto que implementa el juego de cartas "La Cosa" en versión web.
Proporciona una API para gestionar tanto la lógica del juego como las acciones y la información de los jugadores.

## Requisitos Previos

Asegúrate de tener los siguientes requisitos previos instalados antes de continuar:

- Python [3.10.12](https://www.python.org/downloads/release/python-31012/)
- Entorno virtual (recomendamos [pyenv](https://github.com/pyenv/pyenv))
- [pip](https://pip.pypa.io/en/stable/installation/)
- [uvicorn](https://www.uvicorn.org/)
- [npm](https://www.npmjs.com/get-npm)
- [mysql](https://www.mysql.com/)

## Instalación

1. Clona este repositorio.
2. Ingresa a la carpeta del proyecto
3. Asegurate de que mysql esté corriendo en tu máquina.
4. Crea un entorno virtual con Python 3.10.12.
5. Activa el entorno virtual.
6. Instala las dependencias con:

```shell
pip install -r requirements.txt
```

7. Modifica el archivo 'app/constants.py' con los datos de inicio de sesión de mysql.
8. Inicia el servidor con:

```shell
npm run start-server -- --host localhost --port 8000
```

9. En otra terminal, puedes probar el correcto funcionamiento de la API con:

```shell
npm run test
```
