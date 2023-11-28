import typing
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response
from face_verify import faceRec
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from database import create_students_from_subdolder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Attendance
import json
import datetime
from typing import Any


camera = faceRec()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        return obj.strftime("%m/%d/%Y, %H:%M:%S")
    raise TypeError ("Type %s not serializable" % type(obj))


create_students_from_subdolder()

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def gen(camera):
    while True:
        frame = camera.main()
        if frame != "":
            global_frame = frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen(camera), media_type='multipart/x-mixed-replace; boundary=frame')

class CustomJSONResponse(JSONResponse):

    def render(self, content: Any) -> bytes:
        return json.dumps([attendance.to_dict() for attendance in content], default=json_serial).encode("utf-8")
    
@app.get("/report")
def get_report():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///students.sqlite')

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Create a Session
    session = Session()

    attendances = session.query(Attendance).all()

    # attendance_json = json.dumps([attendance.to_dict() for attendance in attendances], default=json_serial)

    # for attendance in attendance_json:
    #     attendance['in_time'] = attendance['in_time'].strftime("%m/%d/%Y, %H:%M:%S")
    #     attendance['out_time'] = attendance['out_time'].strftime("%m/%d/%Y, %H:%M:%S")

    return CustomJSONResponse(content=attendances)    

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
