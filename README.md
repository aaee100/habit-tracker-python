
# 📅 Habit Tracker (Python + Tkinter)

![Python](https://img.shields.io/badge/Python-3.7-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![Pandas](https://img.shields.io/badge/Data-Pandas-orange)
![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-red)

## About the Project

A desktop application for recording habits, reviewing past records, and visualizing progress. Records are stored locally in `data/habits.csv`, so the app works offline. Habit Tracker is a desktop application built with **Python**, **Tkinter**, **Pandas**, **Matplotlib**, and **Seaborn** for recording habits and viewing personal progress. Users can mark habits as Done or Missed, browse records, view a daily success-rate chart, check streaks for each habit independently, and explore a calendar-style completion-percentage heatmap. Records are stored locally in a CSV file, so the app works offline.

## Features

- Record habits as **Done** or **Missed**.
- View records and filter by habit.
- Display a daily success-rate chart.
- Calculate current and longest streaks independently for each habit.
- Display a calendar-style heatmap of daily completion percentages.
- Store records locally in CSV format.

## How calculations work

### Streaks

Each habit has its own streak. Consecutive `Done` records extend a streak when their dates are exactly one day apart. A `Missed` record or a gap between recorded dates breaks the streak.

The **current streak** is the streak ending on that habit's latest recorded date. It is not automatically set to zero just because no record has been added today. If the latest record is `Missed`, the current streak is zero.

### Progress chart and heatmap

For each date, the app calculates the percentage of distinct habits recorded on that date whose latest status is `Done`. Habits without a record on that date are not included in the denominator. If the same habit has multiple records on one date, the last entry in the CSV is used for calculations.

For example, if two habits are recorded on a date and one is marked `Done`, that date shows 50%. Days with no records appear blank in the heatmap.

## Technologies

- Python
- Tkinter
- Pandas
- Matplotlib
- Seaborn

## Requirements and installation

Install the third-party packages in your Python environment:

```bash
python -m pip install pandas matplotlib seaborn
```

Run the program:

```bash
python habit_tracker_corrected.py
```

### Python 3.7.3

Python 3.7 is end-of-life, and current versions of Pandas, Matplotlib, and Seaborn may not support it. If you must use Python 3.7.3, install package versions that explicitly support that Python version. For a new setup, prefer a currently supported Python release.

## Emoji font warnings on older Windows setups

The current program uses plain text for streak labels and **does not use the fire (`🔥`) or trophy (`🏆`) emojis**. This avoids Matplotlib missing-glyph warnings for those characters on fonts that do not support them.

If warnings mentioning `Glyph 128293` (fire) or `Glyph 127942` (trophy) still appear, you may be running an older copy of the program that still includes those emojis. These are font-rendering warnings, not evidence that the habit data is corrupted.

## Project structure

```text
habit-tracker/
├── habit_tracker_corrected.py
├── data/
│   └── habits.csv
├── screenshots/
├── requirements.txt
└── README.md
```

The `data` directory and CSV file are created automatically if they do not exist.

## Possible future improvements

- Weekly and monthly summaries.
- Custom habit categories.
- Goals and target completion percentages.
- Export charts as PNG files.
- Dark mode.

