# Building a Habit Tracker with Python, Tkinter, and Pandas

## Introduction

A habit tracker can make it easier to record daily activities and review progress over time. I developed this project as a desktop application using Python, Tkinter, Pandas, Matplotlib, and Seaborn.

The application allows users to record habits as `Done` or `Missed`, browse previous entries, filter records by habit, view a daily progress chart, calculate individual habit streaks, and explore a calendar-style heatmap.

The project began as a small exercise in building a Tkinter interface and saving records to CSV. During development, it grew into a more complete application with data validation, date processing, streak calculations, and two types of visualizations.

## Features

### 1. Recording daily habits

Users enter a habit name and select one of two statuses: `Done` or `Missed`.

The application automatically assigns the current date. It checks that the habit name is not empty and that the selected status is valid before saving the entry.

Records are stored in a CSV file with three columns:

- `Date`
- `Habit`
- `Status`

### 2. Viewing and filtering records

The application opens a separate window containing a table of saved records.

Users can display all entries or select a particular habit from a dropdown menu. The table refreshes when the selected filter changes.

### 3. Daily progress chart

The progress chart displays the overall daily habit success rate.

The application converts statuses into numeric values:

- `Done` becomes `1`.
- `Missed` becomes `0`.

Pandas groups the records by date and calculates the mean. This produces the proportion of recorded habits completed on each date.

For example, if three habits were recorded on a particular date and two were marked `Done`, the success rate is approximately 67%.

Matplotlib displays these values as a line chart with a vertical scale from 0% to 100%.

### 4. Independent habit streaks

The application calculates current and longest streaks separately for each habit.

A consecutive `Done` record extends that habit's streak when it follows the previous recorded date by exactly one day. A `Missed` record or a gap between consecutive recorded dates breaks the sequence.

The current streak refers to the latest recorded sequence for that habit. It is not automatically set to zero just because no record has been added today.

The streak information is displayed beneath the progress chart, with separate current and longest values for each habit.

### 5. Calendar-style completion heatmap

The heatmap provides a calendar-style overview of daily progress.

For each date, the application calculates the percentage of distinct habits recorded on that date whose status is `Done`. Habits without an entry on that date are not included in the calculation.

The resulting percentages are displayed using Seaborn's heatmap function and a green color scale ranging from 0% to 100%.

Dates without records appear blank. This makes the heatmap different from a chart that simply counts completed records: it compares the proportion completed rather than the number of completed habits.

### 6. Local CSV storage

The application stores its data in `data/habits.csv`, inside the project directory.

Pathlib identifies the directory containing the Python script. The program creates the `data/` directory if it does not exist and creates an empty CSV file with the required columns when necessary.

CSV is a straightforward format that can also be opened and inspected using spreadsheet software.

## How the Application Works

### Setting up the data file

The program uses `Path(__file__).parent` to locate its own directory. It then creates the data directory and defines the path to `habits.csv`.

If the file is missing, Pandas creates an empty DataFrame with the columns `Date`, `Habit`, and `Status`, and saves it as the initial CSV file.

### Adding and reading records

The `add_record()` function reads the values entered in the Tkinter interface, validates them, assigns today's date, and creates a new DataFrame row.

It combines the new entry with the existing CSV records using `pd.concat()` and saves the result.

The `read_records()` function prepares records for analysis. It converts dates to a consistent datetime format, removes invalid dates, trims whitespace from habit names and statuses, and keeps only recognized statuses.

If a habit has multiple records on the same date, the last CSV entry is used for calculations.

### Calculating streaks

The `calculate_streaks()` function processes each habit independently.

It sorts the habit's records by date and checks whether each `Done` record follows the previous recorded date by one day. It maintains two values: the current streak and the longest streak.

This approach avoids combining different habits into one overall streak.

### Generating visualizations

The `show_chart()` function calculates the daily mean of the numeric status values and uses Matplotlib to display the progress line chart. It also calls `calculate_streaks()` and adds the individual streak results beneath the chart.

The `show_heatmap()` function calculates daily completion percentages, creates a continuous date range, and organizes the values by week and weekday. A pivot table reshapes the data into the grid required by Seaborn.

## Development Process and Challenges

