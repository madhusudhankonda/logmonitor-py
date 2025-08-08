# Log Monitor Streamlit Dashboard

A web-based dashboard for the log monitoring application that provides an intuitive interface for uploading and analyzing log files.

## Features

- 📁 **File Upload**: Drag and drop or browse to upload CSV log files
- 📊 **Interactive Dashboard**: Visual representation of job statistics
- 📈 **Real-time Metrics**: Total jobs, completion rates, warnings, and errors
- ⏱️ **Duration Analytics**: Average, minimum, and maximum job durations
- 🚨 **Alert Distribution**: Visual breakdown of job alerts (OK, WARNING, ERROR)
- 📋 **Filterable Job Table**: Filter jobs by status and alert level
- 📥 **Report Generation**: Generate detailed text reports
- 🌙 **Day Rollover Support**: Handles jobs that span midnight

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run streamlit_app.py
```

3. Open your browser to the provided URL (typically http://localhost:8501)

## Usage

### 1. Upload a Log File
- Click "Browse files" or drag and drop your CSV log file
- Supported formats: `.csv`, `.log`
- Expected format: `HH:MM:SS,description,action,pid`

### 2. View Dashboard
Once uploaded, the dashboard displays:
- **Summary Statistics**: Key metrics at a glance
- **Duration Statistics**: Performance analytics
- **Alert Distribution**: Visual chart of job alerts
- **Job Details**: Filterable table of all jobs

### 3. Filter and Analyze
- Use the dropdown filters to focus on specific job types
- Filter by completion status (Complete/Incomplete)
- Filter by alert level (OK/WARNING/ERROR)

### 4. Generate Reports
- Click "Generate Detailed Report" for a comprehensive text report
- Copy the report content to save or share

## Example Log File Format

```csv
10:30:15,scheduled task 001,START,12345
10:33:20,scheduled task 001,END,12345
11:15:00,background job 002,START,67890
11:22:30,background job 002,END,67890
23:58:00,overnight batch,START,99999
00:05:00,overnight batch,END,99999
```

## Day Rollover Handling

The application automatically handles jobs that cross midnight:
- Jobs starting late in one day and ending early the next day
- Calculates correct duration by adding 24 hours when end < start time
- Example: Job from 23:58:00 to 00:05:00 = 7 minutes (not negative)

## Alert Levels

- **OK**: Job duration ≤ 5 minutes
- **WARNING**: Job duration > 5 minutes and ≤ 10 minutes  
- **ERROR**: Job duration > 10 minutes

## Architecture

The Streamlit app integrates with the existing log monitoring components:
- `LogParser`: Parses CSV log files into structured entries
- `JobTracker`: Matches START/END entries and calculates durations
- `ReportGenerator`: Creates detailed text reports
- Day rollover logic handles cross-midnight jobs automatically

## Troubleshooting

**File Upload Issues:**
- Ensure your file follows the exact CSV format
- Check that START and END entries have matching PIDs
- Verify timestamps are in HH:MM:SS format

**Missing Data:**
- If jobs show as incomplete, check for missing END entries
- Ensure file contains both START and END entries for each job

**Performance:**
- Large log files (>1000 entries) may take a few seconds to process
- The app shows a loading spinner during processing
