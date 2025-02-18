import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

# Set page to full-screen layout
st.set_page_config(layout="wide")

# Function to get email based on user_id
def get_email_by_user_id(user_id, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM links WHERE link LIKE %s", (f"%{user_id}%",))
    email = cursor.fetchone()
    cursor.close()
    return email[0] if email else None

# Function to insert data into MySQL table
def insert_data(user_id, site_number, comp_price):
    conn = mysql.connector.connect(
        host="gcbdallas.caqfykoqtrvk.us-east-1.rds.amazonaws.com",
        user="Dallas_2024",
        password="GCBDallas$223",
        database="VerizonClientMarketing"
    )
    email = get_email_by_user_id(user_id, conn)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientInputs (email, siteNumber, compPrice) VALUES (%s, %s, %s)", 
                   (email if email else None, site_number, comp_price))
    conn.commit()
    conn.close()

# Static GCB Quote
GCB_QUOTE = 5500  # Static value email = get_email_by_user_id(user_id, conn)

st.title("Verizon Budget Calculator")

# User Inputs in Yellow Highlighted Table (Table 1)
st.subheader("Enter Input Values")
# Extract `user_id` from the URL (e.g., ?user_id=1234abcd)
url_params = st.query_params()
user_id = url_params.get("user_id", [None])[0]
new_build = st.number_input("No.Of Sites", min_value=1, step=1, value=150)
competitor_pricing = st.number_input("Competitor Pricing ($)", min_value=1, step=1, value=10000)
st.write(user_id)
if st.button("Get Quote") or new_build or competitor_pricing:
    insert_data(user_id, new_build, competitor_pricing)

# Layout for side-by-side tables and graphs
col1, col2 = st.columns([1, 1])

with col1:
    # Display Table 1
    st.subheader("Table 1: Verizon Budget per Site")
    table1 = {
        "Market": ["Market 1"],
        "No. Of Sites": [new_build],
        "Competitor Pricing ($)": [competitor_pricing],
        "GCB Quote ($)": [GCB_QUOTE]
    }
    df_table1 = pd.DataFrame(table1)
    st.table(df_table1)

    # Calculations (Table 2)
    competitor_budget = new_build * competitor_pricing
    gcb_budget = new_build * GCB_QUOTE
    budget_saved = competitor_budget - gcb_budget
    percent_savings = round((budget_saved / competitor_budget) * 100, 2) if competitor_budget != 0 else 0

    # Display Results in Table 2
    st.subheader("Verizon Total Budget & Savings")
    data = {
        "Market": ["Market 1"],
        "Competitor Budget ($)": [competitor_budget],
        "GCB Budget ($)": [gcb_budget],
        "Budget Saved ($)": [budget_saved],
        "% Savings": [f"{percent_savings:.2f}%"]
    }
    df = pd.DataFrame(data)
    st.table(df)

    # Future Site Funding Calculation
    future_sites_funded = int(budget_saved / GCB_QUOTE) if GCB_QUOTE != 0 else 0

    # Display Table 3
    st.subheader("Future Site Count Funded by GCB Savings")
    table3 = {
        "Market": ["Market 1"],
        "Future Site Count Funded": [future_sites_funded],
        "% Savings on Buildout Cost": [f"{percent_savings:.2f}%"]
    }
    df_table3 = pd.DataFrame(table3)
    st.table(df_table3)

with col2:
    # Visualization
    st.subheader("Budget Comparison and Future Site Count")
    fig, axs = plt.subplots(1, 2, figsize=(16, 7))  # Increased figure size

    # Budget Comparison
    labels = ["Competitor Budget", "GCB Budget", "Budget Saved"]
    values = [competitor_budget, gcb_budget, budget_saved]
    axs[0].bar(labels, values, color=["#1f77b4", "#ff7f0e", "#2ca02c"], width=0.5)
    axs[0].set_ylabel("Amount ($)")
    axs[0].set_title("Verizon Budget: GCB vs Competitor")
    for i, v in enumerate(values):
        axs[0].text(i, v + 20000, f"${v:,}", ha='center', fontsize=12, fontweight='bold')

    # Future Site Count Funded
    labels2 = ["Future Sites Funded", "% Savings"]
    values2 = [future_sites_funded, percent_savings]
    axs[1].bar(labels2, values2, color=["#1f77b4", "#ff7f0e"], width=0.5)
    axs[1].set_ylabel("Count / Percentage")
    axs[1].set_title("Future Site Count Funded by GCB Savings")
    for i, v in enumerate(values2):
        axs[1].text(i, v + 2, f"{v:.2f}%" if i == 1 else f"{v}", ha='center', fontsize=12, fontweight='bold')

    st.pyplot(fig)
