import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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

