import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Expenses Tracker", layout="wide", page_icon="💰", initial_sidebar_state="expanded")

# Theme Toggle
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

def set_theme():
    st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"

# Color Palettes for Light and Dark Themes
theme_colors = {
    "light": {
        "bg": "#F7F7F7",
        "header": "#4682B4",
        "text": "#333333",
        "button": "#5F9EA0",
        "chart_bg": "#FFFFFF",
        "chart_colors": px.colors.sequential.Blues
    },
    "dark": {
        "bg": "#2F021B",
        "header": "#8D0650",
        "text": "#EAD3CB",
        "button": "#5E0435",
        "chart_bg": "#D6CADD",
        "chart_colors": ["#8D0650", "#7E0647", "#6E053E", "#5E0435", "#4F042D", "#3F0324"]
    }
}

colors = theme_colors[st.session_state["theme"]]

# Apply Custom Styles Based on Theme
st.markdown(f"""
    <style>
        body {{ background-color: {colors['bg']}; color: {colors['text']}; }}
        .header {{ text-align: center; font-size: 32px; color: {colors['header']}; font-weight: bold; }}
        .stButton>button {{ background-color: {colors['button']}; color: white; border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# Theme Toggle Button
st.sidebar.button("Toggle Light/Dark Mode", on_click=set_theme)

# Data Storage
DATA_FILE = "expenses.csv"

def load_expenses():
    """Load expenses file with robust error handling."""
    try:
        data = pd.read_csv(DATA_FILE)
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        return data.dropna(subset=["Date"])
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

if "expenses" not in st.session_state:
    st.session_state["expenses"] = load_expenses()

# Upload Custom Expense File
st.sidebar.header("📤 Upload Expense File")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    try:
        user_expenses = pd.read_csv(uploaded_file)
        user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")
        user_expenses = user_expenses.dropna(subset=["Date"])  # Ensure valid dates
        st.session_state["expenses"] = user_expenses
        st.sidebar.success("✅ File Uploaded Successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Error loading file: {e}")

# Sidebar Inputs
st.sidebar.header("➕ Add New Expense")
date = st.sidebar.date_input("Date", datetime.today())
category = st.sidebar.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Utilities", "Shopping", "Miscellaneous"])
amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01)
description = st.sidebar.text_input("Description")

if st.sidebar.button("Add Expense"):
    new_expense = {"Date": date, "Category": category, "Amount": amount, "Description": description}
    st.session_state["expenses"] = pd.concat([st.session_state["expenses"], pd.DataFrame([new_expense])], ignore_index=True)
    st.session_state["expenses"].to_csv(DATA_FILE, index=False)
    st.sidebar.success("✅ Expense Added!")
    st.experimental_rerun()

# Main Area
st.markdown(f"<div class='header'>💰 Expense Tracker</div>", unsafe_allow_html=True)

if not st.session_state["expenses"].empty:
    # Date Range Filtering
    start_date, end_date = st.sidebar.date_input("Filter by Date Range", value=(
        st.session_state["expenses"]["Date"].min().date(), st.session_state["expenses"]["Date"].max().date()
    ))
    filtered_expenses = st.session_state["expenses"][
        (st.session_state["expenses"]["Date"].dt.date >= start_date) &
        (st.session_state["expenses"]["Date"].dt.date <= end_date)
    ]

    st.subheader("📋 Recorded Expenses")
    st.dataframe(filtered_expenses, use_container_width=True)

    # Visualization - Bar Chart
    st.subheader("📊 Expense Distribution by Category")
    fig_bar = px.bar(filtered_expenses, x="Category", y="Amount", color="Category", title="Expenses by Category",
                     color_discrete_sequence=colors['chart_colors'])
    fig_bar.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Visualization - Expense Trends Over Time
    st.subheader("📈 Expense Trends Over Time")
    fig_line = px.line(filtered_expenses.sort_values(by="Date"), x="Date", y="Amount",
                       title="Expense Trends Over Time", markers=True,
                       color_discrete_sequence=[colors['header']])
    fig_line.update_layout(paper_bgcolor=colors['chart_bg'], plot_bgcolor=colors['chart_bg'])
    st.plotly_chart(fig_line, use_container_width=True)

    # Summary Stats
    st.subheader("📊 Key Statistics")
    total_expenses = filtered_expenses["Amount"].sum()
    avg_expense = filtered_expenses["Amount"].mean()
    max_expense = filtered_expenses.loc[filtered_expenses["Amount"].idxmax()] if not filtered_expenses.empty else None

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses", f"${total_expenses:,.2f}")
    col2.metric("Average Expense", f"${avg_expense:,.2f}")
    col3.metric("Highest Expense", f"${max_expense['Amount']:,.2f}" if max_expense is not None else "-", 
                f"Category: {max_expense['Category']}" if max_expense is not None else "-")
else:
    st.info("No expenses added yet. Use the sidebar to add new expenses.")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; font-size: 12px; color: {colors['text']};'>📊 Designed with ❤️ using Streamlit | {st.session_state['theme'].capitalize()} Theme</div>", unsafe_allow_html=True)