The project started with four basic requirements: a Tkinter form, CSV storage, a table for reviewing records, and a progress chart.

The first version saved records in the Downloads folder. It provided the basic interface and allowed users to filter the records by habit.

One early problem appeared when the progress chart was added. The chart calculation encountered the text value `Missed` because the original status column contained words rather than numbers. Converting `Done` and `Missed` to `1` and `0` made it possible to calculate daily averages and display a success-rate chart.

The next stage introduced streak tracking and a calendar-style heatmap. The first streak calculation treated all recorded habits together, which did not provide a separate streak for each activity. The calculation was redesigned to group records by habit and evaluate each habit's dates independently.

The first heatmap also displayed completed-record counts. This could make days with different numbers of recorded habits difficult to compare. The calculation was changed to display the percentage of recorded habits completed on each date instead.

During development, the data file was moved from Downloads into a project-local `data/` directory. This made the application easier to organize and allowed it to create its storage location automatically.

Additional data handling was introduced to normalize dates, remove invalid records, standardize habit names and statuses, and handle multiple entries for the same habit on one date consistently.

The project also exposed a font compatibility issue. An earlier chart version used fire and trophy emojis in its streak labels. On some Windows setups, Matplotlib reported that the selected font did not contain those characters. The current program uses plain-text streak labels instead.

Finally, testing with newer pandas versions produced a deprecation warning for `DatetimeIndex.weekday`. The heatmap code was updated to use `DatetimeIndex.day_of_week`, which preserves the Monday-to-Sunday numbering.

## Technologies Used

- **Python** — application logic, date handling, and file operations.
- **Tkinter and ttk** — desktop interface, input fields, buttons, tables, and filtering.
- **Pandas** — CSV handling, data cleaning, grouping, and calculations.
- **Matplotlib** — daily progress line chart.
- **Seaborn** — calendar-style completion heatmap.
- **Pathlib** — project-relative file and directory paths.
- **datetime** — current-date handling when adding records.

## Project Structure

A typical repository layout is:

```text
habit-tracker-python/
├── habit_tracker.py
├── README.md
├── article.md
├── requirements.txt
├── .gitignore
├── data/
│   └── habits.csv
└── screenshots/
    ├── main-window.png
    ├── habit-records.png
    ├── progress-chart.png
    └── heatmap.png
```

The application creates the `data/` directory and CSV file automatically when they do not exist. If the repository is public, use fictional sample records rather than personal habit data.

## Testing and Compatibility

The program was tested with these combinations:

| Component | Environment 1 | Environment 2 |
|---|---:|---:|
| Python | 3.7.3 | 3.14.10 |
| Pandas | 1.3.5 | 3.1.1 |
| Matplotlib | 3.5.3 | 3.11.2 |
| Seaborn | 0.12.2 | 0.13.2 |

The `day_of_week` property is used in the current heatmap code to avoid the deprecation warning reported by newer pandas versions.

Python 3.7 is end-of-life, so it is best to use a currently supported Python release for new installations. When using Python 3.7.3, install package versions that support that interpreter.

## Limitations and Possible Improvements

The current application is a useful foundation, but it could be extended with:

- Weekly and monthly progress summaries.
- A selectable date range for charts.
- A habit-management interface for renaming or deleting habits.
- Editing and deleting existing records.
- Duplicate-entry warnings when a habit is recorded more than once on the same date.
- Exporting charts and reports.
- More flexible chart and table layouts.
- Optional interface themes.

The streak calculation is based on recorded entries. A missing date breaks a streak, so the application does not distinguish between a day when a habit was intentionally not scheduled and a day when a record was forgotten.

The heatmap percentage also includes only habits recorded on each date. It does not compare completion against a fixed list of every habit the user has created.

## Conclusion

The Habit Tracker demonstrates how Python can combine a desktop interface, local data storage, data processing, and visualization in one application.

The development process involved more than adding buttons and charts. It required debugging calculations, defining meaningful streak rules, choosing a useful way to compare daily progress, organizing local data, and checking compatibility across Python and library versions.

The result is a practical habit-recording application and a project that provided experience with Tkinter, Pandas, Matplotlib, Seaborn, date handling, and iterative software development.