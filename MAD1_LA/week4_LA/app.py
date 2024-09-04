from flask import Flask,request,render_template
import matplotlib.pyplot as plt
plt.switch_backend("agg")

app = Flask(__name__)

data = []
f = open("data.csv" , "r")
for i in f.readlines()[1:]:
    data.append(i.strip().split(","))
f.close()

@app.route('/', methods = ["GET", "POST"])
def executer():
    if request.method == "GET":
        return render_template("home.html")
    if request.method == "POST":
        try:
            typer = request.form["ID"]
            id_data = request.form["id_value"]
        except:
            return render_template("error.html")
    if typer == "student_id" :
        total = 0
        student = {}
        for i in data:
            if i[0] == id_data :
                total += int(i[2])
                student[i[1]] = i[2]
        if len(student) > 0 :
            return render_template("student.html", total_marks = total, s_id = id_data, student = student )
        else:
            return render_template("error.html")
    elif typer == "course_id":
        marks = []
        for i in data:
            if int(i[1])==int(id_data):
                marks.append(int(i[2]))

        if len(marks) > 0:
            plt.clf()
            fig = plt.figure()
            plt.hist(marks)
            plt.xlabel("Marks")
            plt.ylabel("Frequency")
            plt.savefig("static/hist.png")
            avg_marks = sum(marks)/len(marks)
            return render_template("course.html", average_marks = avg_marks, maximum_marks = max(marks))
        else:
            return render_template("error.html")


if __name__ == "__main__":
    app.run(debug = True)