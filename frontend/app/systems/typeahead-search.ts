export default class TypeaheadSearch {
    static EditDistance(a: string, b: string): number {
        const matrix: number[][] = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));
    
        for (let i = 0; i <= a.length; i++) {
            matrix[i][0] = i;
        }
  
        for (let j = 0; j <= b.length; j++) {
            matrix[0][j] = j;
        }
    
        for (let i = 1; i <= a.length; i++) {
            for (let j = 1; j <= b.length; j++) {
                if (a[i - 1] === b[j - 1]) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(matrix[i - 1][j - 1], matrix[i][j - 1], matrix[i - 1][j]) + 1;
                }
            }
        }
    
        return matrix[a.length][b.length];
    }
  
    static SanitizeInput(a: string): string {
        return a.replace(/[^a-zA-Z0-9 \-_]/g, '').trim();
    }
  
    static handleInputChange(event: React.ChangeEvent<HTMLInputElement>, courses: Course[], setQuery: (query: string) => void, setFilteredCourses: (courses: Course[]) => void, maxEditDistance: number): void {
        const value = event.target.value; // Remove sanitization here
        setQuery(value);
  
        if (!value) {
            setFilteredCourses([]);
            return;
        }
  
        const sanitizedValue = TypeaheadSearch.SanitizeInput(value).toLowerCase();
  
        const filtered = courses.filter(course => {
            const courseCode = course.code.toLowerCase();
  
            if (courseCode.includes(sanitizedValue)) {
                if (sanitizedValue.length > 1) {
                    const distance = TypeaheadSearch.EditDistance(sanitizedValue, courseCode);
                    return distance <= maxEditDistance;
                }
                return true;
            }
            return false;
        });
        setFilteredCourses(filtered);
    }
  }
  