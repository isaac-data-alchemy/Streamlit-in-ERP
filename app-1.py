import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Initialize session state to store employees abd shifts data
if 'employees' not in st.session_state:
    st.session_state['employees'] = pd.DataFrame(columns=['Employee ID', 'Name', 'Department', 'Role'])

if 'shifts' not in st.session_state:
    st.session_state['shifts'] = pd.DataFrame(columns=['Shift ID', 'Shift Name', 'Start Time', 'End Time', 'Assigned Employees'])


# Generate mock attendance data
def generate_mock_data(num_records=7):
    """
    Generate mock data for employee attendance records.

Args:
    num_records (int): Number of records to generate (default is 7).

Returns:
    pandas.DataFrame: DataFrame containing generated mock data.
   """
    #np.random.seed(42)
    employees_df = st.session_state.get('employees', pd.DataFrame())
    shifts_df = st.session_state.get('shifts', pd.DataFrame())
    
    if employees_df.empty or shifts_df.empty:
        st.warning("No employees or shifts data available. Using default values.")
        employees_ids = np.random.randint(1000, 1300, num_records)
        departments = np.random.choice(['HR', 'Engineering', 'Sales', 'Marketing'], num_records)
    else:
        employees_ids = np.random.choice(employees_df['Employee ID'], num_records)
        departments = [ 
            employees_df[employees_df['Employee ID'] == emp_id]['Department'].values[0]
            for emp_id in employees_ids
        ]

    data = {
        'Employee ID': employees_ids,
        'Date': [datetime.now().date() - timedelta(days=i % 100) for i in range(num_records)],
        'Check-in Time': np.random.choice(pd.date_range("08:30", "10:30", freq="1T").time, num_records),
        'Check-out Time': np.random.choice(pd.date_range("16:00", "20:00", freq="1T").time, num_records),
        'Department': departments,
        'Attendance Status': np.random.choice(['Present', 'Absent', 'Late'], num_records, p=[0.7, 0.2, 0.1])
    
    }

    # Generate check-in and checkout times based on shifts 
    if not shifts_df.empty:
        check_in_times = []
        check_out_times = []
        for _ in  range(num_records):
            shift = shifts_df.sample(n=1).iloc[0]
            base_check_in = datetime.combine(datetime.today(), shift['Start Time'])
            base_check_out = datetime.combine(datetime.today(), shift['End Time'])

            # Adding some randomness to check-in and checkout times
            check_in = base_check_in + timedelta(minutes=np.random.randint(-30, 30))
            check_out = base_check_out + timedelta(minutes=np.random.randint(-30, 60))

            check_in_times.append(check_in.time())
            check_out_times.append(check_out.time())
    else:
        check_in_times = np.random.choice(pd.date_range("08:30", "10:30", freq='1T').time, num_records)
        check_out_times = np.random.choice(pd.date_range("16:00", "20:00", freq='1T').time, num_records)
    
    data['Check-in Time'] = check_in_times
    data['Check-out Time'] = check_out_times
    return pd.DataFrame(data)

# Function to calculate overtime and lateness
def calculate_overtime_and_lateness(df):
    """
    Calculate lateness and overtime hours for each entry in the DataFrame.

    Parameters:
    - df: pandas DataFrame containing 'Check-in Time' and 'Check-out Time' columns

    The function calculates lateness by comparing 'Check-in Time' with a predefined threshold.
    Overtime hours are calculated by comparing 'Check-out Time' with another threshold.

    The 'Is Late' column is set to True if the 'Check-in Time' is later than the lateness threshold.
    Overtime Hours are calculated as the difference between 'Check-out Time' hour and the overtime threshold hour.
    """
    # Define lateness and overtime thresholds
    lateness_threshold = datetime.strptime("09:00:00", "%H:%M:%S").time()
    overtime_threshold = datetime.strptime("17:00:00", "%H:%M:%S").time()

    # Convert time colymns to datetime.time for comparison
    df['Check-in Time'] = pd.to_datetime(df['Check-in Time'], format="%H:%M:%S").dt.time
    df['Check-out Time'] = pd.to_datetime(df['Check-out Time'], format="%H:%M:%S").dt.time

    # Mark lateness
    df['Is Late'] = df['Check-in Time'] > lateness_threshold

    # Calculate overtime hours (Simplified logic on purpose)
    df['Overtime Hours'] = np.where(
        pd.to_datetime(df['Check-out Time'], format="%H:%M:%S").dt.hour > overtime_threshold.hour,
        (pd.to_datetime(df['Check-out Time'], format="%H:%M:%S").dt.hour - overtime_threshold.hour),0
    )

    return df

