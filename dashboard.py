import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('visits_data.csv')
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    return data

data = load_data()

# Title of the dashboard
st.title('Business Metrics')

# Sidebar for filters
st.sidebar.header('Filter Options')
selected_offerings = st.sidebar.multiselect('Select Offerings', options=data['Offering'].unique(), default=data['Offering'].unique())
selected_locations = st.sidebar.multiselect('Select Locations', options=data['Location'].unique(), default=data['Location'].unique())
selected_business_units = st.sidebar.multiselect('Select Business Unit', options=data['Business_Unit'].unique(), default=data['Business_Unit'].unique())

# Filtered data by offering and location
filtered_data = data[(data['Offering'].isin(selected_offerings)) & (data['Location'].isin(selected_locations)) & (data['Business_Unit'].isin(selected_business_units))]

# Calculate and display WAU and Retention
def calculate_metrics(data):
    # Calculate WAU
    latest_week = data['Timestamp'].max().normalize() - pd.DateOffset(days=data['Timestamp'].max().weekday())
    current_wau = data[(data['Timestamp'] >= latest_week) & (data['Timestamp'] < latest_week + pd.DateOffset(days=7))]['User_ID'].nunique()
    previous_week = latest_week - pd.DateOffset(days=7)
    previous_wau = data[(data['Timestamp'] >= previous_week) & (data['Timestamp'] < previous_week + pd.DateOffset(days=7))]['User_ID'].nunique()
    delta_wau = current_wau - previous_wau

    # Calculate Retention
    current_users = set(data[(data['Timestamp'] >= latest_week) & (data['Timestamp'] < latest_week + pd.DateOffset(days=7))]['User_ID'])
    previous_users = set(data[(data['Timestamp'] >= previous_week) & (data['Timestamp'] < latest_week)]['User_ID'])
    retained_users = current_users.intersection(previous_users)
    if previous_users:
        retention_rate = len(retained_users) / len(previous_users) * 100
    else:
        retention_rate = 0
    
    return current_wau, delta_wau, retention_rate

current_wau, delta_wau, retention_rate = calculate_metrics(filtered_data)

# Display the current WAU and Retention with enhanced styling
st.markdown(f"""
<div style="background-color: #f1f1f1; border-radius: 10px; padding: 10px; margin: 10px 0;">
    <h2 style="text-align: center; color: #4CAF50;">Weekly Active Users</h2>
    <h1 style="text-align: center; color: #4CAF50;">{current_wau}</h1>
    <p style="text-align: center;">Change from previous week: <b style="color: {'green' if delta_wau >= 0 else 'red'};">{delta_wau}</b></p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background-color: #f1f1f1; border-radius: 10px; padding: 10px; margin: 10px 0;">
    <h2 style="text-align: center; color: #4CAF50;">Weekly Retention Rate</h2>
    <h1 style="text-align: center; color: #4CAF50;">{retention_rate:.2f}%</h1>
</div>
""", unsafe_allow_html=True)


# Plot Weekly Active Users (WAU) using the exact timestamps
st.header("Weekly Active Users (WAU) Over Time")
wau_data = filtered_data.groupby([pd.Grouper(key='Timestamp', freq='W'), 'Offering'])['User_ID'].nunique().unstack().fillna(0)
fig, ax = plt.subplots()
wau_data.plot(kind='bar', stacked=True, ax=ax)
ax.axhline(10000, color='red', linestyle='--', label='10k users target')
plt.xticks(rotation=45)
plt.ylabel('Active Users')
plt.legend(title='Offering')
plt.tight_layout()
st.pyplot(fig)

def calculate_weekly_retention(data):
    data['Week'] = data['Timestamp'].dt.to_period('W')
    users_per_week = data.groupby(['Week', 'User_ID']).size().reset_index().rename(columns={0: 'Interactions'})
    all_weeks = users_per_week['Week'].sort_values().unique()
    retention_rates = []
    weeks_formatted = []

    for i in range(len(all_weeks)-1):
        prev_week_users = set(users_per_week[users_per_week['Week'] == all_weeks[i]]['User_ID'])
        current_week_users = set(users_per_week[users_per_week['Week'] == all_weeks[i + 1]]['User_ID'])
        retained_users = prev_week_users.intersection(current_week_users)
        if prev_week_users:
            retention_rate = len(retained_users) / len(prev_week_users) * 100
        else:
            retention_rate = 0
        retention_rates.append(retention_rate)
        weeks_formatted.append(all_weeks[i].start_time)  # Convert Period to datetime for plotting

    return weeks_formatted, retention_rates

# Calculate retention rates
weeks, retention_rates = calculate_weekly_retention(filtered_data)

# Plot retention rates over time
st.header("User Retention Rate Over Time")
fig, ax = plt.subplots()
ax.plot(weeks, retention_rates, marker='o', linestyle='-')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)
plt.xlabel('Week')
plt.ylabel('Retention Rate (%)')
plt.title('Weekly Retention Rates')
plt.grid(True)
plt.tight_layout()
st.pyplot(fig)