from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from parser import get_vacancies

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run-parser', methods=['POST'])
def run_parser():
    keyword = request.form.get('keyword')
    min_salary = request.form.get('min_salary')
    experience = request.form.get('experience')

    # Сохраняем параметры поиска в сессии
    session['keyword'] = keyword
    session['min_salary'] = min_salary
    session['experience'] = experience

    # Парсинг данных с использованием введенных фильтров
    vacancies_data = get_vacancies(keyword, min_salary=min_salary, experience=experience)

    # Очищаем параметры поиска в сессии после использования
    session.pop('keyword', None)
    session.pop('min_salary', None)
    session.pop('experience', None)

    return redirect(url_for('results'))


@app.route('/results')
def results():
    keyword = session.get('keyword')
    min_salary = session.get('min_salary')
    experience = session.get('experience')

    connection = mysql.connector.connect(
        host='mysql',
        user='user',
        password='userpassword',
        database='vacancies_db'
    )
    cursor = connection.cursor()

    # Формируем SQL запрос с условиями, исключающими вакансии с неуказанной зарплатой
    if min_salary:
        min_salary = int(min_salary)
        cursor.execute("""
            SELECT * FROM vacancies 
            WHERE salary_from IS NOT NULL AND salary_from >= %s
        """, (min_salary,))
    else:
        cursor.execute("""
            SELECT * FROM vacancies 
            WHERE salary_from IS NOT NULL
        """)

    vacancies = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('results.html', vacancies=vacancies)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
