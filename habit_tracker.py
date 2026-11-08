import tkinter as tk
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import ttk, messagebox
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
FILE_PATH = DATA_DIR / "habits.csv"

if not FILE_PATH.exists():
    pd.DataFrame(columns=["Date", "Habit", "Status"]).to_csv(FILE_PATH, index=False)


def read_records():
    """Read valid records and normalize dates, names, and statuses."""
    df = pd.read_csv(FILE_PATH)
    required = {"Date", "Habit", "Status"}
    if not required.issubset(df.columns):
        raise ValueError("habits.csv must contain Date, Habit, and Status columns.")
    if df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Value"] = pd.Series(dtype="float64")
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    df["Habit"] = df["Habit"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip().str.title()
    df = df.dropna(subset=["Date"])
    df = df[(df["Habit"] != "") & df["Status"].isin(["Done", "Missed"])]
    # If a habit has multiple records on a date, the last CSV entry wins.
    df = df.drop_duplicates(subset=["Date", "Habit"], keep="last").copy()
    df["Value"] = df["Status"].map({"Done": 1, "Missed": 0})
    return df


def add_record():
    habit = entry_habit.get().strip()
    status = combo_status.get()
    if not habit:
        messagebox.showerror("Error", "Please enter a habit name.")
        return
    if status not in ("Done", "Missed"):
        messagebox.showerror("Error", "Please select Done or Missed.")
        return

    today = datetime.date.today().strftime("%Y-%m-%d")
    new_data = pd.DataFrame([[today, habit, status]], columns=["Date", "Habit", "Status"])
    try:
        df = pd.read_csv(FILE_PATH)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(FILE_PATH, index=False)
        messagebox.showinfo("Success", "Recorded: {} → {}".format(habit, status))
        entry_habit.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_data():
    try:
        df = pd.read_csv(FILE_PATH)
        if df.empty:
            messagebox.showinfo("Info", "No data available yet.")
            return
        if not {"Date", "Habit", "Status"}.issubset(df.columns):
            raise ValueError("habits.csv must contain Date, Habit, and Status columns.")

        top = tk.Toplevel(root)
        top.title("Habit Records")
        top.geometry("500x400")
        frm_filter = ttk.Frame(top)
        frm_filter.pack(fill="x", pady=5)
        ttk.Label(frm_filter, text="Filter by habit:").pack(side="left", padx=5)
        habits = ["All"] + sorted(df["Habit"].dropna().astype(str).unique().tolist())
        combo_filter = ttk.Combobox(frm_filter, values=habits, state="readonly")
        combo_filter.set("All")
        combo_filter.pack(side="left")

        tree = ttk.Treeview(top, columns=("Date", "Habit", "Status"), show="headings")
        for col in ("Date", "Habit", "Status"):
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)

        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)
            selected = combo_filter.get()
            filtered = df if selected == "All" else df[df["Habit"] == selected]
            for _, row in filtered.iterrows():
                tree.insert("", "end", values=list(row))

        combo_filter.bind("<<ComboboxSelected>>", lambda event: refresh_table())
        refresh_table()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def calculate_streaks(df):
    """Return {habit: (current, longest)} with an independent streak per habit.

    A missed record or a gap between consecutive recorded dates breaks a streak.
    Current streak refers to the latest recorded sequence; it is not forced to
    zero just because no record has been added today.
    """
    if df.empty:
        return {}
    required = {"Date", "Habit", "Status"}
    if not required.issubset(df.columns):
        raise ValueError("Streak calculation requires Date, Habit, and Status columns.")

    records = df.copy()
    records["Date"] = pd.to_datetime(records["Date"], errors="coerce").dt.normalize()
    records["Habit"] = records["Habit"].astype(str).str.strip()
    records["Status"] = records["Status"].astype(str).str.strip().str.title()
    records = records.dropna(subset=["Date"])
    records = records[(records["Habit"] != "") & records["Status"].isin(["Done", "Missed"])]
    records = records.drop_duplicates(subset=["Date", "Habit"], keep="last").copy()
    records["Value"] = records["Status"].map({"Done": 1, "Missed": 0})

    streaks = {}
    for habit, habit_df in records.groupby("Habit"):
        habit_df = habit_df.sort_values("Date")
        current = longest = 0
        previous_date = None
        for _, row in habit_df.iterrows():
            date = row["Date"]
            if row["Value"] == 1:
                current = current + 1 if previous_date is not None and (date - previous_date).days == 1 else 1
                longest = max(longest, current)
            else:
                current = 0
            previous_date = date
        streaks[habit] = (current, longest)
    return streaks


def show_chart():
    try:
        df = read_records()
        if df.empty:
            messagebox.showinfo("Info", "No data available yet.")
            return
        daily = df.groupby("Date")["Value"].mean().sort_index()
        fig, ax = plt.subplots()
        daily.plot(kind="line", marker="o", ax=ax)
        ax.set_title("Habit Success Rate Over Time")
        ax.set_ylabel("Success Rate")
        ax.set_yticks([0, .25, .5, .75, 1])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
        ax.set_xlabel("Date")
        ax.set_ylim(0, 1)
        ax.grid(True)

        streaks = calculate_streaks(df)
        if streaks:
            lines = [
                "{}: current {} day(s), longest {} day(s)".format(name, current, longest)
                for name, (current, longest) in sorted(streaks.items())
            ]
            # Plain text avoids missing-emoji-glyph warnings on some fonts.
            fig.text(0.5, -0.02, "Streaks by habit\n" + "\n".join(lines),
                     ha="center", va="top", fontsize=8)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Chart Error", str(e))


def show_heatmap():
    try:
        df = read_records()
        if df.empty:
            messagebox.showinfo("Info", "No data available yet.")
            return
        # Percentage among distinct habits recorded that day, not all known habits.
        daily = (df.groupby("Date")["Value"].mean() * 100).rename("Percentage")
        dates = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
        daily = daily.reindex(dates)
        data = daily.to_frame()
        data["WeekStart"] = data.index - pd.to_timedelta(data.index.weekday, unit="D")
        data["Weekday"] = data.index.weekday
        pivot = data.pivot(index="WeekStart", columns="Weekday", values="Percentage")
        pivot = pivot.reindex(columns=[0, 1, 2, 3, 4, 5, 6]).sort_index(ascending=False)

        fig, ax = plt.subplots(figsize=(10, max(3, len(pivot) * .35)))
        sns.heatmap(pivot, cmap="Greens", linewidths=.5, cbar=True, vmin=0, vmax=100,
                    mask=pivot.isna(), cbar_kws={"label": "Habits completed (%)"}, ax=ax)
        ax.set_title("Habit Completion Percentage by Day")
        ax.set_ylabel("Week starting (Monday)")
        ax.set_xlabel("Day of week (0 = Monday, 6 = Sunday)")
        ax.set_yticklabels([label.get_text()[:10] for label in ax.get_yticklabels()], rotation=0)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Heatmap Error", str(e))


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
ttk.Button(frm_main, text="Add Record", command=add_record).pack(pady=5, fill="x")
ttk.Button(frm_main, text="View All Records", command=view_data).pack(pady=5, fill="x")
ttk.Button(frm_main, text="Show Progress Chart", command=show_chart).pack(pady=5, fill="x")
ttk.Button(frm_main, text="Show Habit Heatmap", command=show_heatmap).pack(fill="x", pady=5)
root.mainloop()
