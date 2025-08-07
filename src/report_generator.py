"""
Report Generator Module

Generates human-readable reports and alerts based on job execution data.
Handles formatting and output of warnings, errors, and summary statistics.
"""

from datetime import datetime
from typing import List, TextIO
import sys

from .job_tracker import JobExecution, AlertLevel

"""
    This clss generates formatted reports for job monitoring results.

    """
    
class ReportGenerator:
    
    def __init__(self, output_file: TextIO = None):
        
        self.output_file = output_file or sys.stdout
    
    def _seconds_to_time_str(self, seconds: int) -> str:
        
        # Convert seconds since start of day to HH:MM:SS format
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}" # double check this??
    
    
    """
        Generate a complete report including all jobs and statistics.
        Send most part of the reports to functions    
    """
    def generate_full_report(self, jobs: List[JobExecution], statistics: dict) -> None:
        
        self._write_header(" LOG MONITORING REPORT ")
        
        self._write_separator()
        
        # Generate summary statistics
        self._write_statistics_section(statistics)
        
        self._write_separator()
        
        # Generate detailed job listing
        self._write_jobs_section(jobs)
        
    def _write_header(self, title: str) -> None:
        """Write a formatted header."""
        self._write_line(f"\n{'=' * 60}")
        self._write_line(f"{title:^60}")
        self._write_line(f"{'=' * 60}")
    
    def _write_separator(self) -> None:
        """Write a section separator."""
        self._write_line(f"{'-' * 60}")
    
    def _write_timestamp(self) -> None:
        """Write the current timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._write_line(f"Generated: {timestamp}")
    
    def _write_line(self, text: str = "") -> None:
        """Write a line to the output."""
        print(text, file=self.output_file)
    
    
    def _write_statistics_section(self, statistics: dict) -> None:
        self._write_line(" SUMMARY STATISTICS")
        self._write_line()
        
        self._write_line(f"Total Jobs Processed: {statistics.get('total_jobs', 0)}")
        self._write_line(f"Completed Jobs: {statistics.get('completed_jobs', 0)}")
        self._write_line(f"Incomplete Jobs: {statistics.get('incomplete_jobs', 0)}")
        self._write_line(f"Jobs with Warnings: {statistics.get('jobs_with_warnings', 0)}")
        self._write_line(f"Jobs with Errors: {statistics.get('jobs_with_errors', 0)}")
        
        if statistics.get('avg_duration_minutes'):
            avg_duration = self._format_duration(statistics['avg_duration_minutes'])
            min_duration = self._format_duration(statistics['min_duration_minutes'])
            max_duration = self._format_duration(statistics['max_duration_minutes'])
            
            self._write_line(f" Duration (Average): {avg_duration}")
            self._write_line(f" Duration (Minimum): {min_duration}")
            self._write_line(f" Duration (Maximum): {max_duration}")
    
    def _write_jobs_section(self, jobs: List[JobExecution]) -> None:
        
        if not jobs:
            return
        
        self._write_line("DETAILED JOBS")
        self._write_line()
        
        # Write table header
        # TODO: Make this more readable - kinda ugly
        self._write_line(f"{'PID':<8} {'Description':<30} {'Duration':<12} {'Status':<10} {'Alert':<8}")
        self._write_line(f"{'-' * 8} {'-' * 30} {'-' * 12} {'-' * 10} {'-' * 8}")
        
        for job in jobs:
            pid = job.pid[:7]  # Truncate long PIDs
            description = job.description[:29]  # Truncate long descriptions
            duration = self._format_duration(job.get_duration_minutes()) if job.is_complete() else "N/A"
            status = "Complete" if job.is_complete() else "Incomplete"
            alert = job.alert_level.value if job.alert_level != AlertLevel.INFO else "-"
            
            self._write_line(f"{pid:<8} {description:<30} {duration:<12} {status:<10} {alert:<8}")
    
    
    def _format_duration(self, minutes: float) -> str:
        
        if minutes < 1:
            seconds = int(minutes * 60)
            return f"{seconds}s"
        elif minutes < 60:
            return f"{minutes:.1f}m"
        else:
            hours = int(minutes // 60)
            remaining_minutes = int(minutes % 60)
            return f"{hours}h {remaining_minutes}m"
