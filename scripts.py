import uvicorn

def run_dev():
    uvicorn.run("app.main:app", reload=True)