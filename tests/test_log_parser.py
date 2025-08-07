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
Basic tests for log parsing.
"""
class TestLogParser:
    
    def test_parse_valid_entry(self):
        parser = LogParser()
        row = ["10:30:15", "Test job", "START", "12345"]
        entry = parser._parse_row(row, 1)
        
        assert entry.description == "Test job"
        assert entry.action == "START"
        assert entry.pid == "12345"
        # 10:30:15 = 10*3600 + 30*60 + 15 = 37815 seconds
        assert entry.timestamp == 37815
    
    def test_parse_invalid_time(self): # invalid time format
        
        parser = LogParser()
        row = ["25:99:99", "Test job", "START", "12345"]  # See that this is invalid time
        
        with pytest.raises(ValueError):
            parser._parse_row(row, 1)
    
    def test_parse_file(self):
        content = """10:00:00,Quick job,START,001
                        10:01:00,Quick job,END,001
                        10:02:00,Slow job,START,002
                        10:12:30,Slow job,END,002"""
        
        # Create a temporary file to test the parse_file method
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            parser = LogParser()
            entries = parser.parse_file(temp_path)
            assert len(entries) == 4
            assert entries[0].description == "Quick job"
            assert entries[0].action == "START"
        finally:
            os.unlink(temp_path)
