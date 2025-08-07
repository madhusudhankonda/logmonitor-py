#!/usr/bin/env python3
"""
Log Monitor Application

A simple log monitoring application that tracks job execution times
and generates alerts for jobs that exceed time thresholds.

Usage:
    python log_monitor.py <log_file>

The foll owing features are implemented in the iteration

1. Parses CSV log files with START/END job entries (LogParser class)
2. Tracks job duration by matching PIDs (done by JobTracker class)
3. Generates warnings for jobs > 5 minutes (dobe by JobTracker class)
4. Generates errors for jobs > 10 minutes (by JobTracker class)
5. Provides detailed reporting and statistics (this is implemented by ReportGenerator class)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src")) # Add src directory to path for imports

from src.log_parser import LogParser
from src.job_tracker import track_jobs, get_statistics, get_alert_jobs
from src.report_generator import ReportGenerator


def main():
    # Simple command line handling
    if len(sys.argv) != 2:
        print("Usage: python log_monitor.py <log_file>", file=sys.stderr)
        print("Example: python log_monitor.py logs.log", file=sys.stderr)
        sys.exit(1)
    
    # Get the log file from the command line arguments - first argument is the log file
    log_file = sys.argv[1]
    
    try:
        log_file_path = Path(log_file)

        # check if the log file exists
        if not log_file_path.exists():
            print(f"Error: Log file '{log_file}' not found.", file=sys.stderr)
            sys.exit(1)
        
        # Parse log file
        parser = LogParser() # create a new instance of the LogParser class

        # parse the log file and return a list of LogEntry objects
        entries = parser.parse_file(log_file) 
        
        # for debugging, print the number of entries
        print(f"Number of entries parsed are:: {len(entries)}")

        # Track job executions (5min warning, 10min error thresholds built-in)
        jobs = track_jobs(entries)

        for job in jobs:
            if job["complete"]:
                print(f"Job: {job['description']} - Duration: {job['duration_minutes']:.1f} minutes")

        # Get statistics
        statistics = get_statistics(jobs)
        
        
        report_generator = ReportGenerator()

        # Generate the full report 
        # - pass in the jobs and the statistics from the above
        report_generator.generate_full_report(jobs, statistics)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
