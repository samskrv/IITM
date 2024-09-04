import sys
import csv
from jinja2 import Template
import matplotlib.pyplot as plt 

error_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Something Went Wrong</title>
    </head>
    <body>
        <h1>Wrong Inputs</h1>
        <p>Something went wrong</p>
    </body>
    </html>
    '''

try:
    argu = sys.argv[1:]
    id = argu[1]

    # Open and read the CSV file
    with open('data.csv') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]

    if argu[0] == '-s':
        student_list = []
        total = 0
        for row in rows[1:]:
            if row[0] == id:
                student_list.append(row)
                total += int(row[2])
        
        if len(student_list) > 0:
            student_detail = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Student Data</title>
    </head>
    <body>
        <h1>Student Details</h1>
        <table border="1">
            <tr>
                <th>Student ID</th>
                <th>Course ID</th>
                <th>Marks</th>
            </tr>
            {% for data in list %}
            <tr>
                <td>{{ data[0] }}</td>
                <td>{{ data[1] }}</td>
                <td>{{ data[2] }}</td>
            </tr>
            {% endfor %}
            <tr>
                <td colspan="2" style="text-align: center;">Total Marks</td>
                <td>{{ total }}</td>
            </tr>
        </table>
    </body>
    </html>
    '''
            template = Template(student_detail)
            out = template.render(list=student_list, total=total)    
        else:
            template = Template(error_template)
            out = template.render()

    elif argu[0] == '-c':
        course_list = []
        total = 0
        for row in rows[1:]:
            course_id = row[1].strip()
            if course_id == id:
                course_list.append(int(row[2]))
                total += int(row[2])
        
        if len(course_list) > 0:
            average_marks = total / len(course_list)
            maximum_marks = max(course_list)
            course_details = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Course Data</title>
    </head>
    <body>
        <h1>Course Details</h1>
        <table border="1">
            <tr>
                <th>Average Marks</th>
                <th>Maximum Marks</th>
            </tr>
            <tr>
                <td>{{ average_marks }}</td>
                <td>{{ maximum_marks }}</td>
            </tr>
        </table>
        <img src="histo.png" alt="Histogram">
    </body>
    </html>
    '''
            plt.hist(course_list)
            plt.xlabel('Marks')
            plt.ylabel('Frequency')
            plt.savefig('histo.png')
            template = Template(course_details)
            out = template.render(average_marks=average_marks, maximum_marks=maximum_marks)
        else:
            template = Template(error_template)
            out = template.render()
    else:
        template = Template(error_template)
        out = template.render()

    with open('output.html', 'w') as result:
        result.write(out)
except:
    template = Template(error_template)
    out = template.render()
    with open('output.html', 'w') as result:
        result.write(out)