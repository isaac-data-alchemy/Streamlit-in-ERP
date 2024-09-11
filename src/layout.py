# src/layout.py

import streamlit as st
import pandas as pd

# Add Employee form
def add_employee_form():
    with st.form("add_employee_form"):
        st.subheader("Add New Employee")
        emp_id = st.text_input("Employee ID")
        name = st.text_input("Employee Name")
        department = st.selectbox("Department", ['HR', 'Engineering', 'Sales', 'Marketing'])
        role = st.text_input("Role")
        submitted = st.form_submit_button("Add Employee")

        if submitted:
            new_employee = pd.DataFrame(
                [{'Employee ID': emp_id, 'Name': name, 'Department': department, 'Role': role}]
            )
            st.session_state['employees'] = pd.concat([st.session_state['employees'], new_employee], ignore_index=True)
            st.success(f"Employee {name} added successfully!")

# Add Shift form
def add_shift_form():
    with st.form("add_shift_form"):
        st.subheader("Add New Shift")
        shift_id = st.text_input("Shift ID")
        shift_name = st.text_input("Shift Name")
        start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
        end_time = st.time_input("End Time", value=datetime.strptime("17:00", "%H:%M").time())
        assigned_employees = st.multiselect("Assign Employees", st.session_state['employees']['Name'].tolist())
        submitted = st.form_submit_button("Add Shift")

        if submitted:
            new_shift = pd.DataFrame(
                [{'Shift ID': shift_id, 'Shift Name': shift_name, 'Start Time': start_time, 'End Time': end_time, 'Assigned Employees': ', '.join(assigned_employees)}]
            )
            st.session_state['shifts'] = pd.concat([st.session_state['shifts'], new_shift], ignore_index=True)
            st.success(f"Shift {shift_name} added successfully!")

# Sidebar layout for filtering options
def sidebar_layout():
    st.sidebar.title("Filters")
    date_range = st.sidebar.date_input("Select Date Range", [datetime.now().date() - timedelta(365), datetime.now().date()])
    department_filter = st.sidebar.multiselect("Select Department", options=['HR', 'Engineering', 'Sales', 'Marketing'], default=['HR', 'Engineering', 'Sales', 'Marketing'])
    employee_filter = st.sidebar.text_input("Search Employee by ID")
    return date_range, department_filter, employee_filter
