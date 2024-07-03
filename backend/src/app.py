from flask import Flask, request, jsonify
from flask_cors import CORS
from webscrape import WebScraper
from database import DatabaseManager
from psycopg2 import connect, OperationalError

app = Flask(__name__)
app.secret_key = ''
CORS(app)

# Configuration for Google OAuth
GOOGLE_CLIENT_ID = 'your_client_id_here'
GOOGLE_CLIENT_SECRET = 'your_client_secret_here'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/oauth2callback'
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_db_manager(semester, exam_type, table_name=None):
    """
    Returns a DatabaseManager instance configured with given semester and exam_type.

    :param semester: String
    :param exam_type: String
    :param table_name: String, optional
    :return: DatabaseManager instance
    """
    scraper = WebScraper(semester, exam_type)
    db_manager = DatabaseManager(lambda: connect(
        dbname="cu_prelim_planner",
        user="",
        password="",
        host="localhost",
        port="5432"
    ), scraper, table_name)
    return db_manager


@app.route('/courses/exams/create', methods=['POST'])
def create_all_exams():
    """
    Initializes the database with exams based on provided semester and exam_type.

    JSON Body Parameters:
    - semester: String
    - exam_type: String

    Returns:
    - JSON response indicating success or failure.
    """
    try:
        data = request.json
        semester = data['semester']
        exam_type = data['exam_type']
        db_manager = get_db_manager(semester, exam_type)

        # Scrape the data and populate the database
        db_manager.populate_exam_table(semester, exam_type)

        return success_response("Exam data created successfully.")
    except Exception as e:
        return failure_response(str(e))


@app.route('/courses/exams/<course_code>', methods=['GET'])
def get_exams_by_course_code(course_code):
    """
    Retrieves exams for a specific course code and semester.

    Path Parameters:
    - course_code: String

    Query Parameters:
    - semester: String
    - exam_type: String

    Returns:
    - JSON object containing exams for the specified course code.

    Raises:
    - Exception: If there is an error while fetching exams.
    """
    try:
        semester = request.args.get('semester')
        exam_type = request.args.get('exam_type')
        db_manager = get_db_manager(semester, exam_type)
        exams = db_manager.fetch_exam(course_code, exam_type)

        return success_response(exams)
    except Exception as e:
        return failure_response(str(e))


@app.route('/courses/exams/update/<course_code>', methods=['PUT'])
def update_exam_by_course_code(course_code):
    """
    Updates exam data for a specific course code.

    Path Parameters:
    - course_code: String

    JSON Body Parameters:
    - semester: String
    - exam_type: String
    - new_exam_data: JSON object containing updated exam data.

    Returns:
    - JSON response indicating success or failure.
    """
    try:
        data = request.json
        semester = data['semester']
        exam_type = data['exam_type']
        new_exam_data = data['new_exam_data']
        db_manager = get_db_manager(semester, exam_type)

        # Update the exam data
        db_manager.update_exam(course_code, new_exam_data)

        return success_response("Exam data updated successfully.")
    except Exception as e:
        return failure_response(str(e))


@app.route('/exams/delete/<course_code>', methods=['DELETE'])
def delete_exam_by_course_code(course_code):
    """
    Deletes exam data for a specific course code.

    Path Parameters:
    - course_code: String

    Query Parameters:
    - semester: String
    - exam_type: String

    Returns:
    - JSON response indicating success or failure.
    """
    try:
        semester = request.args.get('semester')
        exam_type = request.args.get('exam_type')
        db_manager = get_db_manager(semester, exam_type)

        # Delete the exam data
        db_manager.delete_exam(course_code)

        return success_response(f"Exam data for course {course_code} deleted successfully.")
    except Exception as e:
        return failure_response(str(e))


@app.route('/courses', methods=['GET'])
def fetch_all_courses():
    """
    Fetches all course codes from the database based on semester and exam_type.

    Query Parameters:
    - semester: String
    - exam_type: String

    Returns:
    - JSON object containing all course codes fetched from the database.

    Raises:
    - Exception: If there is an error while fetching courses.
    """
    try:
        semester = request.args.get('semester')
        exam_type = request.args.get('exam_type')
        db_manager = get_db_manager(semester, exam_type)
        courses = db_manager.fetch_all_courses()

        return success_response(courses)
    except Exception as e:
        return failure_response(str(e))


# Placeholder route for Google OAuth callback
@app.route('/oauth2callback')
def oauth2callback():
    pass


# Placeholder route to push courses to Google Calendar
@app.route('/push_courses_to_calendar')
def push_courses_to_calendar():
    pass


# Helper function to return success response with JSON data
def success_response(data, code=200):
    return jsonify(data), code


# Helper function to return failure response with error message
def failure_response(message, code=404):
    return jsonify({'error': message}), code


# Main entry point to run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
