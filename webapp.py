import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
import requests
import io
from PIL import Image

# Set page to full-screen layout
st.set_page_config(layout="wide")
# Add logo to the top-left corner

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
def insert_data(email, site_number, comp_price):
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

# Layout: Inputs on left, Tables in the middle, and Logo on the right
col_left, col_middle, col_right = st.columns([1, 2, 1])

with col_left:
    st.subheader("Calculate Savings")

    new_build = st.number_input(
        "No. of Sites", min_value=1, step=1, value=150, format="%d"
    )

    competitor_pricing = st.number_input(
        "Competitor Pricing ($)", min_value=1, step=1, value=10000, format="%d"
    )

    user_id = st.query_params.get_all("session_id")
    if user_id:
        try:
            email = get_email_by_user_id(user_id[0])
        except Exception:
            email = "Not found"
    else:
        email = "No user ID found"

    if new_build or competitor_pricing:
        insert_data(email, new_build, competitor_pricing)

    # Budget Calculations
    competitor_budget = new_build * competitor_pricing
    gcb_budget = new_build * GCB_QUOTE
    budget_saved = competitor_budget - gcb_budget
    percent_savings = round((budget_saved / competitor_budget) * 100, 2) if competitor_budget != 0 else 0
    future_sites_funded = int(budget_saved / GCB_QUOTE) if GCB_QUOTE != 0 else 0

# Middle column: Data Tables and Charts
with col_middle:
    st.subheader("Budget Summary")

    # Custom CSS for increasing table size
    st.markdown(
        """
        <style>
        .custom-table {
            width: 140% !important;  /* Increase width by 40% */
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Table 1: Basic Site & Pricing Info
    df_table1 = pd.DataFrame({
        "No. of Sites": [new_build],
        "Competitor Pricing ($)": [f"${competitor_pricing:,.0f}"],
        "GCB Quote ($)": [f"${GCB_QUOTE:,.0f}"]
    })

    st.markdown(f'<div class="custom-table">{df_table1.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)

    # Define function to highlight "Budget Saved" and "% Savings" columns with increased font size
    def highlight_green(val):
        return "background-color: #56e356; font-weight: bold; font-size: 110%;" if "$" in str(val) or "%" in str(val) else ""

    # Table 2: Budget Comparisons
    df_table2 = pd.DataFrame({
        "Competitor Budget ($)": [f"${competitor_budget:,.0f}"],
        "GCB Budget ($)": [f"${gcb_budget:,.0f}"],
        "Budget Saved ($)": [f"${budget_saved:,.0f}"],
        "% Savings": [f"{percent_savings:.0f}%"]
    })

    # Apply styling
    df_table2_styled = df_table2.style.map(highlight_green, subset=["Budget Saved ($)", "% Savings"]).hide(axis="index")

    # Display the styled DataFrame in Streamlit with increased width
    st.markdown(f'<div class="custom-table">{df_table2_styled.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)

    # Table 3: Future Site Funding
    df_table3 = pd.DataFrame({
        "Future Site Count Funded": [future_sites_funded],
        "% Savings on Buildout Cost": [f"{percent_savings:.0f}%"]
    })

    st.markdown(f'<div class="custom-table">{df_table3.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)

# Right column: Display the Logo
with col_right:
    # Adjust the size of the logo and position it to the right
    st.image("logo.png", width=150)  # Adjust width as needed

# Align Charts Side by Side
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig1, ax1 = plt.subplots(figsize=(6, 3))  # Reduced graph size
    labels = ["Competitor Budget", "GCB Budget", "Budget Saved"]
    values = [competitor_budget, gcb_budget, budget_saved]
    
    bars = ax1.bar(labels, values, color=["#1f77b4", "#ff7f0e", "#2ca02c"], width=0.5)
    ax1.set_ylabel("Amount ($)", fontsize=9)  # Set font size for the y-axis label
    ax1.set_title("Budget Comparison", fontsize=14, color="#f5f5f5", pad=20)  # Title color and padding
    
    # Set background color for the title
    ax1.title.set_backgroundcolor("#ff7f0e")  # Background color for the title
    ax1.title.set_position([0.5, 1.05])  # Adjust title position to prevent overlap

    # Add labels inside the bars
    for bar, value in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() - (bar.get_height()*0.15),
                 f"${value:,.0f}", ha='center', fontsize=7, fontweight='bold', color='white', va='top')

    # Remove the offset text from the y-axis (e.g., 1e6)
    ax1.yaxis.offsetText.set_visible(False)

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
    ax2_left.set_title("Future Sites Funded & % Savings", fontsize=14, color="#f5f5f5", pad=20)  # Title color and padding

    # Set background color for the title
    ax2_left.title.set_backgroundcolor("#ff7f0e")  # Background color for the title
    ax2_left.title.set_position([0.5, 1.05])  # Adjust title position to prevent overlap

    # Add labels inside the bars
    for bar, value in zip(bars_left, values_left):
        if value > 0:
            ax2_left.text(bar.get_x() + bar.get_width()/2, 
                          bar.get_height() - (bar.get_height() * 0.15),
                          f"{value:.0f}%", ha='center', fontsize=8, fontweight='bold', color='white', va='top')

    for bar, value in zip(bars_right, values_right):
        if value > 0:
            ax2_right.text(bar.get_x() + bar.get_width()/2, 
                           bar.get_height() - (bar.get_height() * 0.15),
                           f"{value:,}", ha='center', fontsize=8, fontweight='bold', color='white', va='top')

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
