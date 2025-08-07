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

"""
  Tests for report generation

  @TODO: Add more tests for the report generator
"""
class TestReportGenerator:
    
    def test_time_formatting(self):
        
        generator = ReportGenerator()
        
        assert generator._seconds_to_time_str(3661) == "01:01:01"  # 1h 1m 1s
        assert generator._seconds_to_time_str(36000) == "10:00:00"  # 10:00:00
        assert generator._seconds_to_time_str(86399) == "23:59:59"  # 23:59:59
    
    def test_duration_formatting(self):
        
        generator = ReportGenerator()
        
        assert generator._format_duration(0.5) == "30s"      # 30 seconds
        assert generator._format_duration(5.5) == "5.5m"     # 5.5 minutes
        assert generator._format_duration(75) == "1h 15m"    # 1 hour 15 minutes


# Shall we try end to end test?? - 

class TestEndToEnd:
    
    def test_complete_workflow(self):
        # Create a simple log file - we can use the given sample log file as the basis
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
            tracker = JobTracker()
            tracker.process_entries(entries)
            jobs = tracker.get_completed_jobs()
            assert len(jobs) == 3
            
            # Get statistics - high level is fine
            stats = tracker.get_statistics()
            assert stats['total_jobs'] == 3
            assert stats['jobs_with_warnings'] == 1
            assert stats['jobs_with_errors'] == 1
            
        finally:
            os.unlink(temp_path)
