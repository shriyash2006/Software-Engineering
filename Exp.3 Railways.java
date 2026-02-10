import java.util.*;

public class RailwaySystem {
    private static Scanner scanner = new Scanner(System.in);
    private static Map<String, String> users = new HashMap<>();

    public static void main(String[] args) {
        System.out.println("--- Welcome to the Express Railway Portal ---");
        
        // 1. Authentication System
        System.out.print("Enter Phone Number (10 digits): ");
        String phone = scanner.next();
        
        if (phone.length() != 10) {
            System.out.println("Invalid phone number. Please restart.");
            return;
        }

        String password = phone.substring(6); // Last 4 digits
        System.out.println("Login Successful! (Your auto-password was: " + password + ")");
        
        // 2. Train Selection (Real Data)
        System.out.println("\n--- Available Trains ---");
        String[][] trains = {
            {"12002", "Bhopal Shatabdi Express"},
            {"12424", "New Delhi Rajdhani Express"},
            {"12137", "Punjab Mail"},
            {"12951", "Mumbai Rajdhani Express"}
        };

        for (int i = 0; i < trains.length; i++) {
            System.out.println((i + 1) + ". [" + trains[i][0] + "] " + trains[i][1]);
        }

        System.out.print("Select Train (1-4): ");
        int choice = scanner.nextInt();
        String selectedTrain = trains[choice - 1][1];
        String trainNo = trains[choice - 1][0];

        // 3. Location Selection
        System.out.print("\nEnter Departure Station: ");
        String start = scanner.next();
        System.out.print("Enter Destination Station: ");
        String end = scanner.next();

        // 4. Ticket Generation
        generateTicket(selectedTrain, trainNo, start, end);
    }

    public static void generateTicket(String name, String no, String from, String to) {
        long ticketID = System.currentTimeMillis() / 1000; // Unique ID based on time
        System.out.println("\n================================");
        System.out.println("       E-TICKET CONFIRMED       ");
        System.out.println("================================");
        System.out.println("Ticket ID: #" + ticketID);
        System.out.println("Train: " + no + " - " + name);
        System.out.println("Route: " + from.toUpperCase() + " >>> " + to.toUpperCase());
        System.out.println("Status: Confirmed");
        System.out.println("================================");
        System.out.println("Wish you a happy and safe journey!");
    }
}
