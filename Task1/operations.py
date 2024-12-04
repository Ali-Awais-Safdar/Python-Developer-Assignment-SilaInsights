from fastapi import HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Student, Subject, Teacher
from schemas import StudentBase, TeacherBase, SubjectBase
import csv
import io
from sqlalchemy import desc

class BaseOperations:
    def paginate_query(self, query, page: int = 1, page_size: int = 10):
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(status_code=400, detail="Page number must be greater than 0")
        if page_size < 1:
            raise HTTPException(status_code=400, detail="Page size must be greater than 0")
        if page_size > 100:  # Add maximum page size limit
            raise HTTPException(status_code=400, detail="Page size cannot exceed 100")
            
        return query.offset((page - 1) * page_size).limit(page_size)

class StudentOperations(BaseOperations):
    def get_students(self, db: Session, page: int = 1, page_size: int = 10):
        query = db.query(Student)
        total = query.count()
        students = self.paginate_query(query, page, page_size).all()
        
        return {
            "items": [self.get_student_data(db, student.id) for student in students],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

    def get_student_data(self, db: Session, student_id: int):
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "subjects": [{"id": subject.id, "name": subject.name} for subject in student.subjects]
        }

    def insert_student(self, db: Session, student_data: StudentBase):
        try:
            student = Student(name=student_data.name, email=student_data.email)
            db.add(student)
            db.commit()
            
            response = {"student_id": student.id, "successfully_linked_subjects": [], "failed_subjects": []}
            
            if student_data.subject_ids:
                subjects = db.query(Subject).filter(Subject.id.in_(student_data.subject_ids)).all()
                student.subjects.extend(subjects)
                db.commit()
                db.refresh(student)
                
                response["successfully_linked_subjects"] = [{"id": subject.id, "name": subject.name} for subject in subjects]
                response["failed_subjects"] = list(set(student_data.subject_ids) - {subject.id for subject in subjects})
                
            return response
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Email already exists in the database"
            )

    def update_student(self, db: Session, student_id: int, student_data: dict):
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        if "name" in student_data:
            student.name = student_data["name"]
        if "email" in student_data:
            student.email = student_data["email"]
        if "subject_ids" in student_data:
            student.subjects = []
            subjects = db.query(Subject).filter(Subject.id.in_(student_data["subject_ids"])).all()
            student.subjects.extend(subjects)
        
        db.commit()
        return self.get_student_data(db, student_id)
    
    def remove_subject_student(self, db: Session, student_id: int, subject_id: int):
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
            
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
            
        if subject not in student.subjects:
            raise HTTPException(status_code=404, detail="Subject not assigned to this student")
            
        student.subjects.remove(subject)
        db.commit()
        return self.get_student_data(db, student_id)

class TeacherOperations(BaseOperations):
    def get_teachers(self, db: Session, page: int = 1, page_size: int = 10):
        query = db.query(Teacher)
        total = query.count()
        teachers = self.paginate_query(query, page, page_size).all()
        
        return {
            "items": [self.get_teacher_data(db, teacher.id) for teacher in teachers],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

    def get_teacher_data(self, db: Session, teacher_id: int):
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        return {
            "id": teacher.id,
            "name": teacher.name,
            "email": teacher.email,
            "subjects": [{"id": subject.id, "name": subject.name} for subject in teacher.subjects]
        }

    def insert_teacher(self, db: Session, teacher_data: TeacherBase):
        teacher = Teacher(name=teacher_data.name, email=teacher_data.email)
        db.add(teacher)
        db.commit()

        response = {"teacher_id": teacher.id, "successfully_linked_subjects": [], "failed_subjects": []}

        if teacher_data.subject_ids:
            subjects = db.query(Subject).filter(Subject.id.in_(teacher_data.subject_ids)).all()
            teacher.subjects.extend(subjects)
            db.commit()
            db.refresh(teacher)

            response["successfully_linked_subjects"] = [{"id": subject.id, "name": subject.name} for subject in subjects]
            response["failed_subjects"] = list(set(teacher_data.subject_ids) - {subject.id for subject in subjects})

        return response

    def update_teacher(self, db: Session, teacher_id: int, teacher_data: dict):
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

        if "name" in teacher_data:
            teacher.name = teacher_data["name"]
        if "email" in teacher_data:
            teacher.email = teacher_data["email"]
        if "subject_ids" in teacher_data:
            teacher.subjects = []
            subjects = db.query(Subject).filter(Subject.id.in_(teacher_data["subject_ids"])).all()
            teacher.subjects.extend(subjects)
        
        db.commit()
        return self.get_teacher_data(db, teacher_id)
    
    def remove_subject_teacher(self, db: Session, teacher_id: int, subject_id: int):
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
            
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
            
        if subject not in teacher.subjects:
            raise HTTPException(status_code=404, detail="Subject not assigned to this teacher")
            
        teacher.subjects.remove(subject)
        db.commit()
        return self.get_teacher_data(db, teacher_id)

class SubjectOperations(BaseOperations):
    def get_subjects(self, db: Session, page: int = 1, page_size: int = 10):
        query = db.query(Subject)
        total = query.count()
        subjects = self.paginate_query(query, page, page_size).all()
        
        return {
            "items": [self.get_subject_data(db, subject.id) for subject in subjects],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

    def get_subject_data(self, db: Session, subject_id: int):
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        return {
            "id": subject.id,
            "name": subject.name,
            "students": [{"id": student.id, "name": student.name, "email": student.email} 
                        for student in subject.students],
            "teachers": [{"id": teacher.id, "name": teacher.name, "email": teacher.email} 
                        for teacher in subject.teachers]
        }

    def insert_subject(self, db: Session, name: str):
        subject = Subject(name=name)
        db.add(subject)
        db.commit()
        db.refresh(subject)
        return subject

    def update_subject(self, db: Session, subject_id: int, subject_data: dict):
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        if "name" in subject_data:
            subject.name = subject_data["name"]
        
        db.commit()
        return self.get_subject_data(db, subject_id)