from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return Title('Test'), Main(H1('Hello from 311 Dashboard!'))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5004)
