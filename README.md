# Log Monitor

A simple Python based log monitoring application.
This project is built with Python's KISS principle in mind ;)
The goal is to track the job execution times and generates a report.

## Features

- Parses CSV log files with START/END job entries
- Calculates job durations by matching PIDs  
- Generates **warnings** for jobs > 5 minutes
- Generates **errors** for jobs > 10 minutes
- Shows detailed reports with statistics

## Get Started (CMD LINE)

(see the next section for Streamlit - UI based run)

Run the dependencies:
```bash
pip install -r requirements.txt
```

Now run the log_monitor.py
```
python log_monitor.py logs.log
```

PS: Note, though venv is not required for this project, if you need to follow the standard 
instructions to create the Python virtual environments.

## Log File Format
The given Log file format (CSV): `HH:MM:SS,description,action,pid`

Here's the sample SCV:

```csv
10:30:15,Data processing job,START,12345
10:32:45,Data processing job,END,12345
10:33:10,Email service,START,12346
10:35:50,Email service,END,12346
```

## Sample Output

The output should be along the lines like this::

```
Number of entries parsed are:: 88
Job: background job xxx - Duration: 14.8 minutes
Job: scheduled task nnn - Duration: 12.4 minutes
......

============================================================
                   LOG MONITORING REPORT                    
============================================================
 SUMMARY STATISTICS

Total Jobs Processed: 45
Completed Jobs: 43
Jobs with Warnings: 9
Jobs with Errors: 10
 Duration (Average): 6.0m
 Duration (Maximum): 33.7m

DETAILED JOBS

PID      Description                    Duration     Status     Alert   
-------- ------------------------------ ------------ ---------- --------
81258    background job wmy             14.8m        Complete   ERROR   
45135    scheduled task 515             12.4m        Complete   ERROR   
...
```

## Innder Workings

The app is mainly made of three components: 

1. **LogParser** - Converts CSV entries to structured data
2. **JobTracker** - Matches START/END pairs. It also calculates durations  
3. **ReportGenerator** - Formats output and statistics


## Testing

Simple focused tests covering the essentials:

```bash
python -m pytest tests/test_all.py -v
```

(Just essential tests - no over-engineering ;))

## Project Structure

To understand the project, here's teh structure:

```
logmonitor-py
  ├── src/ # main classes
  │  ├── log_parser.py      # CSV parsing  
  │  ├── job_tracker.py     # Duration tracking
  │  └── report_generator.py # Output formatting
  ├── tests/
  │   └── test_xxx.py     # Essential tests
  ├── log_monitor.py         # Main application
  ├── logs.log                  # Sample data
  └── requirements.txt      # Dependencies
```

## Design Principles

- **Simple** - Easy to understand and modify
- **Fast** - Integer arithmetic instead of complex datetime objects
- **Focused** - Does one thing well
- **Tested** - Core functionality verified


# Log Monitor Streamlit Dashboard (a Simple Streamlit UI)

A web-based dashboard for the log monitoring application. 

The aim is to provides an intuitive interface for uploading and analysing log files.

## Features

-  **File Upload**: Drag and drop or browse to upload CSV log files (use the sample given)
-  **Interactive Dashboard**: Visual representation of job statistics (high level stats)
-  **Real-time Metrics**: Total jobs, completion rates, warnings, and errors
-  **Duration Analytics**: Average, minimum, and maximum job durations
-  **Alert Distribution**: Visual breakdown of job alerts (OK, WARNING, ERROR)
-  **Filterable Job Table**: Filter jobs by status and alert level

## pre-reqs

Make sure you create a venv before you start.

```bash
python3 -m venv .venv
source .venv/bin/activiate
```

(you can also use conda if you are familiar with it to creat ethe venv)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:

Kikc off the streamlit app - you should be able to upload your log file to show the log stats

```bash
streamlit run streamlit_app.py
```

3. Open your browser to the provided URL (typically http://localhost:8501)

## Example Log File Format

```csv
10:30:15,scheduled task 001,START,12345
10:33:20,scheduled task 001,END,12345
11:15:00,background job 002,START,67890
11:22:30,background job 002,END,67890
23:58:00,overnight batch,START,99999
00:05:00,overnight batch,END,99999
```

## Architecture

Remember, the UI is a supplimentary component to the already existign log monitoring app.

The Streamlit app integrates with the existing log monitoring components:
- `LogParser`: Parses CSV log files into structured entries
- `JobTracker`: Matches START/END entries and calculates durations
- `ReportGenerator`: Creates detailed text reports


