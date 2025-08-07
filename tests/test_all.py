"""
Simple tests for the simplified log monitoring application.

@TODO: Add more tests for the job tracker and report generator
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.log_parser import LogParser, LogEntry
from src.job_tracker import track_jobs, get_statistics, get_alert_jobs
from src.report_generator import ReportGenerator

# Basic tests for log parsing
class TestLogParser:
    
    # Test parsing a valid log entry (happy path)
    def test_parse_valid_entry(self):
        
        parser = LogParser()
        row = ["10:30:15", "Test job", "START", "12345"]
        entry = parser._parse_row(row, 1)
        
        assert entry.description == "Test job"
        assert entry.action == "START"
        assert entry.pid == "12345"
        # 10:30:15 = 10*3600 + 30*60 + 15 = 37815 seconds
        assert entry.timestamp == 37815
    
    # Test parsing with invalid time format (negative case)
    def test_parse_invalid_time(self):
        
        parser = LogParser()
        row = ["25:99:99", "Test job", "START", "12345"]  # Invalid time
        
        with pytest.raises(ValueError):
            parser._parse_row(row, 1)


# Basic tests for job tracking - we can add more tests here
class TestJobTracker:
    
    # Test tracking a simple job from START to END
    def test_simple_job_tracking(self):
        
        entries = [
            LogEntry(36000, "Test job", "START", "12345", ""),  # 10:00:00
            LogEntry(36180, "Test job", "END", "12345", "")     # 10:03:00
        ]
        
        jobs = track_jobs(entries)
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["pid"] == "12345"
        assert job["duration_minutes"] == 3.0
        assert job["alert"] == "OK"
        assert job["complete"] == True
    
    # Test job that generates a warning (> 5 minutes)
    def test_warning_job(self):
        
        entries = [
            LogEntry(36000, "Slow job", "START", "12345", ""),   # 10:00:00
            LogEntry(36450, "Slow job", "END", "12345", "")      # 10:07:30
        ]
        
        jobs = track_jobs(entries)
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["duration_minutes"] == 7.5
        assert job["alert"] == "WARNING"
    
    # Test job that generates an error (threshold > 10 minutes)
    def test_error_job(self):
        
        entries = [
            LogEntry(36000, "Very slow job", "START", "12345", ""),  # 10:00:00
            LogEntry(36900, "Very slow job", "END", "12345", "")     # 10:15:00
        ]
        
        jobs = track_jobs(entries)
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["duration_minutes"] == 15.0
        assert job["alert"] == "ERROR"
    
    # Test job with START but no END
    def test_incomplete_job(self):
        
        entries = [
            LogEntry(36000, "Incomplete job", "START", "12345", "")
        ]
        
        jobs = track_jobs(entries)
        
        assert len(jobs) == 1
        job = jobs[0]
        assert job["complete"] == False
        assert job["duration_minutes"] == 0.0


# Test statistics generation reports - we can add more tests here
class TestStatistics:
    
    # Test basic statistics calculation
    def test_get_statistics(self):
        
        jobs = [
            {"complete": True, "duration_minutes": 2.0, "alert": "OK"},
            {"complete": True, "duration_minutes": 7.0, "alert": "WARNING"},
            {"complete": True, "duration_minutes": 15.0, "alert": "ERROR"},
            {"complete": False, "duration_minutes": 0.0, "alert": "OK"}
        ]
        
        stats = get_statistics(jobs)
        
        assert stats["total_jobs"] == 4
        assert stats["completed_jobs"] == 3
        assert stats["incomplete_jobs"] == 1
        assert stats["jobs_with_warnings"] == 1
        assert stats["jobs_with_errors"] == 1
        assert stats["avg_duration_minutes"] == 8.0  # (2+7+15)/3

# Basic tests for report generation
class TestReportGenerator:
    
    # Test converting seconds to time string (positive test)
    def test_time_formatting(self):
        
        generator = ReportGenerator()
        
        assert generator._seconds_to_time_str(3661) == "01:01:01"  # 1h 1m 1s
        assert generator._seconds_to_time_str(36000) == "10:00:00"  # 10:00:00
    
    # Test duration formatting (positive test)
    def test_duration_formatting(self):
        
        generator = ReportGenerator()
        
        assert generator._format_duration(0.5) == "30s"      # 30 seconds
        assert generator._format_duration(5.5) == "5.5m"     # 5.5 minutes

# Basic tests for end to end test
class TestEndToEnd:
    
    # Test the complete workflow from log parsing to tracking
    def test_complete_workflow(self):
        
        # Create a simple log file
        content = """10:00:00,Quick job,START,001
                    10:01:30,Quick job,END,001
                    10:02:00,Warning job,START,002
                    10:08:00,Warning job,END,002
                    10:10:00,Error job,START,003
                    10:22:00,Error job,END,003"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Parse
            parser = LogParser()
            entries = parser.parse_file(temp_path)
            assert len(entries) == 6
            
            # Track jobs
            jobs = track_jobs(entries)
            assert len(jobs) == 3
            
            # Get statistics here
            stats = get_statistics(jobs)
            assert stats['total_jobs'] == 3
            assert stats['jobs_with_warnings'] == 1
            assert stats['jobs_with_errors'] == 1
            
        finally:
            os.unlink(temp_path)
