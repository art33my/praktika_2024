import time
import requests
import mysql.connector
from mysql.connector import errorcode

def get_vacancies(keyword, min_salary=None, experience=None, max_results=500):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": 1,  # Specify the desired area ID (1 is Moscow)
        "per_page": 100,  # Number of vacancies per page
    }

    if min_salary:
        params["salary"] = min_salary

    if experience:
        params["experience"] = experience

    headers = {
        "User-Agent": "Your User Agent",  # Replace with your User-Agent header
    }

    total_added = 0  # Общее количество добавленных вакансий

    while total_added < max_results:
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            vacancies = data.get("items", [])

            if not vacancies:
                print("No more vacancies found.")
                break

            try:
                connection = mysql.connector.connect(
                    host='mysql',
                    user='user',
                    password='userpassword',
                    database='vacancies_db',
                    connection_timeout=10
                )
                cursor = connection.cursor()
                # Очистка базы данных перед добавлением новых данных (только для тестирования)
                cursor.execute("DELETE FROM vacancies")
                connection.commit()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id VARCHAR(255) PRIMARY KEY,
                        title VARCHAR(255),
                        company VARCHAR(255),
                        url VARCHAR(255),
                        salary_from DECIMAL(10, 2),
                        salary_to DECIMAL(10, 2),
                        currency VARCHAR(10),
                        experience VARCHAR(255)
                    )
                """)

                for vacancy in vacancies:
                    if total_added >= max_results:
                        break

                    vacancy_id = vacancy.get("id")
                    vacancy_title = vacancy.get("name")
                    vacancy_url = vacancy.get("alternate_url")
                    company_name = vacancy.get("employer", {}).get("name")

                    salary = vacancy.get("salary", {})
                    salary_from = salary.get("from") if salary and "from" in salary else None
                    salary_to = salary.get("to") if salary and "to" in salary else None
                    salary_currency = salary.get("currency") if salary and "currency" in salary else None

                    experience = vacancy.get("experience", {}).get("name", "")

                    try:
                        cursor.execute("""
                            INSERT INTO vacancies (id, title, company, url, salary_from, salary_to, currency, experience)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                title=VALUES(title),
                                company=VALUES(company),
                                url=VALUES(url),
                                salary_from=VALUES(salary_from),
                                salary_to=VALUES(salary_to),
                                currency=VALUES(currency),
                                experience=VALUES(experience)
                        """, (vacancy_id, vacancy_title, company_name, vacancy_url, salary_from, salary_to, salary_currency,
                              experience))

                        connection.commit()
                        total_added += 1
                        print(f"Added vacancy: {vacancy_title}")

                    except mysql.connector.Error as insert_err:
                        print(f"Error inserting vacancy {vacancy_id}: {insert_err}")

                cursor.close()
                connection.close()

            except mysql.connector.Error as connect_err:
                print(f"MySQL connection error: {connect_err}")
                time.sleep(10)  # Пауза перед повторной попыткой подключения

        else:
            print(f"Request failed with status code: {response.status_code}")
            break  # Прекращаем запросы при ошибке

        params["page"] = data.get("page", 0) + 1  # Переходим на следующую страницу

    print(f"Total vacancies added: {total_added}")
    return total_added
