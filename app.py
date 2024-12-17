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
        "chart_colors": px.colors.sequential.Blues,
        "axis_text": "#000000"
    },
    "dark": {
        "bg": "#2F021B",
        "header": "#8D0650",
        "text": "#EAD3CB",
        "button": "#5E0435",
        "chart_bg": "#D6CADD",
        "chart_colors": ["#8D0650", "#7E0647", "#6E053E", "#5E0435", "#4F042D", "#3F0324"],
        "axis_text": "#000000"
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
if "expenses" not in st.session_state:
    try:
        st.session_state["expenses"] = pd.read_csv(DATA_FILE)
        st.session_state["expenses"]["Date"] = pd.to_datetime(
            st.session_state["expenses"]["Date"], format="%Y-%m-%d", errors="coerce"
        )
    except FileNotFoundError:
        st.session_state["expenses"] = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

# Upload Custom Expense File
st.sidebar.header("📤 Upload Expense File")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    user_expenses = pd.read_csv(uploaded_file)
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], format="%Y-%m-%d", errors="coerce")
    st.session_state["expenses"] = user_expenses
    st.sidebar.success("✅ File Uploaded Successfully!")

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
    # Handle empty or invalid dates
    valid_dates = st.session_state["expenses"]["Date"].dropna()
    if valid_dates.empty:
        start_date, end_date = datetime.today(), datetime.today()
    else:
        start_date, end_date = valid_dates.min().date(), valid_dates.max().date()

    # Date Range Filtering
    date_range = st.sidebar.date_input("Filter by Date Range", value=(start_date, end_date))
    filtered_expenses = st.session_state["expenses"][
        (st.session_state["expenses"]["Date"].dt.date >= date_range[0]) &
        (st.session_state["expenses"]["Date"].dt.date <= date_range[1])
    ]

    st.subheader("📋 Recorded Expenses")
    st.dataframe(filtered_expenses, use_container_width=True)

    # Visualization - Bar Chart
    st.subheader("📊 Expense Distribution by Category")
    fig_bar = px.bar(filtered_expenses, x="Category", y="Amount", color="Category", title="Expenses by Category",
                     color_discrete_sequence=colors['chart_colors'])
    fig_bar.update_layout(
        xaxis=dict(showgrid=False, title_font=dict(color=colors['axis_text']), tickfont=dict(color=colors['axis_text'])),
        yaxis=dict(showgrid=False, title_font=dict(color=colors['axis_text']), tickfont=dict(color=colors['axis_text'])),
        legend=dict(font=dict(color=colors['axis_text'])),
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Visualization - Expense Trends Over Time
    st.subheader("📈 Expense Trends Over Time")
    expenses_sorted = filtered_expenses.sort_values(by="Date")
    fig_line = px.line(expenses_sorted, x="Date", y="Amount", title="Expense Trends Over Time",
                       markers=True, color_discrete_sequence=[colors['header']])
    fig_line.update_layout(
        xaxis=dict(title_font=dict(color=colors['axis_text']), tickfont=dict(color=colors['axis_text'])),
        yaxis=dict(title_font=dict(color=colors['axis_text']), tickfont=dict(color=colors['axis_text'])),
        legend=dict(font=dict(color=colors['axis_text'])),
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg']
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No expenses added yet. Use the sidebar to add new expenses.")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; font-size: 12px; color: {colors['text']};'>📊 Designed with ❤️ using Streamlit | {st.session_state['theme'].capitalize()} Theme</div>", unsafe_allow_html=True)
