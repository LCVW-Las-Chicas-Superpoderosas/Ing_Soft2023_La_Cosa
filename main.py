from fastapi import FastAPI

# Crea una instancia de la aplicación FastAPI
app = FastAPI()


# Define un endpoint (ruta) que responde a la raíz "/"
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
