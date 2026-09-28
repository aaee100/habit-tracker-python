
import tkinter as tk
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import ttk, messagebox
from pathlib import Path

# -------------------------
# File setup
# -------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILE_PATH = DATA_DIR / "habits.csv"

if not FILE_PATH.exists():
    df = pd.DataFrame(columns=["Date", "Habit", "Status"])
    df.to_csv(FILE_PATH, index=False)


# -------------------------
# Main logic functions
# -------------------------
def add_record():
    habit = entry_habit.get().strip()
    status = combo_status.get()

    if not habit:
        messagebox.showerror("Error", "Please enter a habit name.")
        return

    today = datetime.date.today().strftime("%Y-%m-%d")
    new_data = pd.DataFrame([[today, habit, status]], columns=["Date", "Habit", "Status"])

    try:
        df = pd.read_csv(FILE_PATH)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(FILE_PATH, index=False)
        messagebox.showinfo("Success", f"Recorded: {habit} → {status}")
        entry_habit.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_data():
    try:
        df = pd.read_csv(FILE_PATH)
        if df.empty:
            messagebox.showinfo("Info", "No data available yet.")
            return

        top = tk.Toplevel(root)
        top.title("Habit Records")
        top.geometry("500x400")

        # Filter frame
        frm_filter = ttk.Frame(top)
        frm_filter.pack(fill="x", pady=5)
        ttk.Label(frm_filter, text="Filter by habit:").pack(side="left", padx=5)
        habits = ["All"] + sorted(df["Habit"].unique().tolist())
        combo_filter = ttk.Combobox(frm_filter, values=habits, state="readonly")
        combo_filter.set("All")
        combo_filter.pack(side="left")

        # Table
        tree = ttk.Treeview(top, columns=("Date", "Habit", "Status"), show="headings")
        for col in ("Date", "Habit", "Status"):
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)

        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)
            selected = combo_filter.get()
            filtered_df = df if selected == "All" else df[df["Habit"] == selected]
            for _, row in filtered_df.iterrows():
                tree.insert("", "end", values=list(row))

        combo_filter.bind("<<ComboboxSelected>>", lambda e: refresh_table())
        refresh_table()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def calculate_streaks(df):
    df["Value"] = df["Status"].map({"Done": 1, "Missed": 0})
    streak_df = df.groupby("Date")["Value"].mean().reset_index()
    streak_df["Date"] = pd.to_datetime(streak_df["Date"])
    streak_df = streak_df.sort_values("Date")

    current_streak = 0
    longest_streak = 0
    previous_date = None

    for _, row in streak_df.iterrows():
        if row["Value"] == 1:
            if previous_date is None or (row["Date"] - previous_date).days == 1:
                current_streak += 1
            else:
                current_streak = 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0
        previous_date = row["Date"]

    return current_streak, longest_streak


def show_chart():
    try:
        df = pd.read_csv(FILE_PATH)

        # convert Done/Missed to 1/0
        df['Value'] = df['Status'].map({'Done': 1, 'Missed': 0})

        # group by date and compute success % (mean of 1/0)
        daily = df.groupby('Date')['Value'].mean()

        plt.figure()
        daily.plot(kind='line', marker='o')
        plt.title("Habit Success Rate Over Time")
        plt.ylabel("Success Rate")
        plt.yticks([0, 0.25, 0.5, 0.75, 1],
                   ["0%", "25%", "50%", "75%", "100%"])
        plt.xlabel("Date")
        plt.ylim(0, 1)
        plt.grid(True)
        # Calculate streaks
        current_streak, longest_streak = calculate_streaks(df)
        # Display streak text on chart
        plt.figtext(
            0.5, -0.1,
            f"🔥 Current streak: {current_streak} days    🏆 Longest streak: {longest_streak} days",
            ha="center", fontsize=10
        )
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Error X {e}")


def show_heatmap():
    try:
        df = pd.read_csv(FILE_PATH)
        df["Value"] = df["Status"].map({"Done": 1, "Missed": 0})
        df["Date"] = pd.to_datetime(df["Date"])

        # Sum habits per day
        daily = df.groupby("Date")["Value"].sum()

        # Create calendar-style pivot (week rows, weekday columns)
        heatmap_data = daily.resample("D").sum()
        heatmap_data = heatmap_data.fillna(0)

        heatmap_data = heatmap_data.to_frame("Score")
        heatmap_data["Week"] = heatmap_data.index.isocalendar().week
        heatmap_data["Weekday"] = heatmap_data.index.weekday

        pivot = heatmap_data.pivot(
            index="Week",
            columns="Weekday",
            values="Score"
        )

        plt.figure(figsize=(10, 4))
        sns.heatmap(
            pivot,
            cmap="Greens",
            linewidths=.5,
            cbar=True
        )
        plt.title("Habit Progress Heatmap (GitHub Style)")
        plt.ylabel("Week of Year")
        plt.xlabel("Day")
        plt.yticks(rotation=0)
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Heatmap Error: {e}")


# -------------------------
# GUI setup
# -------------------------
root = tk.Tk()
root.title("Habit Tracker")
root.geometry("400x300")

frm_main = ttk.Frame(root, padding=20)
frm_main.pack(fill="both", expand=True)

ttk.Label(frm_main, text="Daily Habit Tracker", font=("Segoe UI", 14, "bold")).pack(pady=5)

ttk.Label(frm_main, text="Habit Name:").pack(anchor="w")
entry_habit = ttk.Entry(frm_main)
entry_habit.pack(fill="x", pady=5)

ttk.Label(frm_main, text="Status:").pack(anchor="w")
combo_status = ttk.Combobox(frm_main, values=["Done", "Missed"], state="readonly")
combo_status.set("Done")
combo_status.pack(fill="x", pady=5)

btn_add = ttk.Button(frm_main, text="Add Record", command=add_record)
btn_add.pack(pady=5, fill="x")

btn_view = ttk.Button(frm_main, text="View All Records", command=view_data)
btn_view.pack(pady=5, fill="x")

btn_chart = ttk.Button(frm_main, text="Show Progress Chart", command=show_chart)
btn_chart.pack(pady=5, fill="x")

ttk.Button(frm_main, text="Show Habit Heatmap",
           command=show_heatmap).pack(fill="x", pady=5)

root.mainloop()
