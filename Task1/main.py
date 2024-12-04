from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from typing import Optional
import csv
from io import StringIO
from schemas import StudentBase, TeacherBase, SubjectBase, TeacherPatchSchema, StudentPatchSchema
from operations import StudentOperations, TeacherOperations, SubjectOperations

app = FastAPI()
student_ops = StudentOperations()
teacher_ops = TeacherOperations()
subject_ops = SubjectOperations()

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/students/")
async def get_students(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    return student_ops.get_students(db, page, page_size)

@app.get("/students/{student_id}")
async def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    return student_ops.get_student_data(db, student_id)

@app.post("/students/")
async def create_student(
    student: StudentBase,
    db: Session = Depends(get_db)
):
    return student_ops.insert_student(db, student)

@app.put("/students/{student_id}")
async def update_student(
    student_id: int,
    student: StudentBase,
    db: Session = Depends(get_db)
):
    return student_ops.update_student(db, student_id, student.dict())

@app.patch("/students/{student_id}")
async def patch_student(
    student_id: int,
    student: StudentPatchSchema,
    db: Session = Depends(get_db)
):
    update_data = {k: v for k, v in student.dict().items() if v is not None}
    return student_ops.update_student(db, student_id, update_data)

@app.delete("/students/{student_id}/subjects/{subject_id}")
async def remove_subject_from_student(
    student_id: int,
    subject_id: int,
    db: Session = Depends(get_db)
):
    return student_ops.remove_subject_student(db, student_id, subject_id)

# Teacher routes
@app.get("/teachers/")
async def get_teachers(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    return teacher_ops.get_teachers(db, page, page_size)

@app.get("/teachers/{teacher_id}")
async def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db)
):
    return teacher_ops.get_teacher_data(db, teacher_id)

@app.post("/teachers/")
async def create_teacher(
    teacher: TeacherBase,
    db: Session = Depends(get_db)
):
    return teacher_ops.insert_teacher(db, teacher)

@app.put("/teachers/{teacher_id}")
async def update_teacher(
    teacher_id: int,
    teacher: TeacherBase,
    db: Session = Depends(get_db)
):
    return teacher_ops.update_teacher(db, teacher_id, teacher.dict())

@app.patch("/teachers/{teacher_id}")
async def patch_teacher(
    teacher_id: int,
    teacher: TeacherPatchSchema,
    db: Session = Depends(get_db)
):
    update_data = {k: v for k, v in teacher.dict().items() if v is not None}
    return teacher_ops.update_teacher(db, teacher_id, update_data)

@app.delete("/teachers/{teacher_id}/subjects/{subject_id}")
async def remove_subject_from_teacher(
    teacher_id: int,
    subject_id: int,
    db: Session = Depends(get_db)
):
    return teacher_ops.remove_subject_teacher(db, teacher_id, subject_id)

# Subject routes
@app.get("/subjects/")
async def get_subjects(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    return subject_ops.get_subjects(db, page, page_size)

@app.get("/subjects/{subject_id}")
async def get_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    return subject_ops.get_subject_data(db, subject_id)

@app.post("/subjects/")
async def create_subject(
    subject: SubjectBase,
    db: Session = Depends(get_db)
):
    return subject_ops.insert_subject(db, subject.name)

@app.put("/subjects/{subject_id}")
async def update_subject(
    subject_id: int,
    subject: SubjectBase,
    db: Session = Depends(get_db)
):
    return subject_ops.update_subject(db, subject_id, subject.dict())

@app.patch("/subjects/{subject_id}")
async def patch_subject(
    subject_id: int,
    subject: SubjectBase,
    db: Session = Depends(get_db)
):
    update_data = {k: v for k, v in subject.dict().items() if v is not None}
    return subject_ops.update_subject(db, subject_id, update_data)

#CSV Upload
@app.post("/upload-csv/")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be a CSV file"
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    try:
        content = content.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(content))
        
        required_fields = {'name', 'email'}  # Only 'name' and 'email' are strictly required
        optional_fields = {'subject_ids'}  # Optional fields
        
        # Validate headers dynamically
        headers = set(csv_reader.fieldnames) if csv_reader.fieldnames else set()
        missing_required_fields = required_fields - headers
        
        if missing_required_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_required_fields)}"
            )

        results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }

        for row_number, row in enumerate(csv_reader, start=1):
            try:
                if any(not row.get(field) for field in required_fields):
                    results["skipped"].append({
                        "row_number": row_number,
                        "row": row,
                        "reason": "Missing or empty required fields"
                    })
                    continue

                subject_ids = []
                if 'subject_ids' in headers and row.get('subject_ids'):
                    try:
                        subject_ids = [
                            int(id.strip()) 
                            for id in row['subject_ids'].replace('"', '').split(',') 
                            if id.strip()
                        ]
                    except ValueError:
                        raise ValueError("Invalid subject_ids format. Expected comma-separated integers.")
                    
                student_data = StudentBase(
                    name=row['name'],
                    email=row['email'],
                    subject_ids=subject_ids
                )
                
                # Attempt to insert the student
                result = student_ops.insert_student(db, student_data)
                results["successful"].append({
                    "row_number": row_number,
                    "name": row['name'],
                    "email": row['email'],
                    "student_id": result["student_id"]
                })

            except Exception as e:
                results["failed"].append({
                    "row_number": row_number,
                    "row": row,
                    "error": str(e)
                })

        # Generate response
        if not results["successful"] and results["failed"]:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "No records were successfully imported",
                    "errors": results["failed"]
                }
            )

        return {
            "summary": {
                "total_rows": row_number,
                "successful": len(results["successful"]),
                "failed": len(results["failed"]),
                "skipped": len(results["skipped"])
            },
            "results": results
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File is not properly encoded. Please ensure it's saved as UTF-8"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing CSV file: {str(e)}"
        )
