# FINAL_FLASK.py
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_degree_by_category(degree_type):
    conn = sqlite3.connect('UX.sqlite')
    cur = conn.cursor()

    if degree_type == 'bachelor':
        dt = 'bachelor'
    elif degree_type == 'masterorphd':
        dt = 'masterorphd'
    elif degree_type == 'certificates':
        dt = 'certificates'

    q = f'''
        SELECT Program, University, CityName, ProgramLink, ProgramType
        FROM Programs
        JOIN Cities
        ON Programs.CityId=Cities.Id
        WHERE Programs.ProgramType = '{dt}'
    '''
    results = cur.execute(q).fetchall()
    conn.close()
    return results

def get_info(sort_by):
    conn = sqlite3.connect('UX.sqlite')
    cur = conn.cursor()

    if sort_by == 'Population':
        q = 'Population'
    elif sort_by == "MedianIncome":
        q = 'MedianIncome'
    elif sort_by == "Age":
        q = "Age"
    elif sort_by == "UnemploymentRate":
        q = "UnemploymentRate"
    
    query = f'''
        SELECT Program, University, CityName, Cities.{q}
        FROM Programs
        JOIN Cities
        ON Programs.CityId=Cities.Id
        ORDER BY Cities.{q} DESC 

    '''
    results = cur.execute(query).fetchall()
    conn.close()
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/degree/<category>')
def bars(category):
    degree_type = category
    results = get_degree_by_category(degree_type)
    return render_template('results2.html', category=category, degree_type=degree_type, results=results)

# @app.route('/degree/<category>', method = ['POST'])
# def results2():
#     degree_type = request.form['degree']
#     results = get_degree_by_category(degree_type)
#     return render_template('results2.html', degree_type=degree_type, results=results)

@app.route('/results', methods=['POST'])
def results():
    sort_by = request.form['category']
    results = get_info(sort_by)
    return render_template('results.html', results=results, sort_by=sort_by)

if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)
