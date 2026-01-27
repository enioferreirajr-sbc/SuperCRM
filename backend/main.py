from fastapi import FastAPI

app = FastAPI(title="SuperCRM API")

@app.get("/")
def read_root():
    return {"message": "Welcome to SuperCRM Backend"}
