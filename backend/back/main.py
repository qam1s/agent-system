from .ioc import get_app

app = get_app()

_container = app.state.container
graph = _container.graph


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
