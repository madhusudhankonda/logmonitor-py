#!/usr/bin/env python3
"""
Log Monitor Streamlit Dashboard

A web-based dashboard for the log monitoring application that allows users
to upload log files and view job execution statistics in a user-friendly interface.
"""

import streamlit as st
import pandas as pd
import tempfile
import os
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.log_parser import LogParser
from src.job_tracker import track_jobs, get_statistics
from src.report_generator import ReportGenerator


def main():
    st.set_page_config(
        page_title="Log Monitor Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Log Monitor Dashboard")
    st.markdown("Upload your CSV log file to analyze job execution times and performance metrics.")
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Choose a CSV log file",
        type=['csv', 'log'],
        help="Upload a CSV file with format: HH:MM:SS,description,action,pid"
    )
    
    if uploaded_file is not None:
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_file:
                # Read the uploaded file content
                content = uploaded_file.read().decode('utf-8')
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Process the log file
            with st.spinner("Processing log file..."):
                parser = LogParser()
                entries = parser.parse_file(tmp_path)
                jobs = track_jobs(entries)
                statistics = get_statistics(jobs)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            # Display results
            display_dashboard(jobs, statistics, entries)
            
        except (ValueError, FileNotFoundError, IOError) as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("Please ensure your file follows the correct CSV format: HH:MM:SS,description,action,pid")
    else:
        # Show example format when no file is uploaded
        st.info("👆 Please upload a log file to begin analysis")
        
        with st.expander("📝 Expected File Format"):
            st.markdown("""
            Your CSV log file should contain entries in this format:
            ```
            HH:MM:SS,description,action,pid
            ```
            
            **Example:**
            ```
            10:30:15,scheduled task 001,START,12345
            10:33:20,scheduled task 001,END,12345
            11:15:00,background job 002,START,67890
            11:22:30,background job 002,END,67890
            ```
            """)


def display_dashboard(jobs, statistics, entries=None):
    """Display the main dashboard with statistics and job details."""
    
    # Summary statistics at the top
    st.header("📈 Summary Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Jobs", statistics['total_jobs'])
    
    with col2:
        st.metric("Completed Jobs", statistics['completed_jobs'])
    
    with col3:
        st.metric("Warnings", statistics.get('jobs_with_warnings', 0))
    
    with col4:
        st.metric("Errors", statistics.get('jobs_with_errors', 0))
    
    with col5:
        incomplete = statistics.get('incomplete_jobs', 0)
        st.metric("Incomplete", incomplete)
    
    # Duration statistics (if available)
    if statistics.get('avg_duration_minutes'):
        st.header("⏱️ Duration Statistics")
        dur_col1, dur_col2, dur_col3 = st.columns(3)
        
        with dur_col1:
            avg_duration = statistics['avg_duration_minutes']
            st.metric("Average Duration", f"{avg_duration:.1f}m")
        
        with dur_col2:
            min_duration = statistics['min_duration_minutes']
            if min_duration < 1:
                min_display = f"{min_duration*60:.0f}s"
            else:
                min_display = f"{min_duration:.1f}m"
            st.metric("Minimum Duration", min_display)
        
        with dur_col3:
            max_duration = statistics['max_duration_minutes']
            st.metric("Maximum Duration", f"{max_duration:.1f}m")
    
    # Alert distribution
    if statistics['completed_jobs'] > 0:
        st.header("🚨 Alert Distribution")
        
        alert_data = {
            'Alert Level': ['OK', 'WARNING', 'ERROR'],
            'Count': [
                statistics['completed_jobs'] - statistics.get('jobs_with_warnings', 0) - statistics.get('jobs_with_errors', 0),
                statistics.get('jobs_with_warnings', 0),
                statistics.get('jobs_with_errors', 0)
            ]
        }
        
        alert_df = pd.DataFrame(alert_data)
        st.bar_chart(alert_df.set_index('Alert Level'))
    
    # Detailed job table
    st.header("📋 Job Details")
    
    if jobs:
        # Convert jobs to DataFrame for better display
        job_df = create_job_dataframe(jobs)
        
        # Add filtering options
        col1, col2 = st.columns(2)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status:",
                ["All", "Complete", "Incomplete"]
            )
        
        with col2:
            alert_filter = st.selectbox(
                "Filter by Alert Level:",
                ["All", "OK", "WARNING", "ERROR"]
            )
        
        # Apply filters
        filtered_df = job_df.copy()
        
        if status_filter != "All":
            if status_filter == "Complete":
                filtered_df = filtered_df[filtered_df['Status'] == 'Complete']
            else:
                filtered_df = filtered_df[filtered_df['Status'] == 'Incomplete']
        
        if alert_filter != "All":
            filtered_df = filtered_df[filtered_df['Alert'] == alert_filter]
        
        # Display the table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download option for detailed report
        if st.button("📥 Generate Detailed Report"):
            generate_detailed_report(jobs, statistics)
    else:
        st.warning("No jobs found in the log file.")


def create_job_dataframe(jobs):
    """Convert jobs list to a pandas DataFrame for display."""
    
    data = []
    for job in jobs:
        # Format duration
        if job['complete'] and job['duration_minutes'] > 0:
            if job['duration_minutes'] < 1:
                duration_str = f"{job['duration_minutes']*60:.0f}s"
            else:
                duration_str = f"{job['duration_minutes']:.1f}m"
        else:
            duration_str = "N/A"
        
        data.append({
            'PID': job['pid'],
            'Description': job['description'],
            'Duration': duration_str,
            'Status': 'Complete' if job['complete'] else 'Incomplete',
            'Alert': job['alert'] if job['complete'] else '-'
        })
    
    return pd.DataFrame(data)


def generate_detailed_report(jobs, statistics):
    """Generate and display a detailed text report."""
    
    report_generator = ReportGenerator()
    
    # Create a temporary file to capture the report output
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp_file:
        # Redirect stdout to capture the report
        original_stdout = sys.stdout
        sys.stdout = tmp_file
        
        try:
            report_generator.generate_full_report(jobs, statistics)
        finally:
            sys.stdout = original_stdout
        
        # Read the report content
        tmp_file.seek(0)
        report_content = tmp_file.read()
    
    # Clean up
    os.unlink(tmp_file.name)
    
    # Display the report
    st.text_area(
        "Detailed Report:",
        value=report_content,
        height=400,
        help="Copy this report content to save or share"
    )


if __name__ == "__main__":
    main()
