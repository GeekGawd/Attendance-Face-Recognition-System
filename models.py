from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from dataclasses import dataclass

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

@dataclass
class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True, index=True)
    in_time = Column(DateTime, nullable=False, index=True)
    out_time = Column(DateTime, nullable=False, index=True)
    student = relationship("Student", back_populates="attendance")

    def to_dict(self):
        return {
            'student': self.student[0].name if self.student else None,
            'in_time': self.in_time,
            'out_time': self.out_time,
        }

class Student(Base):
    __tablename__ = "student"
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    attendance_id = Column(Integer, ForeignKey("attendance.id"))
    attendance = relationship("Attendance", back_populates="student")   

    def to_dict(self):
            return {
                'id': self.id,
                'name': self.name
            }