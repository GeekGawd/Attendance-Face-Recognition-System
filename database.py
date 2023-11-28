from datetime import datetime
from sqlalchemy import func
from models import Student, Attendance


from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os


def create_students_from_subdolder():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///students.sqlite')

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Create a Session
    session = Session()
    # Get all subfolder names from the 'facebank' folder
    folder_path = './data/facebank'
    subfolder_names = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]

    # Insert the names into the Student table if they don't already exist
    for name in subfolder_names:
        # Check if a student with this name already exists
        student = session.query(Student).filter_by(name=name).first()
        if not student:
            # If not, create a new Student object and add it to the session
            new_student = Student(name=name)
            session.add(new_student)

    # Commit the changes to the database
    session.commit()
    print("Creted Users")
    # Close the session 
    session.close()

def mark_attendance_db(name):
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///students.sqlite')

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Create a Session
    session = Session()
    print(name)
    # Get today's date
    # Get today's date
    today = datetime.today().date()

    # Get the student_id for a given name
    student_id_result = session.execute(text("SELECT id FROM student WHERE name = :name LIMIT 1;"), {"name": name}).fetchone()
    if student_id_result is None:
        print(f"No student found with name {name}")
        session.close()
        return
    student_id = student_id_result[0]

    # Check if an attendance entry for today already exists for the student_id
    attendance_result = session.execute(text("SELECT * FROM attendance INNER JOIN student ON attendance.id = student.attendance_id WHERE student.id = :student_id AND DATE(attendance.in_time) = :today LIMIT 1;"), {"student_id": student_id, "today": today}).fetchone()

    now = datetime.now()
    if attendance_result is not None:
        # If an entry exists, update the out_time
        session.execute(text("UPDATE attendance SET out_time = :now WHERE id = :attendance_id;"), {"now": now, "attendance_id": attendance_result[0]})
    else:
        # If no entry exists, create a new one
        session.execute(text("INSERT INTO attendance (in_time, out_time) VALUES (:now, :now);"), {"now": now})
        last_row_id = session.execute(text("SELECT last_insert_rowid();")).scalar()
        session.execute(text("UPDATE student SET attendance_id = :last_row_id WHERE id = :student_id;"), {"last_row_id": last_row_id, "student_id": student_id})

    # Commit the changes to the database
    session.commit()

    # Close the session
    session.close()