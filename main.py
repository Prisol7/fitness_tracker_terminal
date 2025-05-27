import sqlite3
import datetime
import os
from typing import Optional, Tuple

class FitnessTracker:
    def __init__(self, db_path: str = "fitness_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database and create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fitness_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                weight REAL NOT NULL,
                ran BOOLEAN NOT NULL DEFAULT 0,
                distance REAL,
                duration INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_entry(self, date: str, weight: float, ran: bool, distance: Optional[float] = None, 
                  duration: Optional[int] = None, notes: Optional[str] = None) -> bool:
        """Add a new fitness entry to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO fitness_log 
                (date, weight, ran, distance, duration, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, weight, ran, distance, duration, notes))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_recent_entries(self, limit: int = 10) -> list:
        """Get recent fitness entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, weight, ran, distance, duration, notes
            FROM fitness_log
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,))
        
        entries = cursor.fetchall()
        conn.close()
        return entries
    
    def get_weight_progress(self, days: int = 30) -> list:
        """Get weight progress for the last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, weight
            FROM fitness_log
            WHERE date >= date('now', '-{} days')
            ORDER BY date ASC
        '''.format(days))
        
        entries = cursor.fetchall()
        conn.close()
        return entries
    
    def get_running_stats(self, days: int = 30) -> dict:
        """Get running statistics for the last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_days,
                SUM(CASE WHEN ran = 1 THEN 1 ELSE 0 END) as run_days,
                AVG(CASE WHEN ran = 1 THEN distance END) as avg_distance,
                SUM(CASE WHEN ran = 1 THEN distance END) as total_distance,
                AVG(CASE WHEN ran = 1 THEN duration END) as avg_duration
            FROM fitness_log
            WHERE date >= date('now', '-{} days')
        '''.format(days))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_days': result[0] or 0,
            'run_days': result[1] or 0,
            'avg_distance': result[2] or 0,
            'total_distance': result[3] or 0,
            'avg_duration': result[4] or 0
        }

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_float_input(prompt: str, min_val: float = 0) -> float:
    """Get validated float input from user."""
    while True:
        try:
            value = float(input(prompt))
            if value >= min_val:
                return value
            else:
                print(f"Please enter a value >= {min_val}")
        except ValueError:
            print("Please enter a valid number.")

def get_int_input(prompt: str, min_val: int = 0) -> int:
    """Get validated integer input from user."""
    while True:
        try:
            value = int(input(prompt))
            if value >= min_val:
                return value
            else:
                print(f"Please enter a value >= {min_val}")
        except ValueError:
            print("Please enter a valid integer.")

def get_yes_no_input(prompt: str) -> bool:
    """Get yes/no input from user."""
    while True:
        response = input(prompt + " (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'.")

def format_duration(minutes: Optional[int]) -> str:
    """Format duration in minutes to readable format."""
    if minutes is None:
        return "N/A"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"

def main():
    tracker = FitnessTracker()
    
    while True:
        clear_screen()
        print("FITNESS TRACKER")
        print("=" * 40)
        print("1. Add today's entry")
        print("2. View recent entries")
        print("3. View weight progress")
        print("4. View running statistics")
        print("5. Add entry for specific date")
        print("6. Exit")
        print("=" * 40)
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            # Add today's entry
            clear_screen()
            print("ADD TODAY'S ENTRY")
            print("-" * 20)
            
            today = datetime.date.today().strftime('%Y-%m-%d')
            print(f"Date: {today}")
            
            weight = get_float_input("Enter your weight (lbs/kg): ")
            
            ran = get_yes_no_input("Did you run today?")
            
            distance = None
            duration = None
            
            if ran:
                distance = get_float_input("Distance (miles/km): ")
                duration = get_int_input("Duration (minutes): ")
            
            notes = input("Notes (optional): ").strip() or None
            
            if tracker.add_entry(today, weight, ran, distance, duration, notes):
                print("\nEntry added successfully!")
            else:
                print("\n Failed to add entry.")
            
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            # View recent entries
            clear_screen()
            print("RECENT ENTRIES")
            print("-" * 50)
            
            entries = tracker.get_recent_entries()
            
            if not entries:
                print("No entries found.")
            else:
                print(f"{'Date':<12} {'Weight':<8} {'Ran':<5} {'Distance':<10} {'Duration':<10} {'Notes'}")
                print("-" * 65)
                
                for entry in entries:
                    date, weight, ran, distance, duration, notes = entry
                    ran_str = "Yes" if ran else "No"
                    distance_str = f"{distance:.1f}" if distance else "N/A"
                    duration_str = format_duration(duration)
                    notes_str = notes[:15] + "..." if notes and len(notes) > 15 else notes or ""
                    
                    print(f"{date:<12} {weight:<8.1f} {ran_str:<5} {distance_str:<10} {duration_str:<10} {notes_str}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            # View weight progress
            clear_screen()
            print("WEIGHT PROGRESS (Last 30 Days)")
            print("-" * 35)
            
            progress = tracker.get_weight_progress()
            
            if not progress:
                print("No weight data found.")
            else:
                print(f"{'Date':<12} {'Weight':<8} {'Change'}")
                print("-" * 28)
                
                prev_weight = None
                for i, (date, weight) in enumerate(progress):
                    if prev_weight is not None:
                        change = weight - prev_weight
                        change_str = f"{change:+.1f}"
                    else:
                        change_str = "N/A"
                    
                    print(f"{date:<12} {weight:<8.1f} {change_str}")
                    prev_weight = weight
                
                if len(progress) >= 2:
                    total_change = progress[-1][1] - progress[0][1]
                    print(f"\nTotal change: {total_change:+.1f}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            # View running statistics
            clear_screen()
            print("🏃 RUNNING STATISTICS (Last 30 Days)")
            print("-" * 35)
            
            stats = tracker.get_running_stats()
            
            if stats['total_days'] == 0:
                print("No data found for the last 30 days.")
            else:
                run_percentage = (stats['run_days'] / stats['total_days']) * 100 if stats['total_days'] > 0 else 0
                
                print(f"Total logged days: {stats['total_days']}")
                print(f"Days ran: {stats['run_days']}")
                print(f"Run percentage: {run_percentage:.1f}%")
                print(f"Total distance: {stats['total_distance']:.1f}" if stats['total_distance'] else "Total distance: 0")
                print(f"Average distance: {stats['avg_distance']:.1f}" if stats['avg_distance'] else "Average distance: N/A")
                print(f"Average duration: {format_duration(int(stats['avg_duration']) if stats['avg_duration'] else None)}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            # Add entry for specific date
            clear_screen()
            print("ADD ENTRY FOR SPECIFIC DATE")
            print("-" * 30)
            
            while True:
                date_str = input("Enter date (YYYY-MM-DD): ").strip()
                try:
                    datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
            
            weight = get_float_input("Enter weight (lbs/kg): ")
            
            ran = get_yes_no_input("Did you run on this day?")
            
            distance = None
            duration = None
            
            if ran:
                distance = get_float_input("Distance (miles/km): ")
                duration = get_int_input("Duration (minutes): ")
            
            notes = input("Notes (optional): ").strip() or None
            
            if tracker.add_entry(date_str, weight, ran, distance, duration, notes):
                print("\nEntry added successfully!")
            else:
                print("\nFailed to add entry.")
            
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            print("\nThanks for using Fitness Tracker!")
            break
        
        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()