type Course = {
  code: string;
  date: string;
  locations: string;
  exam_type: string;
  time?: string;
  test_type?: string;
};

interface ExamSelectorProps {
  courses: Course[];
}
