"""
Log Parser class that parses a CSV log file and returns a list of LogEntry objects.

"""

import csv
from typing import List, Dict, Any
from dataclasses import dataclass


"""
This class represents a single log entry.
    Make sure we represent the log file provided by the user
"""
@dataclass
class LogEntry:
    
    timestamp: int  # Seconds since start of day
    description: str
    action: str  # START or END type of log entry
    pid: str
    raw_line: str

"""
    Thsi class parses CSV log files 
     It extracts structured log entries

    Expected CSV format: "HH:MM:SS,description,action,pid"
"""
    
class LogParser:
    
    def __init__(self):
        self.entries: List[LogEntry] = []
    
    def parse_file(self, file_path: str) -> List[LogEntry]:
        """
        Parse a CSV log file and return a list of LogEntry objects.

        """
        entries = []
        
        try:
            with open(file_path, 'r', newline='') as file:
                csv_reader = csv.reader(file)
                
                for line_num, row in enumerate(csv_reader, 1):
                    try:
                        entry = self._parse_row(row, line_num)
                        entries.append(entry)
                    except ValueError as e:
                        # Log the error but continue processing other entries
                        print(f"Warning: Skipping malformed entry on line {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {file_path}")
        
        self.entries = entries
        
        return entries
    
    """
    Parse a single CSV row into a LogEntry object.
    """
    
    def _parse_row(self, row: List[str], line_num: int) -> LogEntry:
 
        if len(row) != 4:
            raise ValueError(f"Expected 4 columns, but got incorrect number of columns: {len(row)}: {row}")
        
        timestamp_str, description, action, pid = row
        
        try:
            # Parse timestamp as simple time string (HH:MM:SS)
            
            # We convert the time to total seconds from start of day
            time_parts = timestamp_str.strip().split(':')
            if len(time_parts) != 3:
                raise ValueError("Time must be in HH:MM:SS format")
            
            hours, minutes, seconds = map(int, time_parts)
            
            # Shall we vlalidate the time value ranges?
            if not (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
                raise ValueError("Invalid time values")
                
            # Convert to total seconds from start of day - this is important
            timestamp = hours * 3600 + minutes * 60 + seconds
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid timestamp format '{timestamp_str}': {e}")
        
        # Validate action
        action = action.strip().upper()
        if action not in ['START', 'END']:
            raise ValueError(f"Invalid action '{action}', expected START or END")
        
        # Validate PID
        pid = pid.strip()
        if not pid:
            raise ValueError("PID cannot be empty")
        
        return LogEntry(
            timestamp=timestamp,
            description=description.strip(),
            action=action,
            pid=pid,
            raw_line=','.join(row)
        )
    
    def get_entries_by_pid(self, pid: str) -> List[LogEntry]:
        """
        Get all log entries for a specific PID.        """

        return [entry for entry in self.entries if entry.pid == pid]
    
    def get_unique_pids(self) -> List[str]:
        return list(set(entry.pid for entry in self.entries))