# Add Employee Function
def add_employee():
    """
Creates a form to add a new employee with fields for Employee ID, Name, Department, and Role. 
Upon form submission, a new entry is added to the 'employees' DataFrame in the session state. 
Displays a success message upon successful addition of the employee.
"""
    with st.form("add_employee_form"):
        st.subheader("Create New Employee")
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
            st.success(f"Employees {name} added successfully!")



# Add Shifft function
def add_shift():
    """
Creates a form to add a new shift with input fields for Shift ID, Shift Name, Start Time, End Time, and Assigned Employees. 
Upon form submission, the new shift details are added to the 'shifts' DataFrame in the session state. 
A success message is displayed upon successful addition of the shift.
"""
    with st.form("add_shift_form"):
        st.subheader("Add New Shift")
        shift_id = st.text_input("Shift ID")
        shift_name = st.text_input("Shift Name")
        start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
        end_time = st.time_input(" Time", value=datetime.strptime("17:00", "%H:%M").time())
        assigned_employees = st.multiselect("Assign Employees", st.session_state['employees']['Name'].tolist())
        submitted = st.form_submit_button("Add Shift")

        if submitted:
            new_shift = pd.DataFrame([{
                'Shift ID': shift_id,
                'Shift Name': shift_name,
                'Start Time': start_time,
                'End Time': end_time,
                'Assigned Employees': ', '.join(assigned_employees)
            }])
            st.session_state['shifts'] = pd.concat([st.session_state['shifts'], new_shift], ignore_index=True)
            st.success(f"Shift {shift_name} added successfully!")


        

