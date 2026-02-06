import java.util.*; // import utilities for Scanner and collections
public class marks { // public class matching filename marks.java
	static class Student { // nested class to hold student data
		String reg; // student's registration number
		int[] marks; // marks array for subjects
		int total; // total marks across subjects
		double percent; // percentage score
		String grade; // grade as string
		int rank; // rank within class

		Student(String reg, int[] marks) { // constructor for Student
			this.reg = reg; // set registration number
			this.marks = marks; // set marks array
			this.total = 0; // initialize total
			for (int m : marks) { // loop through marks
				this.total += m; // accumulate total
			}
			this.percent = (double) this.total / (marks.length) ; // compute percentage (total divided by number of subjects)
			this.grade = computeGrade(this.percent); // compute grade from percentage
			this.rank = -1; // placeholder rank until computed
		}
	}

	public static String computeGrade(double percent) { // helper to determine grade from percentage
		if (percent >= 90) { // A+ threshold
			return "A+"; // return A+
		} else if (percent >= 80) { // A threshold
			return "A"; // return A
		} else if (percent >= 70) { // B threshold
			return "B"; // return B
		} else if (percent >= 60) { // C threshold
			return "C"; // return C
		} else if (percent >= 50) { // D threshold
			return "D"; // return D
		} else { // below 50
			return "F"; // return failing grade
		}
	}

	public static void main(String[] args) { // program entry point
		Scanner sc = new Scanner(System.in); // scanner for user input
		System.out.println("Welcome to the Marks Analysis System"); // welcome message
		System.out.print("Enter number of students in the class: "); // prompt for class size
		int n = 0; // initialize n
		try { // try to read integer input
			n = Integer.parseInt(sc.nextLine().trim()); // read and parse number of students
		} catch (Exception e) { // catch parse errors
			System.out.println("Invalid number entered. Exiting."); // error message
			sc.close(); // close scanner
			return; // exit program
		}
		List<Student> students = new ArrayList<>(); // list to hold students
		System.out.print("Enter number of subjects per student: "); // prompt for subject count
		int subj = 0; // initialize subject count
		try { // try to read subject count
			subj = Integer.parseInt(sc.nextLine().trim()); // parse subject count
			if (subj <= 0) { // validate subject count
				System.out.println("Subject count must be positive. Exiting."); // error message
				sc.close(); // close scanner
				return; // exit
			}
		} catch (Exception e) { // catch parse errors
			System.out.println("Invalid subject count. Exiting."); // error message
			sc.close(); // close scanner
			return; // exit
		}

		for (int i = 0; i < n; i++) { // loop to collect each student's data
			System.out.printf("\nEntering data for student %d of %d\n", i + 1, n); // show progress
			System.out.print("Enter registration number: "); // prompt reg no
			String reg = sc.nextLine().trim(); // read registration number
			int[] marks = new int[subj]; // create array for marks
			for (int j = 0; j < subj; j++) { // loop to collect marks for each subject
				while (true) { // loop until valid mark entered
					System.out.printf("Enter marks for subject %d (0-100): ", j + 1); // prompt for mark
					String line = sc.nextLine().trim(); // read input line
					try { // try to parse integer mark
						int m = Integer.parseInt(line); // parse mark
						if (m < 0 || m > 100) { // validate range
							System.out.println("Mark must be between 0 and 100. Try again."); // invalid range
							continue; // repeat input
						}
						marks[j] = m; // store mark
						break; // exit loop
					} catch (Exception ex) { // catch parse errors
						System.out.println("Invalid mark. Enter an integer between 0 and 100."); // error message
					}
				}
			}
			students.add(new Student(reg, marks)); // add student to list
		}

		// compute ranks based on total marks (higher total => better rank)
		List<Integer> totals = new ArrayList<>(); // list to store totals
		for (Student s : students) { // loop through students
			totals.add(s.total); // add each total
		}
		List<Integer> sortedTotals = new ArrayList<>(totals); // copy totals for sorting
		Collections.sort(sortedTotals, Collections.reverseOrder()); // sort descending

		for (Student s : students) { // assign ranks to each student
			int betterCount = 0; // count how many students have higher total
			for (int t : sortedTotals) { // loop through sorted totals
				if (t > s.total) { // if another total is greater
					betterCount++; // increment count
				}
			}
			s.rank = betterCount + 1; // rank is one plus how many are better
		}

		System.out.println("\nData entry complete. You can now lookup students by registration number."); // completion message
		while (true) { // lookup loop
			System.out.print("\nEnter registration number to view results (or type EXIT to quit): "); // prompt for query
			String query = sc.nextLine().trim(); // read query
			if (query.equalsIgnoreCase("EXIT")) { // exit condition
				System.out.println("Exiting. Goodbye!"); // exit message
				break; // break loop
			}
			boolean found = false; // flag for found
			for (Student s : students) { // search students list
				if (s.reg.equalsIgnoreCase(query)) { // if reg matches
					found = true; // mark found
					System.out.println("\n--- Student Report ---"); // report header
					System.out.println("Registration: " + s.reg); // show registration
					for (int k = 0; k < s.marks.length; k++) { // loop through marks
						System.out.printf("Subject %d: %d\n", k + 1, s.marks[k]); // print each subject mark
					}
					System.out.println("Total: " + s.total); // print total
					System.out.printf("Percentage: %.2f%%\n", s.percent); // print percentage
					System.out.println("Grade: " + s.grade); // print grade
					System.out.println("Class Rank: " + s.rank + " out of " + n); // print rank
					break; // stop searching after found
				}
			}
			if (!found) { // if not found
				System.out.println("Registration number not found. Try again."); // message
			}
		}
		sc.close(); // close scanner before exiting
	}
}
