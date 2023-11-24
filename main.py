from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from face_verify import faceRec
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

camera = faceRec()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def gen(camera):
    while True:
        frame = camera.main()
        if frame != "":
            global_frame = frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(gen(camera), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
