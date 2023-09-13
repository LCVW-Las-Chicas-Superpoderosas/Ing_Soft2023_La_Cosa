## Grupo Chicas Super Poderosas



### KickStart:
* Se recomienda usar entorno svirtuales: pyenv, virtualenv, etc.
   
        Instalacion pyenv: https://realpython.com/intro-to-pyenv/   
    (Leer bien y seguir paso a paso...)

* Instalacion de requerimientos:
  
      pip install -r requirements.txt

* Correr hello_world:
  
          uvicorn main:app --reload

    Esto iniciará el servidor de desarrollo de FastAPI. La opción --reload permite que el servidor se reinicie automáticamente cuando hagas cambios en tu código.    
    Ahora, si abres un navegador web o utiliza una herramienta como curl o Postman para hacer una solicitud GET a la url que te aparecera en consola.
    Deberías recibir la respuesta "Hello, World!".
