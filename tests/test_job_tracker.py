"""
Simple tests for the log monitoring application.

Just the essential happy path and error cases
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.log_parser import LogParser, LogEntry
from src.job_tracker import JobTracker, AlertLevel
from src.report_generator import ReportGenerator


class TestJobTracker:
    
    # Test a simple job tracking from START to END.
    def test_simple_job_tracking(self):
        tracker = JobTracker()
        
        # Create log entries: 10:00:00 to 10:03:00 (3 minutes)
        entries = [
            LogEntry(36000, "Test job", "START", "12345", ""),  
            LogEntry(36180, "Test job", "END", "12345", "") 
        ]
        
        tracker.process_entries(entries)
        jobs = tracker.get_completed_jobs()
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job.pid == "12345"
        assert job.get_duration_minutes() == 3.0
        assert job.alert_level == AlertLevel.INFO  # Under 5 minutes
    
    # Test job that checks a warning (> 5 minutes)
    def test_warning_job(self):
        
        tracker = JobTracker()
        
        # Create log entries: 10:00:00 to 10:07:30 (7.5 minutes)
        entries = [
            LogEntry(36000, "Slow job", "START", "12345", ""),   # 10:00:00
            LogEntry(36450, "Slow job", "END", "12345", "")      # 10:07:30
        ]
        
        tracker.process_entries(entries)
        jobs = tracker.get_completed_jobs()
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job.get_duration_minutes() == 7.5
        assert job.alert_level == AlertLevel.WARNING
    
    def test_error_job(self):
        """Test job that generates an error (> 10 minutes)."""
        tracker = JobTracker()
        
        # Create log entries: 10:00:00 to 10:15:00 (15 minutes)
        entries = [
            LogEntry(36000, "Very slow job", "START", "12345", ""),  # 10:00:00
            LogEntry(36900, "Very slow job", "END", "12345", "")     # 10:15:00
        ]
        
        tracker.process_entries(entries)
        jobs = tracker.get_completed_jobs()
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job.get_duration_minutes() == 15.0
        assert job.alert_level == AlertLevel.ERROR
    
    def test_incomplete_job(self):
        """Test job with START but no END."""
        tracker = JobTracker()
        
        entries = [
            LogEntry(36000, "Incomplete job", "START", "12345", "")
        ]
        
        tracker.process_entries(entries)
        jobs = tracker.get_completed_jobs()
        
        assert len(jobs) == 1
        job = jobs[0]
        assert not job.is_complete()
        assert job.get_duration_minutes() == 0.0
