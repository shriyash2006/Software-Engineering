"""
Course Registration System
A comprehensive implementation following UML design principles
Demonstrates OOP concepts: Encapsulation, Inheritance, Polymorphism, and Abstraction
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
import json
import os
import re
from itertools import product


# ==================== UTILITY FUNCTIONS ====================

def validate_registration_number(reg_no: str) -> tuple[bool, str]:
    """
    Validate registration number format: YYXXXNNNNN
    YY: Year (20-29)
    XXX: Department code (3 uppercase letters from valid list)
    NNNNN: Student ID (5 digits from 10001-19999)
    
    Example: 24BET10001
    Returns: (is_valid: bool, message: str)
    """
    valid_departments = [
        "BAC", "BAI", "BAS", "BBA", "BCE", "BCG", "BCY",
        "BEC", "BET", "BEY", "BHI", "BME", "BMR", "BOE"
    ]
    
    # Check length
    if len(reg_no) != 10:
        return False, "Registration number must be 10 characters (e.g., 24BET10001)"
    
    # Extract parts using regex
    match = re.match(r'^(\d{2})([A-Z]{3})(\d{5})$', reg_no)
    
    if not match:
        return False, "Invalid format. Expected: YY-XXX-NNNNN (e.g., 24BET10001)"
    
    year_code, dept_code, student_id = match.groups()
    
    # Validate year code (20-29)
    year = int(year_code)
    if year < 20 or year > 29:
        return False, f"Year code must be between 20-29 (e.g., 24 for 2024)"
    
    # Validate department code
    if dept_code not in valid_departments:
        valid_depts = ", ".join(valid_departments)
        return False, f"Invalid department code '{dept_code}'. Valid codes: {valid_depts}"
    
    # Validate student ID (must be between 10001-19999)
    student_id_num = int(student_id)
    if student_id_num < 10001 or student_id_num > 19999:
        return False, "Student ID must be between 10001-19999"
    
    return True, f"Valid registration number: {reg_no}"


# ==================== ENUMERATIONS ====================

class CourseStatus(Enum):
    """Represents the state of a course (State Chart implementation)"""
    OPEN = "Open"
    FULL = "Full"
    CLOSED = "Closed"


class UserRole(Enum):
    """User role enumeration"""
    STUDENT = "Student"
    PROFESSOR = "Professor"
    REGISTRAR = "Registrar"


class Grade(Enum):
    """Grade enumeration"""
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D = "D"
    F = "F"
    INCOMPLETE = "I"
    WITHDRAWAL = "W"
    NOT_GRADED = "NG"


# ==================== CORE DOMAIN CLASSES ====================

class Department:
    """Represents an academic department"""
    
    def __init__(self, dept_code: str, name: str, head: Optional[str] = None):
        self._dept_code = dept_code
        self._name = name
        self._head = head
        self._courses: List['Course'] = []
    
    @property
    def dept_code(self) -> str:
        return self._dept_code
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def head(self) -> Optional[str]:
        return self._head
    
    @head.setter
    def head(self, value: str):
        self._head = value
    
    def add_course(self, course: 'Course'):
        """Add a course to the department"""
        if course not in self._courses:
            self._courses.append(course)
    
    def get_courses(self) -> List['Course']:
        """Get all courses in the department"""
        return self._courses.copy()
    
    def __str__(self) -> str:
        return f"{self._dept_code} - {self._name}"


class Person:
    """Abstract base class for all users (Demonstrates Abstraction)"""
    
    def __init__(self, user_id: str, name: str, email: str, password: str):
        self._user_id = user_id
        self._name = name
        self._email = email
        self._password = password
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    def authenticate(self, password: str) -> bool:
        """Authenticate user with password"""
        return self._password == password
    
    def get_role(self) -> UserRole:
        """Abstract method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_role()")
    
    def __str__(self) -> str:
        return f"{self._name} ({self._user_id})"


