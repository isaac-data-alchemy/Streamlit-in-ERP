# src/visualization.py

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Plot attendance trends
def plot_attendance_trends(filtered_df):
    attendance_trends = filtered_df.groupby('Date').size().reset_index(name='Attendance Count')
    fig = px.line(attendance_trends, x='Date', y='Attendance Count', title='Attendance Trends Over Time')
    st.plotly_chart(fig, use_container_width=True)

# Plot lateness report
def plot_lateness_report(filtered_df):
    st.subheader("Lateness Report")
    lateness_df = filtered_df[filtered_df['Is Late']]
    lateness_counts = lateness_df.groupby(['Date', 'Department']).size().reset_index(name='Late Count')
    fig_late = px.bar(lateness_counts, x='Date', y='Late Count', color='Department', title='Lateness by Department Over Time')
    st.plotly_chart(fig_late, use_container_width=True)

# Plot overtime report
def plot_overtime_report(filtered_df):
    st.subheader("Overtime Report")
    overtime_df = filtered_df[filtered_df['Overtime Hours'] > 0]
    overtime_summary = overtime_df.groupby(['Employee ID', 'Date']).sum(numeric_only=True).reset_index()
    fig_overtime = px.bar(overtime_summary, x='Date', y='Overtime Hours', color='Employee ID', title='Overtime Hours by Employee')
    st.plotly_chart(fig_overtime, use_container_width=True)
