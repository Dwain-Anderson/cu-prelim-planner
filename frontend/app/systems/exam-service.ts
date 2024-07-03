
const flaskUrl = 'http://localhost:5000'; // Update this to your Flask backend URL

export default class ExamService {
    async fetchAllCourses(semester: string, examType: string): Promise<Course[]> {
        try {
            const response = await fetch(`${flaskUrl}/courses?semester=${semester}&exam_type=${examType}`);
            if (!response.ok) {
                throw new Error(`Error fetching courses: ${response.statusText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(error);
            throw error;
        }
    }

    async fetchSpecificCourse(courseCode: string, courseDate: string, semester: string, examType: string): Promise<Course> {
        try {
            const response = await fetch(`${flaskUrl}/exam/${courseCode}?semester=${semester}&exam_type=${examType}&date=${courseDate}`);
            if (!response.ok) {
                throw new Error(`Error fetching course details: ${response.statusText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(error);
            throw error;
        }
    }
}

