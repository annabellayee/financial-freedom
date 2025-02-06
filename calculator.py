import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import io
from datetime import datetime

# Add custom CSS to center all elements
st.markdown(
    """
    <style>
    /* Center the main content */
    .main {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* Center the titles */
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
    
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to calculate mortgage schedule
def calculate_mortgage_schedule(current_year, mortgage_owing, fortnightly_payment, annual_lump_sum, interest_rate):
    schedule = []
    year = 0
    actual_year = current_year
    while mortgage_owing > 0:
        year += 1
        actual_year += 1
        interest_paid = 0
        principal_paid = 0
        
        # Fortnightly payments for the year
        for _ in range(26):  # 26 fortnights in a year
            interest = mortgage_owing * (interest_rate / 100 / 26)
            principal = min(fortnightly_payment - interest, mortgage_owing)
            mortgage_owing -= principal
            interest_paid += interest
            principal_paid += principal
            if mortgage_owing <= 0:
                break
        
        # Annual lump sum
        if mortgage_owing > 0:
            lump_sum = min(annual_lump_sum, mortgage_owing)
            mortgage_owing -= lump_sum
            principal_paid += lump_sum
        
        schedule.append({
            "Year": year,
            "Actual Year": str(actual_year),  
            "Interest Paid": round(interest_paid, 0),
            "Principal Paid": round(principal_paid, 0),
            "Mortgage Balance": round(max(0, mortgage_owing), 0)
        })
    
    return pd.DataFrame(schedule)

# Streamlit app
st.title("Mortgage Calculator")

# Sidebar for user inputs
current_year = datetime.now().year
st.sidebar.header("Input Parameters")
current_year = st.sidebar.number_input("Current Year", value=current_year, step=1)
mortgage_owing = st.sidebar.number_input("Mortgage Owing ($)", value=300000.0, step=10000.0)
fortnightly_payment = st.sidebar.number_input("Fortnightly Payment ($)", value=2000.0, step=100.0)
annual_lump_sum = st.sidebar.number_input("Annual Lump Sum Payment ($)", value=10000.0, step=1000.0)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=5.0, step=0.1)

# Calculate the schedule
schedule = calculate_mortgage_schedule(
    current_year=current_year,
    mortgage_owing=mortgage_owing,
    fortnightly_payment=fortnightly_payment,
    annual_lump_sum=annual_lump_sum,
    interest_rate=interest_rate
)

# Create a CSV file for download
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False)

csv = convert_df_to_csv(schedule)

# Sidebar download button
st.sidebar.download_button(
    label="Download CSV",
    data=csv,
    file_name='mortgage_schedule.csv',
    mime='text/csv'
)


# Display results
st.header("Mortgage Repayment Schedule")
n_rows = len(schedule) #define n_rows so i can use magic formula below for perfect height of df
st.dataframe(schedule, hide_index=True, height = int(35.2*(n_rows+1)), use_container_width=True)  # Display the table

# Plot graph with two y-axes
fig = go.Figure()

# Mortgage Balance on primary y-axis
fig.add_trace(go.Scatter(
    x=schedule["Year"], 
    y=schedule["Mortgage Balance"], 
    mode='lines+markers', 
    name="Mortgage Balance"
))

# Principal Paid and Interest Paid on secondary y-axis
fig.add_trace(go.Bar(
    x=schedule["Year"], 
    y=schedule["Principal Paid"], 
    name="Principal Paid", 
    opacity=0.6
))
fig.add_trace(go.Bar(
    x=schedule["Year"], 
    y=schedule["Interest Paid"], 
    name="Interest Paid", 
    opacity=0.6
))

# Update layout to include secondary y-axis
fig.update_layout(
    title="Mortgage Repayment Over Time",
    xaxis=dict(title="Year"),
    yaxis=dict(
        title="Mortgage Balance ($)",
        titlefont=dict(color="blue"),
        tickfont=dict(color="blue")
    ),
    yaxis2=dict(
        title="Principal/Interest Paid ($)",
        titlefont=dict(color="red"),
        tickfont=dict(color="red"),
        overlaying="y",    # overlay this y-axis with the primary y-axis
        side="right",
        anchor="x"
    ),
    legend=dict(x=0.5, y=1.2, orientation="h"),
    barmode="stack"
)

st.plotly_chart(fig)