class Student(Person):
    """Student class with enrollment and grade management"""
    
    def __init__(self, student_id: str, name: str, email: str, password: str, 
                 department: Department, admission_year: int):
        super().__init__(student_id, name, email, password)
        self._department = department
        self._admission_year = admission_year
        self._enrollments: List['Registration'] = []
        self._gpa: float = 0.0
        self._total_credits: int = 0
    
    @property
    def department(self) -> Department:
        return self._department
    
    @property
    def admission_year(self) -> int:
        return self._admission_year
    
    @property
    def gpa(self) -> float:
        return self._gpa
    
    @property
    def total_credits(self) -> int:
        return self._total_credits
    
    def get_role(self) -> UserRole:
        return UserRole.STUDENT
    
    def enroll_course(self, registration: 'Registration'):
        """Enroll in a course"""
        if registration not in self._enrollments:
            self._enrollments.append(registration)
            self._total_credits += registration.course.credits
    
    def drop_course(self, registration: 'Registration'):
        """Drop a course"""
        if registration in self._enrollments:
            self._enrollments.remove(registration)
            self._total_credits -= registration.course.credits
    
    def get_enrollments(self) -> List['Registration']:
        """Get all course enrollments"""
        return self._enrollments.copy()
    
    def calculate_gpa(self):
        """Calculate GPA based on completed courses with grades"""
        grade_points = {
            Grade.A_PLUS: 4.0, Grade.A: 4.0, Grade.A_MINUS: 3.7,
            Grade.B_PLUS: 3.3, Grade.B: 3.0, Grade.B_MINUS: 2.7,
            Grade.C_PLUS: 2.3, Grade.C: 2.0, Grade.C_MINUS: 1.7,
            Grade.D: 1.0, Grade.F: 0.0
        }
        
        total_points = 0.0
        total_credits = 0
        
        for enrollment in self._enrollments:
            if enrollment.grade and enrollment.grade in grade_points:
                total_points += grade_points[enrollment.grade] * enrollment.course.credits
                total_credits += enrollment.course.credits
        
        self._gpa = total_points / total_credits if total_credits > 0 else 0.0
        return self._gpa
    
    def get_grade_report(self) -> Dict:
        """Generate grade report"""
        report = {
            'student_id': self._user_id,
            'name': self._name,
            'department': str(self._department),
            'gpa': round(self.calculate_gpa(), 2),
            'total_credits': self._total_credits,
            'courses': []
        }
        
        for enrollment in self._enrollments:
            course_info = {
                'code': enrollment.course.course_code,
                'name': enrollment.course.name,
                'credits': enrollment.course.credits,
                'grade': enrollment.grade.value if enrollment.grade else 'Not Graded',
                'semester': enrollment.semester
            }
            report['courses'].append(course_info)
        
        return report


class Professor(Person):
    """Professor class with course teaching responsibilities"""
    
    def __init__(self, professor_id: str, name: str, email: str, password: str,
                 department: Department, specialization: str):
        super().__init__(professor_id, name, email, password)
        self._department = department
        self._specialization = specialization
        self._teaching_courses: List['Course'] = []
    
    @property
    def department(self) -> Department:
        return self._department
    
    @property
    def specialization(self) -> str:
        return self._specialization
    
    def get_role(self) -> UserRole:
        return UserRole.PROFESSOR
    
    def assign_course(self, course: 'Course'):
        """Assign a course to teach"""
        if course not in self._teaching_courses:
            self._teaching_courses.append(course)
            course.instructor = self
    
    def remove_course(self, course: 'Course'):
        """Remove a course from teaching list"""
        if course in self._teaching_courses:
            self._teaching_courses.remove(course)
    
    def get_teaching_courses(self) -> List['Course']:
        """Get all courses being taught"""
        return self._teaching_courses.copy()
    
    def assign_grade(self, registration: 'Registration', grade: Grade):
        """Assign a grade to a student for a course"""
        if registration.course in self._teaching_courses:
            registration.assign_grade(grade)
            return True
        return False
    
    def get_enrolled_students(self, course: 'Course') -> List['Registration']:
        """Get all students enrolled in a specific course"""
        if course in self._teaching_courses:
            return course.get_enrolled_students()
        return []


class Registrar(Person):
    """Registrar class with administrative privileges"""
    
    def __init__(self, registrar_id: str, name: str, email: str, password: str):
        super().__init__(registrar_id, name, email, password)
    
    def get_role(self) -> UserRole:
        return UserRole.REGISTRAR
    
    def add_student(self, system: 'RegistrationSystem', student: Student):
        """Add a new student to the system"""
        system._students[student.user_id] = student
    
    def remove_student(self, system: 'RegistrationSystem', student_id: str):
        """Remove a student from the system"""
        if student_id in system._students:
            del system._students[student_id]
    
    def add_course(self, system: 'RegistrationSystem', course: 'Course'):
        """Add a new course to the system"""
        system._courses[course.course_code] = course
    
    def remove_course(self, system: 'RegistrationSystem', course_code: str):
        """Remove a course from the system"""
        if course_code in system._courses:
            del system._courses[course_code]
    
    def update_course_status(self, course: 'Course', status: CourseStatus):
        """Update course status"""
        course.status = status
    
    def generate_system_report(self, system: 'RegistrationSystem') -> Dict:
        """Generate comprehensive system report"""
        return {
            'total_students': len(system._students),
            'total_courses': len(system._courses),
            'total_professors': len(system._professors),
            'total_enrollments': sum(len(course.get_enrolled_students()) 
                                    for course in system._courses.values()),
            'departments': len(system._departments)
        }


