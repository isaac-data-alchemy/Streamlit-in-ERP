# app.py

import streamlit as st
from datetime import datetime, timedelta
from src.data_processing import generate_mock_data, calculate_overtime_and_lateness
from src.layout import add_employee_form, add_shift_form, sidebar_layout
from src.visualization import plot_attendance_trends, plot_lateness_report, plot_overtime_report

# Initialize session state for storing employee and shift data
if 'employees' not in st.session_state:
    st.session_state['employees'] = pd.DataFrame(columns=['Employee ID', 'Name', 'Department', 'Role'])

if 'shifts' not in st.session_state:
    st.session_state['shifts'] = pd.DataFrame(columns=['Shift ID', 'Shift Name', 'Start Time', 'End Time', 'Assigned Employees'])

def main():
    # Sidebar navigation
    st.sidebar.title("Dashboard Navigation")
    pages = st.sidebar.radio("Go to", ["Dashboard", "Employee Scheduling", "Shift Management"])
    
    # Attendance Dashboard
    if pages == "Dashboard":
        date_range, department_filter, employee_filter = sidebar_layout()
        df = generate_mock_data()
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = calculate_overtime_and_lateness(df)

        # Filtering data
        filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]
        if department_filter:
            filtered_df = filtered_df[filtered_df['Department'].isin(department_filter)]
        if employee_filter:
            filtered_df = filtered_df[filtered_df['Employee ID'].astype(str).str.contains(employee_filter)]

        st.title("Admin Dashboard - Time and Attendance")
        plot_attendance_trends(filtered_df)
        plot_lateness_report(filtered_df)
        plot_overtime_report(filtered_df)

        # Display attendance records
        st.subheader("Attendance Records")
        st.dataframe(filtered_df)

    # Employee Scheduling Page
    elif pages == "Employee Scheduling":
        st.title("Employee Scheduling")
        add_employee_form()
        st.subheader("Current Employees")
        st.dataframe(st.session_state['employees'])

    # Shift Management Page
    elif pages == "Shift Management":
        st.title("Shift Management")
        add_shift_form()
        st.subheader("Current Shifts")
        st.dataframe(st.session_state['shifts'])

if __name__ == "__main__":
    main()
