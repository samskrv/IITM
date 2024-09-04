from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./week7_database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

#___________________________________________________________________________________________________db.model_______________________
class student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    subs = db.relationship("course", secondary="enrollments", cascade="all, delete")


class course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)


class enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), primary_key=True, nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), primary_key=True, nullable=False)

#___________________________________________________________________________________________________________________index page____

@app.route('/', methods=["GET","POST"])
def student_index():
	if request.method == "GET":
		getstudent = student.query.order_by(student.roll_number).all()
		if getstudent:
			return render_template('sindex.html', getstudent=getstudent)
		else:
			return render_template('sblank.html')

#____________________________________________________________________________________________________________creating students___

@app.route('/student/create', methods=["GET","POST"])
def create_student():
	if request.method == "GET":
		return render_template('screate.html')

	elif request.method == "POST":
		roll = request.form['roll']
		fname = request.form['f_name']
		lname = request.form['l_name']

		found = student.query.filter_by(roll_number=roll).first()
		if not found:
			add_student = student(roll_number=roll, first_name=fname, last_name=lname)
			db.session.add(add_student)
			db.session.commit()
			return redirect(url_for('student_index'))
		else:
			return render_template('sexist.html')

#____________________________________________________________________________________________________________updating student____

@app.route('/student/<sid>/update', methods=["GET","POST"])
def update_student(sid):
	if request.method == "GET":
		y = student.query.filter_by(student_id=sid).first()
		get_course = course.query.order_by(course.course_code).all()
		return render_template('supdate.html', y=y, get_course=get_course)

	elif request.method == "POST":
		fname = request.form['f_name']
		lname = request.form['l_name']
		ea = request.form['course']
		try:
			student.query.filter(student.student_id==sid).update({'first_name':fname, 'last_name':lname})
			#enrollments.query.filter_by(estudent_id=sid).delete()
			for n in ea:
				add_enroll = enrollments(estudent_id=sid, ecourse_id=n[-1])
				db.session.add(add_enroll)
				db.session.commit()
			return redirect(url_for('student_index'))
		except:
			db.session.rollback()
			return ("error in updating")


#____________________________________________________________________________________________________________deleting student____

@app.route('/student/<sid>/delete', methods=["GET","POST"])
def delete_student(sid):
	if request.method == "GET":
		try:
			student.query.filter_by(student_id=sid).delete()
			enrollments.query.filter_by(estudent_id=sid).delete()
			db.session.commit()
			return redirect(url_for('student_index'))
		except:
			db.session.rollback()
			return ("error in deleting")

#____________________________________________________________________________________________________________student detail______

@app.route('/student/<sid>', methods=["GET","POST"])
def student_detail(sid):
	socks = student.query.filter_by(student_id=sid).first()
	shirt = enrollments.query.filter_by(estudent_id=sid).all()
	tshirt = []
	jacket = []
   
	for n in shirt:
		tshirt.append(n.ecourse_id)
	for n in tshirt:
		jacket.append(course.query.filter_by(course_id=n).all())
	return render_template("sdetail.html", sock=socks, jacket=jacket, lad=tshirt)

#________________________________________________________________________________________________withdraw course of the student___

@app.route('/student/<sid>/withdraw/<cid>', methods=["GET","POST"])
def delete_course_from_student(sid,cid):
	if request.method == "GET":
		try:
			enrollments.query.filter((enrollments.estudent_id==sid)&(enrollments.ecourse_id==cid)).delete()
			db.session.commit()
			return redirect(url_for('student_index'))
		except:
			db.session.rollback()
			return ("error in withdrawing")

#____________________________________________________________________________________________________________course index_________

@app.route('/courses', methods=["GET","POST"])
def course_index():
	if request.method == "GET":
		getcourse = course.query.order_by(course.course_code).all()
		if getcourse:
			return render_template('cindex.html', getcourse=getcourse)
		else:
			return render_template('cblank.html')

#____________________________________________________________________________________________________________creating course______

@app.route('/course/create', methods=["GET","POST"])
def create_course():
	if request.method == "GET":
		return render_template('ccreate.html')

	elif request.method == "POST":
		code = request.form['code']
		cname = request.form['c_name']
		desc = request.form['desc']

		found = course.query.filter_by(course_code=code).first()
		if not found:
			add_course = course(course_code=code, course_name=cname, course_description=desc)
			db.session.add(add_course)
			db.session.commit()
			return redirect(url_for('course_index'))
		else:
			return render_template('cexist.html')

#____________________________________________________________________________________________________________updating course_____

@app.route('/course/<cid>/update', methods=["GET","POST"])
def update_course(cid):
	if request.method == "GET":
		y = course.query.filter_by(course_id=cid).first()
		return render_template('cupdate.html', y=y)
	elif request.method == "POST":
		cname = request.form['c_name']
		desc = request.form['desc']
		try:
			course.query.filter(course.course_id==cid).update({'course_name':cname, 'course_description': desc})
			db.session.commit()
			return redirect(url_for('course_index'))
		except:
			db.session.rollback()
			return ("error in updating")

#____________________________________________________________________________________________________________deleting course_____

@app.route('/course/<cid>/delete', methods=["GET","POST"])
def delete_course(cid):
	try:
		course.query.filter_by(course_id=cid).delete()
		enrollments.query.filter_by(ecourse_id=cid).delete()
		db.session.commit()
		return redirect(url_for('course_index'))
	except:
		db.session.rollback()
		return ('error in deleting')

#____________________________________________________________________________________________________________course detail_______

@app.route('/course/<cid>', methods=["GET","POST"])
def course_detail(cid):
	socks = course.query.filter_by(course_id=cid).first()
	shirt = enrollments.query.filter_by(ecourse_id=cid).all()
	tshirt = []
	jackets = []

	for buttons in shirt:
		tshirt.append(buttons.estudent_id)
	for n in tshirt:
		jackets.append(student.query.filter_by(student_id=n).all())

	return render_template('cdetail.html', sock=socks, jacket=jackets, lad=jackets) #html file needs styling

#_________________________________________________________________________________________________________running the flask app_

if __name__ == "__main__":
    # run the flask app
    app.run(host='0.0.0.0', debug=True, port=5000) # running on localhost/0.0.0.0/127.0.0.1 having port 5000 with debugging