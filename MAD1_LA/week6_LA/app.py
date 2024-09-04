from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from werkzeug.exceptions import HTTPException
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///api_database.sqlite3"
db = SQLAlchemy(app)
api = Api(app)
app.app_context().push()

# ---------------------------------- Models ---------------------------------- #
class student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)

class enrollment(db.Model):
    __tablename__ = "enrollment"
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable=False)

course_fields = {
    "course_id": fields.Integer,
    "course_code": fields.String,
    "course_name": fields.String,
    "course_description": fields.String,
}

student_fields = {
    "student_id": fields.Integer,
    "roll_number": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
}

enrollments_fields = {
    "enrollment_id": fields.Integer,
    "student_id": fields.Integer,
    "course_id": fields.Integer,
}

course_reqparse = reqparse.RequestParser()
course_reqparse.add_argument("course_code")
course_reqparse.add_argument("course_name")
course_reqparse.add_argument("course_description")

student_reqparse = reqparse.RequestParser()
student_reqparse.add_argument("roll_number")
student_reqparse.add_argument("first_name")
student_reqparse.add_argument("last_name")

enrollment_reqparse = reqparse.RequestParser()
enrollment_reqparse.add_argument("course_id")

class NotFound(HTTPException):
    def __init__(self, status_code):
        self.response = make_response("", status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        print(message)
        self.response = make_response(json.dumps(message), status_code)

class CourseAPI(Resource):
    @marshal_with(course_fields)
    def get(self, course_id):
        Course = course.query.filter_by(course_id=course_id).first()
        if Course:
            return Course
        else:
            raise NotFound(status_code=404)

    @marshal_with(course_fields)
    def delete(self, course_id):
        Course = course.query.filter_by(course_id=course_id).first()
        if Course:
            db.session.delete(Course)
            db.session.commit()
            return 200
        else:
            raise NotFound(status_code=404)

    @marshal_with(course_fields)
    def put(self, course_id):
        args = course_reqparse.parse_args()
        Course = course.query.filter_by(course_id=course_id).first()
        if Course:

            Course.course_name = args["course_name"]
            if Course.course_name is None:
                raise BusinessValidationError(
                    status_code=400,
                    error_code="COURSE001",
                    error_message="Course Name is required",
                )

            Course.course_code = args["course_code"]
            if Course.course_code is None:
                raise BusinessValidationError(
                    status_code=400,
                    error_code="COURSE002",
                    error_message="Course Code is required",
                )
            if "course_description" in args:
                Course.course_description = args["course_description"]

            db.session.commit()
            return Course, 200
        else:
            raise NotFound(status_code=404)

    @marshal_with(course_fields)
    def post(self):
        args = course_reqparse.parse_args()
        course_name = args["course_name"]
        course_code = args["course_code"]
        course_description = args["course_description"]
        courses = course.query.all()

        if course_code in [i.course_code for i in courses]:
            raise NotFound(status_code=409)

        if course_name is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="COURSE001",
                error_message="Course Name is required",
            )

        if course_code is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="COURSE002",
                error_message="Course Code is required",
            )

        new_course = course(
            course_code=course_code,
            course_name=course_name,
            course_description=course_description,
        )
        db.session.add(new_course)
        db.session.commit()
        return new_course, 201


class StudentAPI(Resource):
    @marshal_with(student_fields)
    def get(self, student_id):
        Student = student.query.filter_by(student_id=student_id).first()
        if Student:
            return Student
        else:
            raise NotFound(status_code=404)

    @marshal_with(student_fields)
    def post(self):
        args = student_reqparse.parse_args()
        roll_number = args["roll_number"]
        first_name = args["first_name"]
        last_name = args["last_name"]
        students = student.query.all()

        if roll_number in [i.roll_number for i in students]:
            raise NotFound(status_code=409)

        if roll_number is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT001",
                error_message="Roll Number is required",
            )

        if first_name is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT002",
                error_message="First Name is required",
            )

        new_student = student(
            roll_number=roll_number, first_name=first_name, last_name=last_name
        )
        db.session.add(new_student)
        db.session.commit()
        return new_student, 201

    @marshal_with(student_fields)
    def delete(self, student_id):
        Student = student.query.filter_by(student_id=student_id).first()
        if Student:
            db.session.delete(Student)
            db.session.commit()
            return 200
        else:
            raise NotFound(status_code=404)

    @marshal_with(student_fields)
    def put(self, student_id):
        args = student_reqparse.parse_args()
        roll_number = args["roll_number"]
        first_name = args["first_name"]
        last_name = args["last_name"]

        if roll_number is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT001",
                error_message="Roll Number is required",
            )

        if first_name is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT002",
                error_message="First Name is required",
            )

        Student = student.query.filter_by(student_id=student_id).first()
        if Student:
            Student.roll_number = roll_number
            Student.first_name = first_name
            Student.last_name = last_name
            db.session.commit()
            return Student, 200
        else:
            raise NotFound(status_code=404)

class EnrollmentAPI(Resource):
    @marshal_with(enrollments_fields)
    def get(self, student_id):

        Student = student.query.filter_by(student_id=student_id).first()

        if Student is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="ENROLLMENT002",
                error_message="Student does not exist",
            )

        Enrollments = enrollment.query.filter_by(student_id=student_id).all()
        if Enrollments:
            return Enrollments, 200
        else:
            raise NotFound(status_code=404)

    @marshal_with(enrollments_fields)
    def post(self, student_id):
        args = enrollment_reqparse.parse_args()
        course_id = args["course_id"]

        Student = student.query.filter_by(student_id=student_id).first()

        if Student is None:
            raise NotFound(status_code=404)

        Course = course.query.filter_by(course_id=course_id).first()

        if Course is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="ENROLLMENT001",
                error_message="Course does not exist",
            )

        Enrollments = enrollment.query.filter_by(student_id=student_id).all()

        new_enrollment = enrollment(student_id=student_id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        return Enrollments, 201

    @marshal_with(enrollments_fields)
    def delete(self, student_id, course_id):
        Student = student.query.filter_by(student_id=student_id).first()
        if Student is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="ENROLLMENT002",
                error_message="Student does not exist",
            )
        Course = course.query.filter_by(course_id=course_id).first()
        if Course is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="ENROLLMENT001",
                error_message="Course does not exist",
            )
        Enrollment = enrollment.query.filter_by(
            student_id=student_id, course_id=course_id
        ).first()
        if Enrollment:
            db.session.delete(Enrollment)
            db.session.commit()
            return "", 200
        else:
            raise NotFound(status_code=404)

api.add_resource(CourseAPI, "/api/course", "/api/course/<int:course_id>")
api.add_resource(StudentAPI, "/api/student", "/api/student/<int:student_id>")
api.add_resource(EnrollmentAPI,"/api/student/<int:student_id>/course","/api/student/<int:student_id>/course/<int:course_id>",)

if __name__ == "__main__":
    app.run(debug=True)