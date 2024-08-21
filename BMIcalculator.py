import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

# Database setup
conn = sqlite3.connect('bmi_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY, name TEXT, height REAL, weight REAL, bmi REAL, category TEXT)''')
conn.commit()

# BMI Calculation and Categorization
def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100  # Convert height from cm to meters
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

# GUI Setup
class BMICalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.geometry("400x300")

        # Labels and Entry widgets
        tk.Label(self, text="Name:").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        tk.Label(self, text="Height (cm):").pack()
        self.height_entry = tk.Entry(self)
        self.height_entry.pack()

        tk.Label(self, text="Weight (kg):").pack()
        self.weight_entry = tk.Entry(self)
        self.weight_entry.pack()

        # Calculate button
        self.calc_button = tk.Button(self, text="Calculate BMI", command=self.calculate_and_save)
        self.calc_button.pack(pady=10)

        # Result label
        self.result_label = tk.Label(self, text="")
        self.result_label.pack()

        # History button
        self.history_button = tk.Button(self, text="View History", command=self.view_history)
        self.history_button.pack(pady=5)

    def calculate_and_save(self):
        try:
            name = self.name_entry.get()
            height_cm = float(self.height_entry.get())
            weight = float(self.weight_entry.get())

            if not name or height_cm <= 0 or weight <= 0:
                raise ValueError("Invalid input")

            bmi = calculate_bmi(weight, height_cm)
            category = categorize_bmi(bmi)

            self.result_label.config(text=f"BMI: {bmi}, Category: {category}")

            # Save to database
            cursor.execute("INSERT INTO users (name, height, weight, bmi, category) VALUES (?, ?, ?, ?, ?)", 
                           (name, height_cm, weight, bmi, category))
            conn.commit()

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid values for height and weight.")

    def view_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("BMI History")
        history_window.geometry("400x300")

        data = pd.read_sql_query("SELECT * FROM users", conn)

        if not data.empty:
            data.plot(x='id', y='bmi', kind='line', title='BMI Trend')
            plt.show()
        else:
            messagebox.showinfo("No Data", "No history available.")

if __name__ == "__main__":
    app = BMICalculator()
    app.mainloop()

    # Close the database connection when the app is closed
    conn.close()
