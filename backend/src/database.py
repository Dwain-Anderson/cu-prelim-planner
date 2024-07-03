from psycopg2 import connect, OperationalError
from typing import Callable, Dict, Any, Union, List, Set
from webscrape import WebScraper


class DatabaseManager:
    """
    A class to manage interactions with a PostgreSQL database for storing and retrieving exam data.

    Attributes:
        conn (Callable): The function to get a database connection.
        table_name (str): Current table name being operated on.
    """

    def __init__(self, db_connect: Callable[[], Any], scraper: WebScraper, table_name=None):
        """
        Initializes the DatabaseManager with the specified database connection details.

        Args:
            db_connect (Callable): The function to get a database connection.
            scraper (WebScraper): An instance of the WebScraper class.
        """
        self.conn = db_connect()
        self.scraper = scraper
        self.table_name = table_name

    def close_connection(self) -> bool:
        """
        Closes the database connection if it is open.

        Returns:
            bool: True if the connection is closed successfully, False otherwise.
        """
        if self.conn:
            self.conn.close()
            return self.success_response("Database connection closed.")
        else:
            return self.error_response("No active database connection to close.")

    def set_exam_table_name(self, table_name: str) -> None:
        """
        Sets the current table name for operations.

        Args:
            table_name (str): The name of the table.
        """
        self.table_name = table_name

    def generate_create_table_query(self, table_name: str, exam_type: str) -> str:
        """
        Generates the SQL query to create an exam table.

        Args:
            table_name (str): The name of the table.
            exam_type (str): The type of exam (e.g., prelim or final).

        Returns:
            str: The SQL query to create the table.
        """
        if exam_type.lower() == 'prelim':
            return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                course_code TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                exam_locations TEXT NOT NULL
            );
            """

        elif exam_type.lower() == 'final':
            return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                course_code TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                exam_time TEXT NOT NULL,
                test_type TEXT NOT NULL 
                exam_locations TEXT NOT NULL
            );
            """
        else:
            raise ValueError("Unknown exam type")

    def create_exam_table(self, semester: str, exam_type: str, year: str) -> bool:
        """
        Creates an exam table in the database if it does not already exist.

        Args:
            semester (str): The semester for which the exam table is created.
            exam_type (str): The type of exam (e.g., prelim or final).
            year (str): The year of the semester.

        Returns:
            bool: True if the table was created successfully, False otherwise.
        """
        self.set_exam_table_name(f"{semester}_{year}_{exam_type}_exams")
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.generate_create_table_query(self.table_name, exam_type))
                self.conn.commit()
            return self.success_response("Table created successfully!")
        except OperationalError as e:
            return self.error_response(f"Error creating table in PostgreSQL: {e}")

    def populate_exam_table(self, semester: str, exam_type: str) -> bool:
        """
        Populates the exam table with data scraped from the web.

        Args:
            semester (str): The semester for which the exam table is populated.
            exam_type (str): The type of exam (e.g., prelim or final).

        Returns:
            bool: True if the table was populated successfully, False otherwise.
        """
        self.scraper.scrape_course_info()
        exams_data = self.scraper.process_exam_data(self.scraper.file_name)
        self.create_exam_table(semester, exam_type.lower(), self.scraper.year)
        try:
            for exam_info in exams_data:
                code = exam_info.get('course_code')
                date = exam_info.get('exam_date')
                locations = exam_info.get('exam_locations')
                if exam_type.lower() == 'final':
                    time = exam_info.get('exam_time')
                    test_type = exam_info.get('test_type')
                    self.insert_exam(code, date, locations, exam_type.lower(), time, test_type)
                else:
                    self.insert_exam(code, date, locations, exam_type.lower())
            self.conn.commit()
            return self.success_response("Data inserted into database successfully!")
        except OperationalError as e:
            return self.error_response(f"Error inserting data into PostgreSQL: {e}")

    def delete_table(self, table_name: str) -> bool:
        """
        Deletes the given table from the database.

        Args:
            table_name (str): The name of the table to delete.

        Returns:
            bool: True if the table was deleted successfully, False otherwise.
        """
        if self.conn:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(f"DROP TABLE IF EXISTS {table_name};")
                    self.conn.commit()
                return self.success_response(f"Table '{table_name}' deleted successfully.")
            except OperationalError as e:
                return self.error_response(f"Error deleting table: {e}")
        else:
            return self.error_response("Database connection not available.")

    def generate_insert_exam_query(self, table_name: str, exam_type: str) -> str:
        """
        Generates the SQL query to insert exam data into a table.

        Args:
            table_name (str): The name of the table.
            exam_type (str): The type of exam (e.g., prelim or final).

        Returns:
            str: The SQL query to insert data into the table.
        """
        if exam_type.lower() == 'prelim':
            return f"""
            INSERT INTO {table_name} (course_code, exam_date, exam_locations)
            VALUES (%s, %s, %s);
            """
        elif exam_type.lower() == 'final':
            return f"""
            INSERT INTO {table_name} (course_code, exam_date, exam_time, exam_or_deliverable, exam_locations)
            VALUES (%s, %s, %s, %s, %s);
            """
        else:
            raise ValueError("Unknown exam type")

    def insert_exam(self, code, date, locations, exam_type, time=None, test_type=None) -> bool:
        """
        Insert an exam record into the database.

        Args:
            code (str): Course code.
            date (str): Exam date.
            locations (str): Exam locations.
            exam_type (str): Exam type ('prelim' or 'final').
            time (str): Exam time (optional, default None).
            test_type (str): Test type (optional, default None).

        Returns:
            bool: True if insertion is successful, False otherwise.
        """
        insert_query = self.generate_insert_exam_query(self.table_name, exam_type.lower())

        try:
            with self.conn.cursor() as cur:
                if exam_type.lower() == 'prelim':
                    cur.execute(insert_query, (code, date, locations))
                elif exam_type.lower() == 'final':
                    cur.execute(insert_query, (code, date, time, test_type, locations))
                else:
                    raise ValueError("Unknown exam type")
                self.conn.commit()
            return self.success_response("Exam record inserted successfully.")
        except OperationalError as e:
            return self.error_response(f"Error inserting exam record: {e}")

    def generate_update_exam_query(self, table_name: str, exam_type: str) -> str:
        """
        Generates the SQL query to update exam data in a table.

        Args:
            table_name (str): The name of the table.
            exam_type (str): The type of exam (e.g., prelim or final).

        Returns:
            str: The SQL query to update data in the table.
        """
        if exam_type.lower() == 'prelim':
            return f"""
            UPDATE {table_name}
            SET exam_date = %s, exam_locations = %s
            WHERE course_code = %s;
            """
        elif exam_type.lower() == 'final':
            return f"""
            UPDATE {table_name}
            SET exam_date = %s, exam_time = %s, exam_or_deliverable = %s, exam_locations = %s
            WHERE course_code = %s;
            """
        else:
            raise ValueError("Unknown exam type")

    def update_exam(self, code, date, locations, exam_type, time=None, test_type=None) -> bool:
        try:
            with self.conn.cursor() as cur:
                update_query = self.generate_update_exam_query(self.table_name, exam_type)
                if exam_type.lower() == 'prelim':
                    cur.execute(update_query, (code, date, locations))
                elif exam_type.lower() == 'final':
                    cur.execute(update_query, (code, date, time, test_type, locations))
                else:
                    raise ValueError("Unknown exam type")
                self.conn.commit()
            return self.success_response("Exam record updated successfully.")
        except OperationalError as e:
            return self.error_response(f"Error updating exam record: {e}")

    def delete_exam(self, course_code: str) -> bool:
        """
        Deletes an exam record from the database.

        Args:
            course_code (str): The course code for the exam.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with self.conn.cursor() as cur:
                delete_query = f"""DELETE FROM "{self.table_name}"WHERE course_code = %s;"""
                cur.execute(delete_query, (course_code,))
                self.conn.commit()
            return self.success_response("Exam record deleted successfully.")
        except OperationalError as e:
            return self.error_response(f"Error deleting exam record: {e}")

    def fetch_exam(self, course_code: str, exam_type) -> Union[List[Dict[str, Any]], bool]:
        """

        :param course_code:
        :param exam_type:
        :return:
        """
        try:
            with self.conn.cursor() as cur:
                fetch_query = f"""SELECT * FROM "{self.table_name}" WHERE course_code = %s;"""
                cur.execute(fetch_query, (course_code,))
                exam_records = cur.fetchall()
            return [self.format_exam_record(record, exam_type) for record in exam_records]
        except OperationalError as e:
            return self.error_response(f"Error fetching exam records: {e}")

    def fetch_k_exams(self, course_codes: List[str], exam_type: str) -> Union[
        list[dict[str, Any]], bool]:
        """

        :param course_codes:
        :param exam_type:
        :return:
        """
        try:
            exam_records = []
            with self.conn.cursor() as cur:
                k = len(course_codes)
                for i in range(k):
                    fetch_query = f"""SELECT * FROM "{self.table_name}" WHERE course_code = %s;"""
                    cur.execute(fetch_query, (course_codes[i],))
                    record = cur.fetchone()
                    if record:
                        exam_records.append(self.format_exam_record(record, exam_type))
            return exam_records
        except OperationalError as e:
            return self.error_response(f"Error fetching exam records: {e}")

    def fetch_all_courses(self) -> Union[list[Any], bool]:
        """
        Fetches all unique course codes from the exam table.

        Returns:
            List[str]: A list of course codes.
        """

        try:
            with self.conn.cursor() as cur:
                fetch_query = f"SELECT DISTINCT course_code FROM {self.table_name};"
                cur.execute(fetch_query)
                course_codes = [record[0] for record in cur.fetchall()]
            return course_codes
        except OperationalError as e:
            return self.error_response(f"Error fetching course codes: {e}")

    def delete_all_exams(self) -> bool:
        """
        Deletes all exam records from the exam table.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with self.conn.cursor() as cur:
                delete_all_query = f"""
                DELETE FROM "{self.table_name}";
                """
                cur.execute(delete_all_query)
                self.conn.commit()
            return self.success_response("All exam records deleted successfully.")
        except OperationalError as e:
            return self.error_response(f"Error deleting all exam records: {e}")

    def format_exam_record(self, record: tuple, exam_type: str) -> Dict[str, Any]:
        """
        Formats a database record into a dictionary.

        Args:
            record (tuple): A tuple representing a database record.

        Returns:
            Dict[str, Any]: A dictionary representing the record.
            :param record:
            :param exam_type:
        """

        if exam_type == "prelim":
            return {
                'course_code': record[0],
                'exam_date': record[1],
                'exam_locations': record[2]
            }
        elif exam_type == "final":
            return {
                'course_code': record[0],
                'exam_date': record[1],
                'exam_time': record[2],
                'test_type': record[3],
                'exam_locations': record[4]
            }
        else:
            raise ValueError("Unknown exam type")

    def error_response(self, error: str) -> bool:
        """
        A generic function to unify how errors are handled/communicated
        regarding the database operations.

        Args:
            error (str): The error message to communicate.

        Returns:
            bool: False indicating an error occurred.
        """
        print(f"Error: {error}")
        return False

    def success_response(self, message: str) -> bool:
        """
        A generic function to unify how successful processes are handled/communicated
        regarding certain database operations.

        Args:
            message (str): The success message to communicate.

        Returns:
            bool: True indicating the operation was successful.
        """
        print(f"Success: {message}")
        return True