class Course:
    """Course class representing an academic course"""
    
    def __init__(self, course_code: str, name: str, credits: int,
                 department: Department, max_capacity: int, 
                 semester: str, year: int):
        self._course_code = course_code
        self._name = name
        self._credits = credits
        self._department = department
        self._max_capacity = max_capacity
        self._semester = semester
        self._year = year
        self._instructor: Optional[Professor] = None
        self._status = CourseStatus.OPEN
        self._enrolled_students: List['Registration'] = []
        self._prerequisites: List['Course'] = []
        
        # Add course to department
        department.add_course(self)
    
    @property
    def course_code(self) -> str:
        return self._course_code
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def credits(self) -> int:
        return self._credits
    
    @property
    def department(self) -> Department:
        return self._department
    
    @property
    def max_capacity(self) -> int:
        return self._max_capacity
    
    @property
    def semester(self) -> str:
        return self._semester
    
    @property
    def year(self) -> int:
        return self._year
    
    @property
    def instructor(self) -> Optional[Professor]:
        return self._instructor
    
    @instructor.setter
    def instructor(self, professor: Professor):
        self._instructor = professor
    
    @property
    def status(self) -> CourseStatus:
        return self._status
    
    @status.setter
    def status(self, value: CourseStatus):
        self._status = value
    
    def get_current_enrollment(self) -> int:
        """Get current enrollment count"""
        return len(self._enrolled_students)
    
    def is_full(self) -> bool:
        """Check if course is full"""
        return self.get_current_enrollment() >= self._max_capacity
    
    def add_prerequisite(self, course: 'Course'):
        """Add a prerequisite course"""
        if course not in self._prerequisites:
            self._prerequisites.append(course)
    
    def get_prerequisites(self) -> List['Course']:
        """Get all prerequisites"""
        return self._prerequisites.copy()
    
    def enroll_student(self, registration: 'Registration') -> bool:
        """Enroll a student in the course"""
        if self._status == CourseStatus.CLOSED:
            return False
        
        if self.is_full():
            self._status = CourseStatus.FULL
            return False
        
        self._enrolled_students.append(registration)
        
        # Update status if now full
        if self.is_full():
            self._status = CourseStatus.FULL
        
        return True
    
    def drop_student(self, registration: 'Registration'):
        """Drop a student from the course"""
        if registration in self._enrolled_students:
            self._enrolled_students.remove(registration)
            
            # Update status if no longer full
            if self._status == CourseStatus.FULL and not self.is_full():
                self._status = CourseStatus.OPEN
    
    def get_enrolled_students(self) -> List['Registration']:
        """Get all enrolled students"""
        return self._enrolled_students.copy()
    
    def update_status(self):
        """Update course status based on enrollment (State Chart logic)"""
        if self._status == CourseStatus.CLOSED:
            return
        
        if self.is_full():
            self._status = CourseStatus.FULL
        else:
            self._status = CourseStatus.OPEN
    
    def __str__(self) -> str:
        instructor_name = self._instructor.name if self._instructor else "TBA"
        return f"{self._course_code} - {self._name} ({instructor_name})"


class Registration:
    """Registration class representing a student's course enrollment"""
    
    _registration_counter = 1000
    
    def __init__(self, student: Student, course: Course, semester: str):
        Registration._registration_counter += 1
        self._registration_id = f"{student.user_id}_{course.course_code}"
        self._student = student
        self._course = course
        self._semester = semester
        self._enrollment_date = datetime.now()
        self._grade: Optional[Grade] = None
        self._status = "Active"
    
    @property
    def registration_id(self) -> str:
        return self._registration_id
    
    @property
    def student(self) -> Student:
        return self._student
    
    @property
    def course(self) -> Course:
        return self._course
    
    @property
    def semester(self) -> str:
        return self._semester
    
    @property
    def enrollment_date(self) -> datetime:
        return self._enrollment_date
    
    @property
    def grade(self) -> Optional[Grade]:
        return self._grade
    
    @property
    def status(self) -> str:
        return self._status
    
    def assign_grade(self, grade: Grade):
        """Assign a grade to this registration"""
        self._grade = grade
    
    def drop(self):
        """Mark registration as dropped"""
        self._status = "Dropped"
        self._grade = Grade.WITHDRAWAL
    
    def __str__(self) -> str:
        return f"{self._registration_id}: {self._student.name} - {self._course.course_code}"


# ==================== REGISTRATION SYSTEM (FACADE) ====================

