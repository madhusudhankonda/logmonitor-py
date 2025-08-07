"""
Job Tracker Module

Tracks job execution times by matching START and END entries,
calculating durations, and identifying jobs that exceed time thresholds.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .log_parser import LogEntry


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class JobExecution:
    """Represents a complete job execution with start and end times."""
    pid: str
    description: str
    start_time: int  # Seconds since start of day
    end_time: Optional[int] = None  # Seconds since start of day
    duration_seconds: Optional[int] = None
    alert_level: AlertLevel = AlertLevel.INFO
    
    def calculate_duration(self) -> Optional[int]:
        """Calculate job duration if both start and end times are available."""
        if self.start_time is not None and self.end_time is not None:
            self.duration_seconds = self.end_time - self.start_time
            return self.duration_seconds
        return None
    
    def get_duration_minutes(self) -> float:
        """Get duration in minutes as a float."""
        if self.duration_seconds is not None:
            return self.duration_seconds / 60.0
        return 0.0
    
    def is_complete(self) -> bool:
        """Check if the job has both start and end times."""
        return self.start_time is not None and self.end_time is not None


class JobTracker:
    """
    Tracks job executions and calculates durations based on START/END log entries.
    
    Generates alerts based on configurable time thresholds:
    - WARNING: Jobs exceeding warning_threshold (default: 5 minutes)
    - ERROR: Jobs exceeding error_threshold (default: 10 minutes)
    """
    
    def __init__(self, warning_threshold_minutes: int = 5, error_threshold_minutes: int = 10):
        """
        Initialize the job tracker with configurable thresholds.
        
        Args:
            warning_threshold_minutes: Minutes after which to generate warnings
            error_threshold_minutes: Minutes after which to generate errors
        """
        self.warning_threshold_seconds = warning_threshold_minutes * 60
        self.error_threshold_seconds = error_threshold_minutes * 60
        self.jobs: Dict[str, JobExecution] = {}
        self.completed_jobs: List[JobExecution] = []
        self.orphaned_entries: List[LogEntry] = []
    
    def process_entries(self, entries: List[LogEntry]) -> None:
        """
        Process a list of log entries to track job executions.
        
        Args:
            entries: List of LogEntry objects to process
        """
        # Sort entries by timestamp to ensure proper chronological processing
        sorted_entries = sorted(entries, key=lambda x: x.timestamp)
        
        for entry in sorted_entries:
            self._process_entry(entry)
        
        # Move any remaining incomplete jobs to completed list for reporting
        for job in self.jobs.values():
            if job.start_time:  # Has at least a start time
                self.completed_jobs.append(job)
        
        self.jobs.clear()
    
    def _process_entry(self, entry: LogEntry) -> None:
        """
        Process a single log entry to update job tracking.
        
        Args:
            entry: LogEntry to process
        """
        if entry.action == "START":
            self._handle_start_entry(entry)
        elif entry.action == "END":
            self._handle_end_entry(entry)
    
    def _handle_start_entry(self, entry: LogEntry) -> None:
        """
        Handle a START log entry.
        
        Args:
            entry: START LogEntry
        """
        if entry.pid in self.jobs:
            # PID already has a running job - this is unusual but we'll handle it
            # Move the existing job to completed (incomplete) and start a new one
            existing_job = self.jobs[entry.pid]
            self.completed_jobs.append(existing_job)
        
        self.jobs[entry.pid] = JobExecution(
            pid=entry.pid,
            description=entry.description,
            start_time=entry.timestamp
        )
    
    def _handle_end_entry(self, entry: LogEntry) -> None:
        """
        Handle an END log entry.
        
        Args:
            entry: END LogEntry
        """
        if entry.pid not in self.jobs:
            # END without START - orphaned entry
            self.orphaned_entries.append(entry)
            return
        
        job = self.jobs[entry.pid]
        job.end_time = entry.timestamp
        job.calculate_duration()
        
        # Determine alert level based on duration
        if job.duration_seconds:
            if job.duration_seconds >= self.error_threshold_seconds:
                job.alert_level = AlertLevel.ERROR
            elif job.duration_seconds >= self.warning_threshold_seconds:
                job.alert_level = AlertLevel.WARNING
        
        # Move to completed jobs
        self.completed_jobs.append(job)
        del self.jobs[entry.pid]
    
    def get_completed_jobs(self) -> List[JobExecution]:
        """
        Get all completed jobs sorted by start time.
        
        Returns:
            List of JobExecution objects
        """
        return sorted(self.completed_jobs, key=lambda x: x.start_time)
    
    def get_jobs_with_alerts(self) -> List[JobExecution]:
        """
        Get jobs that generated warnings or errors.
        
        Returns:
            List of JobExecution objects with WARNING or ERROR alert levels
        """
        return [job for job in self.completed_jobs 
                if job.alert_level in [AlertLevel.WARNING, AlertLevel.ERROR]]
    
    def get_incomplete_jobs(self) -> List[JobExecution]:
        """
        Get jobs that started but never ended.
        
        Returns:
            List of incomplete JobExecution objects
        """
        return [job for job in self.completed_jobs if not job.is_complete()]
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get summary statistics about processed jobs.
        
        Returns:
            Dictionary containing job statistics
        """
        completed = [job for job in self.completed_jobs if job.is_complete()]
        
        stats = {
            'total_jobs': len(self.completed_jobs),
            'completed_jobs': len(completed),
            'incomplete_jobs': len(self.get_incomplete_jobs()),
            'jobs_with_warnings': len([j for j in completed if j.alert_level == AlertLevel.WARNING]),
            'jobs_with_errors': len([j for j in completed if j.alert_level == AlertLevel.ERROR]),
            'orphaned_entries': len(self.orphaned_entries)
        }
        
        if completed:
            durations = [job.get_duration_minutes() for job in completed]
            stats.update({
                'avg_duration_minutes': sum(durations) / len(durations),
                'min_duration_minutes': min(durations),
                'max_duration_minutes': max(durations)
            })
        
        return stats
