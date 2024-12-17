import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Enhanced Expenses Tracker", layout="wide", page_icon="💰", initial_sidebar_state="expanded")

# Theme Toggle
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

def set_theme():
    st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"

# Theme Colors
theme_colors = {
    "light": {"bg": "#F7F7F7", "header": "#4682B4", "text": "#333333", "button": "#5F9EA0"},
    "dark": {"bg": "#2F021B", "header": "#8D0650", "text": "#EAD3CB", "button": "#5E0435"}
}
colors = theme_colors[st.session_state["theme"]]

# Apply Theme
st.markdown(f"""
    <style>
        body {{ background-color: {colors['bg']}; color: {colors['text']}; }}
        .header {{ text-align: center; font-size: 32px; color: {colors['header']}; font-weight: bold; }}
        .stButton>button {{ background-color: {colors['button']}; color: white; border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)
st.sidebar.button("Toggle Light/Dark Mode", on_click=set_theme)

# Load Data
DATA_FILE = "expenses.csv"
try:
    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
except FileNotFoundError:
    st.error("Expenses file not found! Please upload your CSV file.")
    st.stop()

# Sidebar Filters
st.sidebar.header("📤 Filters & Additions")
date_range = st.sidebar.date_input("Filter by Date Range", [df["Date"].min(), df["Date"].max()])
subcategory = st.sidebar.multiselect("Select Subcategory", df["Subcategory"].unique())
payment_method = st.sidebar.multiselect("Select Payment Method", df["Payment Method"].unique())

filtered_df = df[(df["Date"].between(*date_range))]
if subcategory:
    filtered_df = filtered_df[filtered_df["Subcategory"].isin(subcategory)]
if payment_method:
    filtered_df = filtered_df[filtered_df["Payment Method"].isin(payment_method)]

# Title
st.markdown(f"<div class='header'>💰 Enhanced Expense Tracker</div>", unsafe_allow_html=True)

# Recorded Expenses Table
st.subheader("📋 Recorded Expenses")
st.dataframe(filtered_df, use_container_width=True)

# Visualization - Stacked Bar Chart
st.subheader("📊 Stacked Bar Chart: Category vs Subcategory")
fig_stacked = px.bar(filtered_df, x="Category", y="Amount", color="Subcategory", title="Expenses by Category and Subcategory")
st.plotly_chart(fig_stacked, use_container_width=True)

# Visualization - Donut Chart
st.subheader("🍩 Donut Chart: Expense Breakdown by Tags")
fig_donut = px.pie(filtered_df, names="Tags", values="Amount", hole=0.4, title="Expense Breakdown by Tags")
st.plotly_chart(fig_donut, use_container_width=True)

# Visualization - Treemap
st.subheader("🌳 Treemap: Expense Breakdown")
fig_treemap = px.treemap(filtered_df, path=["Category", "Subcategory"], values="Amount", title="Expense Breakdown Treemap")
st.plotly_chart(fig_treemap, use_container_width=True)

# Visualization - Area Chart
st.subheader("📈 Area Chart: Spending Trends Over Time")
fig_area = px.area(filtered_df, x="Date", y="Amount", color="Category", title="Spending Trends Over Time")
st.plotly_chart(fig_area, use_container_width=True)

# Visualization - Scatter Plot
st.subheader("🔍 Scatter Plot: Amount vs Payment Method")
fig_scatter = px.scatter(filtered_df, x="Payment Method", y="Amount", color="Category", size="Amount", title="Amount vs Payment Method")
st.plotly_chart(fig_scatter, use_container_width=True)

# Visualization - Heatmap
st.subheader("🔥 Heatmap: Monthly Spending Patterns")
filtered_df["Month"] = filtered_df["Date"].dt.month_name()
filtered_df["Day"] = filtered_df["Date"].dt.day
pivot_table = filtered_df.pivot_table(index="Month", columns="Day", values="Amount", aggfunc="sum", fill_value=0)
fig_heatmap = px.imshow(pivot_table, labels=dict(x="Day", y="Month", color="Amount"), title="Monthly Spending Heatmap")
st.plotly_chart(fig_heatmap, use_container_width=True)

# Key Statistics
st.subheader("📊 Key Statistics")
total_expenses = filtered_df["Amount"].sum()
avg_expense = filtered_df["Amount"].mean()
max_expense_row = filtered_df.loc[filtered_df["Amount"].idxmax()]

col1, col2, col3 = st.columns(3)
col1.metric("Total Expenses", f"${total_expenses:,.2f}")
col2.metric("Average Expense", f"${avg_expense:,.2f}")
col3.metric("Highest Expense", f"${max_expense_row['Amount']:,.2f}", f"Category: {max_expense_row['Category']}")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; font-size: 12px; color: {colors['text']};'>📊 Designed with ❤️ using Streamlit | Enhanced Visuals</div>", unsafe_allow_html=True)
