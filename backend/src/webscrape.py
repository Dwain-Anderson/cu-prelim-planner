from typing import List, Dict, Union
import requests
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self, semester: str, exam_type: str):
        """
        :param semester: Semester information (e.g., 'Fall 2024')
        :param exam_type: Type of exam (e.g., 'Prelim')
        :param requester: Dependency injection for the HTTP requester (default: requests.get)
        :param parser: Dependency injection for the HTML parser (default: BeautifulSoup)
        """
        self.base_url = "https://registrar.cornell.edu/exams/"
        self.semester = semester  
        self.exam_type = exam_type 
        self.requester = requests.get
        self.parser = BeautifulSoup
        self.file_name = None
        self.exam_data_header = None
        self.year = None

    def scrape_course_info(self) -> Union[str, bool]:
        """
        Scrape course information from the website.
        :return: The raw exam data as a string.
        """
        try:
            response = self.requester(self.generate_url())
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            html_content = response.content
            soup = self.parser(html_content, 'html.parser')
            return self.parse_html(soup)
        except Exception as e:
            return self.error_response(f"Error scraping course information: {e}")

    def parse_html(self, soup) -> str:
        """
        Parse the HTML content to extract exam data.
        :param soup: BeautifulSoup object of the HTML content.
        :return: The raw exam data as a string.
        """
        assert soup is not None
        semester_info = soup.find('div', class_='content').find('div').find('h2').get_text(strip=True)
        pre_element = soup.find('pre')
        strong_element = pre_element.find('strong')
        self.exam_data_header = strong_element.text.strip()
        strong_element.extract()
        exam_data = pre_element.get_text(strip=True)
        self.year = semester_info.split()[1]

        filename = lambda sem, year, exam: f"{sem.lower()}-{year}-{exam.lower()}-exams.txt"
        self.file_name = filename(self.semester, self.year, self.exam_type)
        self.save_to_text_file(self.file_name, f"{semester_info}\n{exam_data}")
        return exam_data

    def process_exam_data(self, filepath: str) -> Union[list[dict[str, str]], bool]:
        """
        Process the exam data from a file and return it in a structured format.
        :param filepath: Path to the file containing exam data.
        :return: Formatted exam data as a list of dictionaries.
        """
        assert filepath is not None
        try:
            with open(filepath, 'r') as file:
                return self.parse_exam_file(file)
        except FileNotFoundError:
            return self.error_response(f"Error: File '{filepath}' not found.")

    def parse_exam_file(self, file) -> List[Dict[str, str]]:
        """
        Parse the exam file to extract structured exam data.
        :param file: File object containing exam data.
        :return: List of dictionaries with formatted exam data.
        """
        assert file is not None
        formatted_data = []
        for line in file:
            line = line.strip()
            if line.startswith(self.semester) or line == "":
                continue  # Skip header line or empty lines
            parts = line.split()
            if self.exam_type.lower() == "prelim":
                if len(parts[2]) == 3:  # If the course_code contains lec info
                    course_code = f"{parts[0]} {parts[1]} {parts[2]}"
                    exam_date = f"{parts[3]}"
                    exam_locations = ' '.join(parts[4:])
                else:  # It doesn't contain lec info, for now this check is reliable
                    course_code = f"{parts[0]} {parts[1]}"
                    exam_date = f"{parts[2]}"
                    exam_locations = ' '.join(parts[3:])  # Join the rest as exam locations
                formatted_exam = {
                    'course_code': course_code.strip(),
                    'exam_date': exam_date.strip(),
                    'exam_locations': exam_locations.strip()
                }
            elif self.exam_type.lower() == "final":
                if len(parts[2]) == 3:  # If the course_code contains lec info
                    course_code = f"{parts[0]} {parts[1]} {parts[2]}"
                    exam_date = f"{parts[3]}"
                    exam_time = ' '.join(parts[4:6])
                    test_type = ' '.join(parts[6:8])
                    exam_locations = ' '.join(parts[8:])
                else:  # It doesn't contain lec info, for now this check is reliable
                    course_code = f"{parts[0]} {parts[1]}"
                    exam_date = f"{parts[2]}"
                    exam_time = ' '.join(parts[3:5])
                    test_type = ' '.join(parts[5:7])
                    exam_locations = ' '.join(parts[7:])

                formatted_exam = {
                    'course_code': course_code.strip(),
                    'exam_date': exam_date.strip(),
                    'exam_time': exam_time.strip(),
                    'test_type': test_type.strip(),
                    'exam_locations': exam_locations.strip(),
                }
            else:
                raise ValueError("Unknown Exam Type")
            formatted_data.append(formatted_exam)
        return formatted_data

    def generate_url(self) -> str:
        """
        Generate the URL for scraping exam data.
        :return: The generated URL as a string.
        """
        semester_param = self.semester.lower().replace(" ", "-")
        exam_type_param = self.exam_type.lower().replace(" ", "-")
        return f"{self.base_url}{semester_param}-{exam_type_param}-exam-schedule"

    def save_to_text_file(self, file_name: str, data: str) -> bool:
        """
        Save data to a text file.
        :param file_name: Name of the file.
        :param data: Data to be saved.
        :return: True if successful, False otherwise.
        """
        assert file_name is not None
        assert data is not None
        try:
            with open(file_name, 'w') as f:
                f.write(data)
            return self.success_response(f"Data saved to {file_name}")
        except Exception as e:
            return self.error_response(f"Error saving data to file: {e}")

    def error_response(self, error: str) -> bool:
        """
        Handle error responses.
        :param error: Error message.
        :return: False.
        """
        assert error is not None
        print(error)
        return False

    def success_response(self, message: str) -> bool:
        """
        Handle success responses.
        :param message: Success message.
        :return: True.
        """
        assert message is not None
        print(message)
        return True


if __name__ == "__main__":
    pass