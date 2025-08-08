"""
Simple Job Tracker - tracks job execution times and generates alerts.
"""

from typing import List, Dict
from .log_parser import LogEntry


def track_jobs(entries: List[LogEntry]) -> List[Dict]:
    jobs = {}  # PID -> start entry
    results = []
    
    # Sort by timestamp to handle out-of-order entries
    sorted_entries = sorted(entries, key=lambda x: x.timestamp)
    
    # First pass: process all START entries
    for entry in sorted_entries:
        if entry.action == "START":
            jobs[entry.pid] = entry
    
    # Second pass: process all END entries
    for entry in sorted_entries:
        if entry.action == "END" and entry.pid in jobs:
            start_entry = jobs[entry.pid]
            duration_seconds = entry.timestamp - start_entry.timestamp
            
            # Handle day rollover: if end time is before start time, add 24 hours (86400 seconds)
            if duration_seconds < 0:
                duration_seconds += 86400  # 24 * 60 * 60 = 86400 seconds in a day
            
            duration_minutes = duration_seconds / 60.0
            
            # Determine alert level
            if duration_minutes > 10:
                alert = "ERROR"
            elif duration_minutes > 5:
                alert = "WARNING"  
            else:
                alert = "OK"
            
            results.append({
                "pid": entry.pid,
                "description": start_entry.description,
                "start_time": start_entry.timestamp,
                "end_time": entry.timestamp,
                "duration_minutes": duration_minutes,
                "alert": alert,
                "complete": True
            })
            
            del jobs[entry.pid]  # Remove completed job
    
    # Add incomplete jobs (START without END)
    for pid, start_entry in jobs.items():
        results.append({
            "pid": pid,
            "description": start_entry.description,
            "start_time": start_entry.timestamp,
            "end_time": None,
            "duration_minutes": 0.0,
            "alert": "OK",
            "complete": False
        })
    
    return sorted(results, key=lambda x: x["start_time"])


def get_statistics(jobs: List[Dict]) -> Dict:
    complete_jobs = [job for job in jobs if job["complete"]]
    
    stats = {
        "total_jobs": len(jobs),
        "completed_jobs": len(complete_jobs),
        "incomplete_jobs": len(jobs) - len(complete_jobs),
        "jobs_with_warnings": len([j for j in complete_jobs if j["alert"] == "WARNING"]),
        "jobs_with_errors": len([j for j in complete_jobs if j["alert"] == "ERROR"])
    }
    
    if complete_jobs:
        durations = [job["duration_minutes"] for job in complete_jobs]
        stats.update({
            "avg_duration_minutes": sum(durations) / len(durations),
            "min_duration_minutes": min(durations),
            "max_duration_minutes": max(durations)
        })
    
    return stats


def get_alert_jobs(jobs: List[Dict]) -> List[Dict]:
    return [job for job in jobs if job["alert"] in ["WARNING", "ERROR"]]