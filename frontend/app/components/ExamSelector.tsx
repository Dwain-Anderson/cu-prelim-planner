import React, { useState, useEffect, useCallback } from 'react';
import TypeaheadSearch from "../systems/typeahead-search";

const flaskUrl = "http://127.0.0.1:5000";

export default function ExamSelector() {
    const [courses, setCourses] = useState<Course[]>([]);
    const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
    const [query, setQuery] = useState<string>('');
    const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
    const [semester, setSemester] = useState<string>('Fall'); // Default semester
    const [examType, setExamType] = useState<string>('prelim'); // Default exam type
    const maxEditDistance = 3;

    useEffect(() => {
        fetchAllCourses();
    }, [semester, examType]);

    const fetchAllCourses = useCallback(async () => {
        try {
            const response = await fetch(`${flaskUrl}/courses?semester=${semester}&exam_type=${examType}`);
            if (!response.ok) {
                throw new Error(`Error fetching courses: ${response.statusText}`);
            }
            const data = await response.json();
            setCourses(data);
        } catch (error) {
            console.error("Error fetching courses:", error);
        }
    }, [semester, examType]);

    const getExamsByCourseCode = async (courseCode: string) => {
        try {
            const response = await fetch(`${flaskUrl}/courses/exams/${courseCode}?semester=${semester}&exam_type=${examType}`);
            if (!response.ok) {
                throw new Error(`Error fetching course details: ${response.statusText}`);
            }
            const data = await response.json();
            setSelectedCourse(data);
        } catch (error) {
            console.error("Error fetching course details:", error);
        }
    };

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
        TypeaheadSearch.handleInputChange(event, courses, setQuery, setFilteredCourses, maxEditDistance);
    };

    const handleCourseSelect = (course: Course): void => {
        setQuery(course.code);
        setFilteredCourses([]);
        getExamsByCourseCode(course.code);
    };

    const handleSemesterChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
        setSemester(event.target.value);
    };

    const handleExamTypeChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
        setExamType(event.target.value);
    };

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        fetchAllCourses();
    };

    return (
        <div className="exam-selector-container">
            <h2 className="exam-selector-title">Exam Selector</h2>
            <form onSubmit={handleSubmit}>
                <div className="selector-container">
                    <label htmlFor="semester">Select Semester:</label>
                    <select id="semester" value={semester} onChange={handleSemesterChange}>
                        <option value="fall">Fall</option>
                        <option value="spring">Spring</option>
                    </select>
                    <label htmlFor="exam_type">Select Exam Type:</label>
                    <select id="exam_type" value={examType} onChange={handleExamTypeChange}>
                        <option value="prelim">Prelim</option>
                        <option value="final">Final</option>
                    </select>
                    <button type="submit">Fetch Courses</button>
                </div>
            </form>
            <input className="course-input" type="text" value={query} onChange={handleInputChange} placeholder="Search for a course"/>
            {filteredCourses.length > 0 && (
                <ul className="suggestions-list">
                    {filteredCourses.map((course, index) => (
                        <li key={index} className="suggestion-item" onClick={() => handleCourseSelect(course)} >
                            {course.code} - {course.date}
                        </li>
                    ))}
                </ul>
            )}
            {selectedCourse && (
                <div className="exam-details">
                    <h3 className="course-title">{selectedCourse.code}</h3>
                    <ul className="exam-list">
                        <li className="exam-item">
                            <span className="exam-date">Exam Date: {selectedCourse.date}</span>
                            <span className="exam-locations">Locations: {selectedCourse.locations}</span>
                            <span className="exam-type">Exam Type: {selectedCourse.exam_type}</span>
                            {selectedCourse.time && <span className="exam-time">Time: {selectedCourse.time}</span>}
                            {selectedCourse.test_type && <span className="test-type">Test Type: {selectedCourse.test_type}</span>}
                        </li>
                    </ul>
                </div>
            )}
        </div>
    );
}