class RegistrationSystem:
    """
    Main system class implementing the Facade pattern
    Manages all system operations and coordinates between components
    """
    
    def __init__(self):
        self._students: Dict[str, Student] = {}
        self._professors: Dict[str, Professor] = {}
        self._registrars: Dict[str, Registrar] = {}
        self._courses: Dict[str, Course] = {}
        self._departments: Dict[str, Department] = {}
        self._registrations: List[Registration] = []
        self._current_user: Optional[Person] = None
    
    # ========== Authentication ==========
    
    def login(self, user_id: str, password: str) -> Optional[Person]:
        """Authenticate and login a user (Use Case: Login)"""
        # Check in students
        if user_id in self._students:
            user = self._students[user_id]
            if user.authenticate(password):
                self._current_user = user
                return user
        
        # Check in professors
        if user_id in self._professors:
            user = self._professors[user_id]
            if user.authenticate(password):
                self._current_user = user
                return user
        
        # Check in registrars
        if user_id in self._registrars:
            user = self._registrars[user_id]
            if user.authenticate(password):
                self._current_user = user
                return user
        
        return None
    
    def logout(self):
        """Logout current user"""
        self._current_user = None
    
    def get_current_user(self) -> Optional[Person]:
        """Get currently logged in user"""
        return self._current_user
    
    # ========== Department Management ==========
    
    def add_department(self, dept_code: str, name: str, head: Optional[str] = None) -> Department:
        """Add a new department"""
        dept = Department(dept_code, name, head)
        self._departments[dept_code] = dept
        return dept
    
    def get_department(self, dept_code: str) -> Optional[Department]:
        """Get department by code"""
        return self._departments.get(dept_code)
    
    def get_all_departments(self) -> List[Department]:
        """Get all departments"""
        return list(self._departments.values())
    
    # ========== User Management ==========
    
    def add_student(self, student_id: str, name: str, email: str, password: str,
                   department: Department, admission_year: int) -> Student:
        """Add a new student"""
        student = Student(student_id, name, email, password, department, admission_year)
        self._students[student_id] = student
        return student
    
    def add_professor(self, professor_id: str, name: str, email: str, password: str,
                     department: Department, specialization: str) -> Professor:
        """Add a new professor"""
        professor = Professor(professor_id, name, email, password, department, specialization)
        self._professors[professor_id] = professor
        return professor
    
    def add_registrar(self, registrar_id: str, name: str, email: str, password: str) -> Registrar:
        """Add a new registrar"""
        registrar = Registrar(registrar_id, name, email, password)
        self._registrars[registrar_id] = registrar
        return registrar
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        return self._students.get(student_id)
    
    def get_professor(self, professor_id: str) -> Optional[Professor]:
        """Get professor by ID"""
        return self._professors.get(professor_id)
    
    def get_all_students(self) -> List[Student]:
        """Get all students"""
        return list(self._students.values())
    
    def get_all_professors(self) -> List[Professor]:
        """Get all professors"""
        return list(self._professors.values())
    
    # ========== Course Management ==========
    
    def add_course(self, course_code: str, name: str, credits: int,
                  department: Department, max_capacity: int,
                  semester: str, year: int) -> Course:
        """Add a new course"""
        course = Course(course_code, name, credits, department, max_capacity, semester, year)
        self._courses[course_code] = course
        return course
    
    def get_course(self, course_code: str) -> Optional[Course]:
        """Get course by code"""
        return self._courses.get(course_code)
    
    def get_all_courses(self) -> List[Course]:
        """Get all courses"""
        return list(self._courses.values())
    
    def get_available_courses(self) -> List[Course]:
        """Get all available (open) courses"""
        return [course for course in self._courses.values() 
                if course.status == CourseStatus.OPEN]
    
    def search_courses(self, keyword: str = "", department: str = "") -> List[Course]:
        """Search courses by keyword and/or department"""
        results = []
        for course in self._courses.values():
            if department and course.department.dept_code != department:
                continue
            if keyword and keyword.lower() not in course.name.lower() and keyword.lower() not in course.course_code.lower():
                continue
            results.append(course)
        return results
    
    # ========== Registration Management (Use Case: Register for Course) ==========
    
    def register_student_for_course(self, student: Student, course: Course, 
                                   semester: str) -> tuple[bool, str]:
        """
        Register a student for a course
        Returns: (success: bool, message: str)
        Implements the sequence diagram flow for enrollment
        """
        # Check if course is available
        if course.status == CourseStatus.CLOSED:
            return False, "Course is closed for registration"
        
        if course.status == CourseStatus.FULL:
            return False, "Course is full"
        
        # Check if already enrolled
        for reg in student.get_enrollments():
            if reg.course.course_code == course.course_code and reg.status == "Active":
                return False, "Already enrolled in this course"
        
        # Check prerequisites
        student_completed_courses = {reg.course.course_code 
                                    for reg in student.get_enrollments() 
                                    if reg.grade and reg.grade not in [Grade.F, Grade.INCOMPLETE, Grade.WITHDRAWAL]}
        
        for prereq in course.get_prerequisites():
            if prereq.course_code not in student_completed_courses:
                return False, f"Prerequisite not met: {prereq.name}"
        
        # Create registration
        registration = Registration(student, course, semester)
        
        # Enroll student in course
        if course.enroll_student(registration):
            student.enroll_course(registration)
            self._registrations.append(registration)
            return True, "Successfully registered for course"
        
        return False, "Failed to register for course"
    
    def drop_course(self, student: Student, course: Course) -> tuple[bool, str]:
        """
        Drop a course for a student
        Returns: (success: bool, message: str)
        """
        # Find the registration
        registration = None
        for reg in student.get_enrollments():
            if reg.course.course_code == course.course_code and reg.status == "Active":
                registration = reg
                break
        
        if not registration:
            return False, "Not enrolled in this course"
        
        # Drop the course
        registration.drop()
        course.drop_student(registration)
        student.drop_course(registration)
        
        return True, "Successfully dropped course"
    
    # ========== Grading ==========
    
    def assign_grade(self, professor: Professor, student: Student, 
                    course: Course, grade: Grade) -> tuple[bool, str]:
        """Professor assigns grade to student"""
        # Find the registration
        registration = None
        for reg in student.get_enrollments():
            if reg.course.course_code == course.course_code:
                registration = reg
                break
        
        if not registration:
            return False, "Student not enrolled in course"
        
        if professor.assign_grade(registration, grade):
            return True, "Grade assigned successfully"
        
        return False, "Professor not authorized to grade this course"
    
    # ========== Reporting ==========
    
    def get_student_grade_report(self, student: Student) -> Dict:
        """Get grade report for a student (Use Case: View Grade Report)"""
        return student.get_grade_report()
    
    def get_course_enrollment_report(self, course: Course) -> Dict:
        """Get enrollment report for a course"""
        enrollments = course.get_enrolled_students()
        return {
            'course_code': course.course_code,
            'course_name': course.name,
            'instructor': course.instructor.name if course.instructor else "TBA",
            'capacity': course.max_capacity,
            'enrolled': len(enrollments),
            'available_seats': course.max_capacity - len(enrollments),
            'status': course.status.value,
            'students': [
                {
                    'student_id': reg.student.user_id,
                    'name': reg.student.name,
                    'grade': reg.grade.value if reg.grade else "Not Graded"
                }
                for reg in enrollments
            ]
        }
    
    def get_system_statistics(self) -> Dict:
        """Get overall system statistics"""
        return {
            'total_students': len(self._students),
            'total_professors': len(self._professors),
            'total_courses': len(self._courses),
            'total_departments': len(self._departments),
            'total_registrations': len(self._registrations),
            'active_registrations': len([r for r in self._registrations if r.status == "Active"])
        }
    
    # ========== Data Persistence ==========
    
    def save_to_file(self, filename: str = "system_data.json"):
        """Save system data to file"""
        data = {
            'departments': {code: {'name': dept.name, 'head': dept.head} 
                          for code, dept in self._departments.items()},
            'students': {
                sid: {
                    'name': s.name,
                    'email': s.email,
                    'password': s._password,
                    'department': s.department.dept_code,
                    'admission_year': s.admission_year
                }
                for sid, s in self._students.items()
            },
            'professors': {
                pid: {
                    'name': p.name,
                    'email': p.email,
                    'password': p._password,
                    'department': p.department.dept_code,
                    'specialization': p.specialization
                }
                for pid, p in self._professors.items()
            },
            'registrars': {
                rid: {
                    'name': r.name,
                    'email': r.email,
                    'password': r._password
                }
                for rid, r in self._registrars.items()
            },
            'courses': {
                code: {
                    'name': c.name,
                    'credits': c.credits,
                    'department': c.department.dept_code,
                    'max_capacity': c.max_capacity,
                    'semester': c.semester,
                    'year': c.year,
                    'instructor': c.instructor.user_id if c.instructor else None
                }
                for code, c in self._courses.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"System data saved to {filename}")


# ==================== DEMO AND TESTING ====================

def create_sample_data(system: RegistrationSystem):
    """Create sample data for demonstration"""
    
    print("=" * 60)
    print("INITIALIZING COURSE REGISTRATION SYSTEM")
    print("=" * 60)
    
    # Create Departments
    print("\n[1] Creating Departments...")
    cs_dept = system.add_department("CS", "Computer Science", "Dr. Alan Turing")
    math_dept = system.add_department("MATH", "Mathematics", "Dr. Emmy Noether")
    eng_dept = system.add_department("ENG", "Engineering", "Dr. Nikola Tesla")
    bus_dept = system.add_department("BUS", "Business Administration", "Dr. Peter Drucker")
    print(f"   ✓ Created {len(system.get_all_departments())} departments")
    
    # Create Professors
    print("\n[2] Creating Professors...")
    prof1 = system.add_professor("P001", "Dr. James Smith", "james@university.edu", 
                                "prof123", cs_dept, "Software Engineering")
    prof2 = system.add_professor("P002", "Dr. Sarah Johnson", "sarah@university.edu",
                                "prof123", cs_dept, "Artificial Intelligence")
    prof3 = system.add_professor("P003", "Dr. Michael Brown", "michael@university.edu",
                                "prof123", math_dept, "Calculus")
    prof4 = system.add_professor("P004", "Dr. Emily Davis", "emily@university.edu",
                                "prof123", eng_dept, "Mechanical Engineering")
    print(f"   ✓ Created {len(system.get_all_professors())} professors")
    
    # Create Students
    print("\n[3] Creating Students...")
    student1 = system.add_student("S1001", "Alice Williams", "alice@student.edu",
                                 "student123", cs_dept, 2023)
    student2 = system.add_student("S1002", "Bob Martinez", "bob@student.edu",
                                 "student123", cs_dept, 2023)
    student3 = system.add_student("S1003", "Carol Garcia", "carol@student.edu",
                                 "student123", math_dept, 2022)
    student4 = system.add_student("S1004", "David Lee", "david@student.edu",
                                 "student123", eng_dept, 2024)
    student5 = system.add_student("S1005", "Emma Wilson", "emma@student.edu",
                                 "student123", cs_dept, 2023)
    print(f"   ✓ Created {len(system.get_all_students())} students")
    
    # Create Registrar
    print("\n[4] Creating Registrar...")
    registrar = system.add_registrar("R001", "Admin Registrar", "admin@university.edu", "admin123")
    print("   ✓ Created registrar account")
    
    # Create Courses
    print("\n[5] Creating Courses...")
    course1 = system.add_course("CS101", "Introduction to Programming", 3, cs_dept, 30, "Fall", 2024)
    course2 = system.add_course("CS201", "Data Structures", 4, cs_dept, 25, "Fall", 2024)
    course3 = system.add_course("CS301", "Database Systems", 3, cs_dept, 20, "Fall", 2024)
    course4 = system.add_course("CS401", "Artificial Intelligence", 4, cs_dept, 15, "Fall", 2024)
    course5 = system.add_course("MATH101", "Calculus I", 4, math_dept, 40, "Fall", 2024)
    course6 = system.add_course("MATH201", "Linear Algebra", 3, math_dept, 30, "Fall", 2024)
    course7 = system.add_course("ENG101", "Engineering Mechanics", 3, eng_dept, 25, "Fall", 2024)
    course8 = system.add_course("BUS101", "Business Fundamentals", 3, bus_dept, 35, "Fall", 2024)
    print(f"   ✓ Created {len(system.get_all_courses())} courses")
    
    # Assign Professors to Courses
    print("\n[6] Assigning Professors to Courses...")
    prof1.assign_course(course1)
    prof1.assign_course(course2)
    prof2.assign_course(course3)
    prof2.assign_course(course4)
    prof3.assign_course(course5)
    prof3.assign_course(course6)
    prof4.assign_course(course7)
    print("   ✓ Assigned professors to courses")
    
    # Add Prerequisites
    print("\n[7] Setting Course Prerequisites...")
    course2.add_prerequisite(course1)  # Data Structures requires Intro to Programming
    course3.add_prerequisite(course2)  # Database Systems requires Data Structures
    course4.add_prerequisite(course2)  # AI requires Data Structures
    course6.add_prerequisite(course5)  # Linear Algebra requires Calculus I
    print("   ✓ Set course prerequisites")
    
    # Register Students for Courses
    print("\n[8] Registering Students for Courses...")
    registrations = [
        (student1, course1, "Fall 2024"),
        (student1, course5, "Fall 2024"),
        (student2, course1, "Fall 2024"),
        (student2, course8, "Fall 2024"),
        (student3, course5, "Fall 2024"),
        (student3, course6, "Fall 2024"),
        (student4, course7, "Fall 2024"),
        (student5, course1, "Fall 2024"),
    ]
    
    for student, course, semester in registrations:
        success, message = system.register_student_for_course(student, course, semester)
        if success:
            print(f"   ✓ {student.name} → {course.course_code}")
    
    # Assign Some Grades
    print("\n[9] Assigning Grades (Sample)...")
    # Note: In real scenario, only completed courses would have grades
    for reg in student1.get_enrollments():
        if reg.course.course_code == "CS101":
            prof1.assign_grade(reg, Grade.A)
    
    for reg in student3.get_enrollments():
        if reg.course.course_code == "MATH101":
            prof3.assign_grade(reg, Grade.B_PLUS)
    
    print("   ✓ Assigned sample grades")
    
    print("\n" + "=" * 60)
    print("SYSTEM INITIALIZATION COMPLETE")
    print("=" * 60)
    
    return {
        'students': [student1, student2, student3, student4, student5],
        'professors': [prof1, prof2, prof3, prof4],
        'registrar': registrar,
        'courses': [course1, course2, course3, course4, course5, course6, course7, course8]
    }


def demonstrate_system_features(system: RegistrationSystem, sample_data: Dict):
    """Demonstrate key system features"""
    
    print("\n\n" + "=" * 60)
    print("DEMONSTRATING SYSTEM FEATURES")
    print("=" * 60)
    
    # Feature 1: Student Login and Course Registration
    print("\n[FEATURE 1] Student Login and Course Registration")
    print("-" * 60)
    student = sample_data['students'][0]
    
    # Login
    logged_in_user = system.login(student.user_id, "student123")
    if logged_in_user:
        print(f"✓ Login successful: {logged_in_user.name}")
        print(f"  Role: {logged_in_user.get_role().value}")
    
    # View Available Courses
    print("\n  Available Courses:")
    available = system.get_available_courses()
    for course in available[:5]:  # Show first 5
        print(f"    • {course.course_code}: {course.name}")
        print(f"      Credits: {course.credits} | Seats: {course.get_current_enrollment()}/{course.max_capacity}")
    
    # Feature 2: View Grade Report
    print("\n[FEATURE 2] Student Grade Report")
    print("-" * 60)
    report = system.get_student_grade_report(student)
    print(f"  Student: {report['name']} ({report['student_id']})")
    print(f"  Department: {report['department']}")
    print(f"  GPA: {report['gpa']}")
    print(f"  Total Credits: {report['total_credits']}")
    print("\n  Enrolled Courses:")
    for course_info in report['courses']:
        print(f"    • {course_info['code']}: {course_info['name']}")
        print(f"      Grade: {course_info['grade']} | Credits: {course_info['credits']}")
    
    # Feature 3: Professor View
    print("\n[FEATURE 3] Professor Dashboard")
    print("-" * 60)
    prof = sample_data['professors'][0]
    system.logout()
    system.login(prof.user_id, "prof123")
    
    print(f"  Professor: {prof.name}")
    print(f"  Department: {prof.department.name}")
    print(f"  Specialization: {prof.specialization}")
    print("\n  Teaching Courses:")
    
    for course in prof.get_teaching_courses():
        print(f"\n    Course: {course.course_code} - {course.name}")
        enrollment_report = system.get_course_enrollment_report(course)
        print(f"    Enrolled: {enrollment_report['enrolled']}/{enrollment_report['capacity']}")
        print(f"    Students:")
        for student_info in enrollment_report['students'][:3]:  # Show first 3
            print(f"      • {student_info['name']} ({student_info['student_id']}) - Grade: {student_info['grade']}")
    
    # Feature 4: Registrar Functions
    print("\n[FEATURE 4] Registrar Administrative Functions")
    print("-" * 60)
    registrar = sample_data['registrar']
    system.logout()
    system.login(registrar.user_id, "admin123")
    
    stats = system.get_system_statistics()
    print("  System Statistics:")
    print(f"    • Total Students: {stats['total_students']}")
    print(f"    • Total Professors: {stats['total_professors']}")
    print(f"    • Total Courses: {stats['total_courses']}")
    print(f"    • Total Departments: {stats['total_departments']}")
    print(f"    • Active Registrations: {stats['active_registrations']}")
    
    # Feature 5: Course State Transitions
    print("\n[FEATURE 5] Course Status Management (State Chart)")
    print("-" * 60)
    course = sample_data['courses'][0]
    print(f"  Course: {course.course_code} - {course.name}")
    print(f"  Current Status: {course.status.value}")
    print(f"  Enrollment: {course.get_current_enrollment()}/{course.max_capacity}")
    print(f"  Is Full: {course.is_full()}")
    
    # Feature 6: Search Functionality
    print("\n[FEATURE 6] Course Search")
    print("-" * 60)
    search_results = system.search_courses(keyword="Data", department="CS")
    print("  Search: keyword='Data', department='CS'")
    print(f"  Results ({len(search_results)} found):")
    for course in search_results:
        print(f"    • {course.course_code}: {course.name}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


def interactive_menu(system: RegistrationSystem):
    """Interactive menu for testing the system"""
    
    while True:
        print("\n" + "=" * 60)
        print("COURSE REGISTRATION SYSTEM - MAIN MENU")
        print("=" * 60)
        
        if system.get_current_user():
            user = system.get_current_user()
            print(f"Logged in as: {user.name} ({user.get_role().value})")
        else:
            print("Not logged in")
        
        print("\n1. Login")
        print("2. View All Courses")
        print("3. View Available Courses")
        print("4. View System Statistics")
        if system.get_current_user():
            role = system.get_current_user().get_role()
            if role == UserRole.STUDENT:
                print("5. Register for Course")
                print("6. Drop Course")
                print("7. View My Courses")
                print("8. View Grade Report")
            elif role == UserRole.PROFESSOR:
                print("5. View My Teaching Courses")
                print("6. View Enrolled Students")
                print("7. Assign Grade")
            elif role == UserRole.REGISTRAR:
                print("5. Add New Student")
                print("6. Add New Course")
                print("7. View All Students")
        print("9. Logout")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("\nThank you for using the Course Registration System!")
            break
        elif choice == "1":
            # Get registration number
            reg_no = input("Enter your Reg.no: ").strip().upper()
            is_valid, message = validate_registration_number(reg_no)
            
            if is_valid:
                print(f"✓ {message}")
                user_id = input("Enter User ID: ").strip()
                password = input("Enter Password: ").strip()
                user = system.login(user_id, password)
                if user:
                    print(f"\n✓ Login successful! Welcome, {user.name}")
                else:
                    print("\n✗ Invalid credentials")
            else:
                print(f"✗ Invalid registration number: {message}")
                print("Format required: YYXXXNNNNN (e.g., 24BET10001)")
                print("  YY: Year (20-29)")
                print("  XXX: Department (BAC, BAI, BAS, BBA, BCE, BCG, BCY, BEC, BET, BEY, BHI, BME, BMR, BOE, etc.)")
                print("  NNNNN: Student ID (10001-19999)")
                
        elif choice == "2":
            print("\n" + "=" * 60)
            print("ALL COURSES")
            print("=" * 60)
            for course in system.get_all_courses():
                instructor = course.instructor.name if course.instructor else "TBA"
                print(f"\n{course.course_code}: {course.name}")
                print(f"  Instructor: {instructor}")
                print(f"  Credits: {course.credits} | Department: {course.department.dept_code}")
                print(f"  Enrollment: {course.get_current_enrollment()}/{course.max_capacity}")
                print(f"  Status: {course.status.value}")
        elif choice == "3":
            print("\n" + "=" * 60)
            print("AVAILABLE COURSES")
            print("=" * 60)
            for course in system.get_available_courses():
                instructor = course.instructor.name if course.instructor else "TBA"
                print(f"\n{course.course_code}: {course.name}")
                print(f"  Instructor: {instructor}")
                print(f"  Credits: {course.credits}")
                print(f"  Available Seats: {course.max_capacity - course.get_current_enrollment()}")
        elif choice == "4":
            print("\n" + "=" * 60)
            print("SYSTEM STATISTICS")
            print("=" * 60)
            stats = system.get_system_statistics()
            for key, value in stats.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        elif choice == "5" and system.get_current_user():
            role = system.get_current_user().get_role()
            if role == UserRole.STUDENT:
                course_code = input("Enter Course Code to register: ").strip().upper()
                course = system.get_course(course_code)
                if course:
                    success, message = system.register_student_for_course(
                        system.get_current_user(), course, "Fall 2024")
                    print(f"\n{'✓' if success else '✗'} {message}")
                else:
                    print("\n✗ Course not found")
        elif choice == "6" and system.get_current_user():
            role = system.get_current_user().get_role()
            if role == UserRole.STUDENT:
                course_code = input("Enter Course Code to drop: ").strip().upper()
                course = system.get_course(course_code)
                if course:
                    success, message = system.drop_course(system.get_current_user(), course)
                    print(f"\n{'✓' if success else '✗'} {message}")
                else:
                    print("\n✗ Course not found")
        elif choice == "7" and system.get_current_user():
            role = system.get_current_user().get_role()
            if role == UserRole.STUDENT:
                student = system.get_current_user()
                print("\n" + "=" * 60)
                print("MY ENROLLED COURSES")
                print("=" * 60)
                for reg in student.get_enrollments():
                    if reg.status == "Active":
                        print(f"\n{reg.course.course_code}: {reg.course.name}")
                        print(f"  Credits: {reg.course.credits}")
                        print(f"  Grade: {reg.grade.value if reg.grade else 'Not Graded'}")
        elif choice == "8" and system.get_current_user():
            role = system.get_current_user().get_role()
            if role == UserRole.STUDENT:
                student = system.get_current_user()
                report = system.get_student_grade_report(student)
                print("\n" + "=" * 60)
                print("GRADE REPORT")
                print("=" * 60)
                print(f"Student: {report['name']} ({report['student_id']})")
                print(f"Department: {report['department']}")
                print(f"GPA: {report['gpa']}")
                print(f"Total Credits: {report['total_credits']}")
                print("\nCourses:")
                for course_info in report['courses']:
                    print(f"\n  {course_info['code']}: {course_info['name']}")
                    print(f"    Credits: {course_info['credits']} | Grade: {course_info['grade']}")
        elif choice == "9":
            system.logout()
            print("\n✓ Logged out successfully")
        else:
            print("\n✗ Invalid choice or insufficient permissions")
        
        input("\nPress Enter to continue...")


def main():
    """Main function to run the system"""
    
    # Create system instance
    system = RegistrationSystem()
    
    # Create sample data
    sample_data = create_sample_data(system)
    
    # Demonstrate system features
    demonstrate_system_features(system, sample_data)
    
    # Save system data
    print("\n\nSaving system data...")
    system.save_to_file()
    
    # Interactive menu
    print("\n\nStarting interactive mode...")
    input("Press Enter to continue to interactive menu...")
    interactive_menu(system)


if __name__ == "__main__":
    main()