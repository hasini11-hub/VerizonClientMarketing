import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
import requests
import io
from PIL import Image

# Set page to full-screen layout
st.set_page_config(layout="wide")

# Function to get email based on user_id
def get_email_by_user_id(user_id):
    conn = mysql.connector.connect(
        host="gcbdallas.caqfykoqtrvk.us-east-1.rds.amazonaws.com",
        user="Dallas_2024",
        password="GCBDallas$223",
        database="VerizonClientMarketing"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM links WHERE link LIKE %s", (f"%{user_id}%",))
    email = cursor.fetchone()
    cursor.close()
    return email[0] if email else None

def get_user_ip():
    """Fetch the public IP of the user"""
    try:
        ip = requests.get("https://api64.ipify.org?format=json").json()["ip"]
        return ip
    except:
        return "Unknown"
    
# Function to insert data into MySQL table
def insert_data(user_id, site_number, comp_price):
    conn = mysql.connector.connect(
        host="gcbdallas.caqfykoqtrvk.us-east-1.rds.amazonaws.com",
        user="Dallas_2024",
        password="GCBDallas$223",
        database="VerizonClientMarketing"
    )
    
    cursor = conn.cursor()
    user_ip = get_user_ip()
    cursor.execute("INSERT INTO clientInputs (email, siteNumber, compPrice, clientIP) VALUES (%s, %s, %s, %s)", 
                   (email if email else "cantgetemail", site_number, comp_price, user_ip))
    conn.commit()
    conn.close()




# Static GCB Quote
GCB_QUOTE = 5500

#st.title("Budget Calculator")

# Custom CSS to reduce input box width
st.markdown(
    """
    <style>
    div[data-baseweb="input"] {
        width: 80% !important; 
        margin-bottom: 5px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Layout: Inputs on left, Tables and Charts on right
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.subheader("Calculate savings")

    new_build = st.number_input(
        "No. of Sites", min_value=1, step=1, value=150, format="%d"
    )

    competitor_pricing = st.number_input(
        "Competitor Pricing ($)", min_value=1, step=1, value=10000, format="%d"
    )

    # Extract `user_id` from the URL (e.g., ?user_id=1234abcd)
    user_id = st.query_params.get_all("session_id")
    try:
        email = get_email_by_user_id(user_id[0])
    except Exception:
        email = "Not found"
    if new_build or competitor_pricing:
        insert_data(user_id, new_build, competitor_pricing)

    # Budget Calculations
    competitor_budget = new_build * competitor_pricing
    gcb_budget = new_build * GCB_QUOTE
    budget_saved = competitor_budget - gcb_budget
    percent_savings = round((budget_saved / competitor_budget) * 100, 2) if competitor_budget != 0 else 0
    future_sites_funded = int(budget_saved / GCB_QUOTE) if GCB_QUOTE != 0 else 0

# Right section: Data Tables and Charts
with col_right:
    st.subheader("Budget Summary")

    df_table1 = pd.DataFrame({
        "No. of Sites": [new_build],
        "Competitor Pricing ($)": [f"${competitor_pricing:,.0f}"],
        "GCB Quote ($)": [f"${GCB_QUOTE:,.0f}"]
    })
    
    st.markdown(df_table1.to_html(index=False, escape=False), unsafe_allow_html=True)

   # Define function to highlight "Budget Saved" and "% Savings" columns
    def highlight_green(val):
        return "background-color: #56e356; font-weight: bold;" if "$" in str(val) or "%" in str(val) else ""

    df_table2 = pd.DataFrame({
        "Competitor Budget ($)": [f"${competitor_budget:,.0f}"],
        "GCB Budget ($)": [f"${gcb_budget:,.0f}"],
        "Budget Saved ($)": [f"${budget_saved:,.0f}"],
        "% Savings": [f"{percent_savings:.2f}%"]
    })

    # Apply styling
    df_table2_styled = df_table2.style.map(highlight_green, subset=["Budget Saved ($)", "% Savings"]).hide(axis="index")

    # Display the styled DataFrame in Streamlit
    st.markdown(df_table2_styled.to_html(index=False, escape=False), unsafe_allow_html=True)


    df_table3 = pd.DataFrame({
        "Future Site Count Funded": [future_sites_funded],
        "% Savings on Buildout Cost": [f"{percent_savings:.2f}%"]
    })
    
    st.markdown(df_table3.to_html(index=False, escape=False), unsafe_allow_html=True)

# Align Charts Side by Side
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig1, ax1 = plt.subplots(figsize=(6, 3))  # Reduced graph size
    labels = ["Competitor Budget", "GCB Budget", "Budget Saved"]
    values = [competitor_budget, gcb_budget, budget_saved]
    
    bars = ax1.bar(labels, values, color=["#1f77b4", "#ff7f0e", "#2ca02c"], width=0.5)
    ax1.set_ylabel("Amount ($)")
    ax1.set_title("Budget Comparison", fontsize=9)

    # Add labels inside the bars
    for bar, value in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() - (bar.get_height()*0.15),
                 f"${value:,.0f}", ha='center', fontsize=7, fontweight='bold', color='white', va='top')

    st.pyplot(fig1)

with col_chart2:
    fig2, ax2_left = plt.subplots(figsize=(6, 3.4))  # Compact graph size
    
    # Primary Y-axis (Left) for % Savings
    ax2_right = ax2_left.twinx()  # Secondary Y-axis (Right) for Future Sites Funded

    labels = ["% Savings", "Future Sites Funded"]
    values_left = [percent_savings, 0]  # % Savings on the left Y-axis
    values_right = [0, future_sites_funded]  # Future Sites Funded on the right Y-axis

    # Bars for left Y-axis (% Savings)
    bars_left = ax2_left.bar(labels, values_left, color="#ff7f0e", width=0.5, label="% Savings")

    # Bars for right Y-axis (Future Sites Funded)
    bars_right = ax2_right.bar(labels, values_right, color="#1f77b4", width=0.5, alpha=0.7, label="Future Sites Funded")

    # Labels and Titles
    ax2_left.set_ylabel("% Savings", color="#ff7f0e", fontsize=9)
    ax2_right.set_ylabel("Future Sites Funded (Count)", color="#1f77b4", fontsize=9)
    ax2_left.set_title("Future Sites Funded & % Savings", fontsize=9)

    # Add labels inside the bars
    for bar, value in zip(bars_left, values_left):
        if value > 0:
            ax2_left.text(bar.get_x() + bar.get_width()/2, 
                          bar.get_height() - (bar.get_height() * 0.15),
                          f"{value:.2f}%", ha='center', fontsize=7, fontweight='bold', color='white', va='top')

    for bar, value in zip(bars_right, values_right):
        if value > 0:
            ax2_right.text(bar.get_x() + bar.get_width()/2, 
                           bar.get_height() - (bar.get_height() * 0.15),
                           f"{value:,}", ha='center', fontsize=7, fontweight='bold', color='white', va='top')

    # Ensure Y-axes are aligned properly
    ax2_left.set_ylim(0, max(percent_savings + 10, 100))  # Add buffer for visibility
    ax2_right.set_ylim(0, max(future_sites_funded + 10, future_sites_funded * 1.2))

    st.pyplot(fig2)

# Footer
st.markdown(
    """
    <hr style="margin-top: 30px;">
    <p style="text-align: center; font-size: 15px; font-weight: bold;">
        GCB Services L.L.C. CONFIDENTIAL and PROPRIETARY
    </p>
    """, 
    unsafe_allow_html=True
)
