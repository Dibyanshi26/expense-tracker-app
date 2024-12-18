import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="💰ExpenseTrackerPro💰",
    layout="wide",
    page_icon="💰"
)

# Custom CSS for Source Sans Pro Font
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Source Sans Pro', sans-serif;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Gradient Color Palette
color_palette = ["#FFECB3", "#E85285", "#6A1B9A", "#FFAA00", "#7E57C2", "#FF80AB", "#4FC3F7"]

# Default Data File
DEFAULT_DATA_FILE = "expenses.csv"

# Load CSV Data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # Ensures consistent datetime
    return df

# Sidebar - Upload Custom File
st.sidebar.header("📤 Upload Expense File")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    df = load_data(uploaded_file)  # Use uploaded file
    st.sidebar.success("✅ File Uploaded Successfully!")
else:
    df = load_data(DEFAULT_DATA_FILE)  # Use default file

# Sidebar Filters and Options
st.sidebar.header("📊 Filters & Additions")
date_range = st.sidebar.date_input("Filter by Date Range", [df["Date"].min().date(), df["Date"].max().date()])
subcategory = st.sidebar.selectbox("Select Subcategory", ["All"] + sorted(df["Subcategory"].unique()))
payment_method = st.sidebar.selectbox("Select Payment Method", ["All"] + sorted(df["Payment Method"].unique()))

# Filter Data
filtered_df = df[
    (df["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))) &
    (df["Subcategory"] == subcategory if subcategory != "All" else True) &
    (df["Payment Method"] == payment_method if payment_method != "All" else True)
]

# Main Title
st.markdown("<h1 style='text-align: center; color: #6A1B9A;'>💰 ExpenseTrackerPro 💰</h1>", unsafe_allow_html=True)

# Display Filtered Data
st.subheader("📋 Filtered Expense Records")
st.dataframe(filtered_df, use_container_width=True)

# Charts
col1, col2 = st.columns(2)

# 1. Bar Chart - Expense Distribution by Category
with col1:
    st.subheader("📊 Expense Distribution by Category")
    fig_bar = px.bar(filtered_df, x="Category", y="Amount", color="Category", 
                     title="Expenses by Category",
                     color_discrete_sequence=color_palette,
                     text="Amount")
    fig_bar.update_layout(plot_bgcolor="#1E1E2E", paper_bgcolor="#1E1E2E", font_color="white")
    st.plotly_chart(fig_bar, use_container_width=True)

# 2. Donut Chart - Expense Breakdown
with col2:
    st.subheader("🍩 Expense Breakdown")
    fig_pie = px.pie(filtered_df, names="Category", values="Amount", hole=0.5,
                     title="Expense Breakdown", color_discrete_sequence=color_palette)
    fig_pie.update_layout(plot_bgcolor="#1E1E2E", paper_bgcolor="#1E1E2E", font_color="white")
    st.plotly_chart(fig_pie, use_container_width=True)

# 3. Treemap - Subcategory Spend
st.subheader("🌳 Subcategory Spend Breakdown")
fig_tree = px.treemap(filtered_df, path=["Category", "Subcategory"], values="Amount", 
                      title="Subcategory Spend Breakdown", color="Amount",
                      color_continuous_scale=color_palette)
fig_tree.update_layout(margin=dict(t=50, l=25, r=25, b=25), font_color="white", 
                       plot_bgcolor="#1E1E2E", paper_bgcolor="#1E1E2E")
st.plotly_chart(fig_tree, use_container_width=True)

# 4. Line Chart - Expense Trends Over Time
st.subheader("📈 Expense Trends Over Time")
fig_line = px.line(filtered_df.sort_values(by="Date"), x="Date", y="Amount", title="Expense Trends",
                   markers=True, color_discrete_sequence=["#FF80AB"])
fig_line.update_layout(plot_bgcolor="#1E1E2E", paper_bgcolor="#1E1E2E", font_color="white")
st.plotly_chart(fig_line, use_container_width=True)

# 5. Horizontal Bar Chart - Payment Method Comparison
st.subheader("💳 Payment Method Comparison")
fig_barh = px.bar(filtered_df, y="Payment Method", x="Amount", color="Payment Method", 
                  orientation="h", text="Amount", color_discrete_sequence=color_palette)
fig_barh.update_layout(plot_bgcolor="#1E1E2E", paper_bgcolor="#1E1E2E", font_color="white")
st.plotly_chart(fig_barh, use_container_width=True)

# Key Statistics
st.subheader("📊 Key Statistics")
total_expense = filtered_df["Amount"].sum()
avg_expense = filtered_df["Amount"].mean()
highest_expense = filtered_df.loc[filtered_df["Amount"].idxmax()] if not filtered_df.empty else None

col1, col2, col3 = st.columns(3)
col1.metric("Total Expenses", f"${total_expense:,.2f}")
col2.metric("Average Expense", f"${avg_expense:,.2f}")
col3.metric("Highest Expense", f"${highest_expense['Amount']:,.2f}" if highest_expense is not None else "-", 
            f"Category: {highest_expense['Category']}" if highest_expense is not None else "-")

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF80AB;'>✨ Designed with ❤️ using Streamlit, by Dibyanshi Singh ✨</p>", unsafe_allow_html=True)