# Main Stream Lit Application
def main():
    """
Displays an interactive dashboard for time and attendance management. 
Allows navigation between different pages such as 'Dashboard', 'Employee Scheduling', and 'Shift Management'. 
Provides filters for date range, department, and employee search. 
Generates metrics, trends, reports, and visualizations based on the filtered data. 
Enables adding new employees and shifts with success messages upon addition. 
Supports downloading attendance data and real-time data refresh.
"""
    # Sidebar for navigation
    st.sidebar.title("Dashboard Navigation")
    pages = st.sidebar.radio("Go to", ['Dashboard', 'Employee Scheduling', 'Shift Management'])

    # Attendance Dashboard
    if pages == 'Dashboard':
        
        # Sidebar
        st.sidebar.title("Filters")
        date_range = st.sidebar.date_input("Select Date Range", [datetime.now().date() - timedelta(365), datetime.now().date()])
        departmemt_filter = st.sidebar.multiselect("Select Department", options=['HR', 'Engineering', 'Sales', 'Marketing'], default=['HR', 'Engineering', 'Sales', 'Marketing'])
        employee_filter = st.sidebar.text_input("Search Employee by ID")

        # Mock data generation
        df = generate_mock_data()
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = calculate_overtime_and_lateness(df)


        # filtering data
        filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <=date_range[1])]
        if 'Department' in filtered_df.columns and departmemt_filter:
            filtered_df = filtered_df[filtered_df['Department'].isin(departmemt_filter)]

        if employee_filter:
            filtered_df = filtered_df[filtered_df['Employee ID'].astype(str).str.contains(employee_filter)]


        

        # Main Dashboard Content
        st.title("Admin Dashboard - Time and Attendance")

        # Metrics
        total_hours_worked = np.random.randint(4000, 5000) # Placeholder values
        absenteesim_rate = round((filtered_df['Attendance Status'] == 'Absent').mean() * 100, 2)
        overtime_hours = filtered_df['Overtime Hours'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Hours Worked", f"{total_hours_worked} hrs")
        col2.metric("Absenteeism Rate", f"{absenteesim_rate} %")
        col3.metric("Overtime Hours", f"{overtime_hours} hrs")

        # Attendance Trends
        attendance_trends = filtered_df.groupby('Date').size().reset_index(name='Attendance Count')
        fig = px.line(attendance_trends, x='Date', y='Attendance Count', title='Attendance Trends Over Time')
        st.plotly_chart(fig, use_container_width=True)

        # Lateness Report
        st.subheader("Lateness Report")
        lateness_df = filtered_df[filtered_df['Is Late']]
        lateness_counts = lateness_df.groupby(['Date', 'Department']).size().reset_index(name='Late Count')
        fig_late = px.bar(lateness_counts, x='Date', y='Late Count', color='Department', title='Lateness by Department Over Time')
        st.plotly_chart(fig_late, use_container_width=True)

        # Individual Records
        st.subheader("Individual Attendance Records")
        st.dataframe(filtered_df)

        # Overtime Reports 
        st.subheader("Overtime Report")
        overtime_df = filtered_df[filtered_df['Overtime Hours'] > 0]
        overtime_summary = overtime_df.groupby(['Employee ID', 'Date']).sum(numeric_only=True).reset_index()
        fig_overtime = px.bar(overtime_summary, x='Date', y='Overtime Hours', color='Employee ID', title='Overtime Hours by Employee')
        st.plotly_chart(fig_overtime, use_container_width=True)
    
    


        # Department-wise Attendance
        st.subheader("Deparment-wise Attendance")
        dept_attendance = filtered_df.groupby('Department').size().reset_index(name='Attendance Count')
        fig_dept = px.bar(dept_attendance, x='Department', y='Attendance Count', color='Department', title='Attendance by Department')
        st.plotly_chart(fig_dept, use_container_width=True)

    
        # Attendance Status Breakdown
        st.subheader("Attendance Status Breakdown")
        status_counts = filtered_df['Attendance Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status = px.pie(status_counts, values='Count', names='Status', title='Attendance Status Distribution')
        st.plotly_chart(fig_status, use_container_width=True)

        # Daily check-in and Check-out Distribution
        st.subheader("Daily Check-in and Check-out Distribution")
        checkin_times = pd.to_datetime(filtered_df['Check-in Time'], format='%H:%M:%S').dt.hour
        checkout_times = pd.to_datetime(filtered_df['Check-out Time'], format='%H:%M:%S').dt.hour
        fig_checkin = go.Figure()
        fig_checkin.add_trace(go.Histogram(x=checkin_times, name='Check-in Times', marker_color='blue', opacity=0.7))
        fig_checkin.add_trace(go.Histogram(x=checkout_times, name='Check-out Times', marker_color='red', opacity=0.7))
        fig_checkin.update_layout(barmode='overlay', title_text='Check-in and Check-out Time Distribution', xaxis_title='Hour of Day', yaxis_title='Frequency')
        st.plotly_chart(fig_checkin, use_container_width=True)


        # Display raw attendance data
        st.header("Attendance Records")
        st.dataframe(filtered_df)

        # Data download option
        st.download_button(
            label="Download Attendance Data",
            data=filtered_df.to_csv(index=False),
            file_name='attendance_data.csv',
            mime='text/csv'
            )

        # Real-time update button
        st.button("Refresh Data")
    
    # Employee Scheduling Page
    elif pages == 'Employee Scheduling':
        st.title("Employee Scheduling")
        st.write("Manage your employee records here.")
        add_employee()
        st.subheader("Current Employees")
        st.dataframe(st.session_state['employees'])


    # Shift Management Page
    elif pages == 'Shift Management':
        st.title("Assign shifts to employees")
        st.write("Manage shifts and assign them to employees")
        add_shift()
        st.subheader("Current Shifts")
        st.dataframe(st.session_state['shifts'])



if __name__ == "__main__":
    main()