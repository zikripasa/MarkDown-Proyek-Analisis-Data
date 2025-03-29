import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data from the CSV file
@st.cache_data
def load_data():
    df = pd.read_csv("all_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'], errors='coerce')
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'], errors='coerce')
    df['payment_value'] = pd.to_numeric(df['payment_value'], errors='coerce')
    df['payment_type'] = df['payment_type'].astype(str)
    
    return df

# ==========================
# ORDER DISTRIBUTION MODULE
# ==========================
def filter_data(df, start_date, end_date, order_status):
    filtered_df = df[
        (df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
        (df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
    ]
    if order_status != "All":
        filtered_df = filtered_df[filtered_df['order_status'] == order_status]
    return filtered_df

def plot_order_distribution(filtered_df):
    filtered_df['date'] = filtered_df['order_purchase_timestamp'].dt.date
    status_count = filtered_df.groupby(['date', 'order_status']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 6))
    status_count.plot(kind='area', stacked=True, ax=ax, cmap='Set1')
    ax.set_title("Order Distribution by Status Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Orders")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

def order_distribution_ui():
    st.title("E-Commerce Public Dataset")
    st.subheader("📦 Order Distribution by Status and Time")
    df = load_data()

    st.sidebar.header("Filters - Order Distribution")
    start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2017-01-01"))
    end_date = st.sidebar.date_input("End Date", pd.to_datetime("2018-12-31"))
    status_options = ["All"] + df['order_status'].dropna().unique().tolist()
    order_status = st.sidebar.selectbox("Order Status", status_options)

    filtered_df = filter_data(df, start_date, end_date, order_status)
    st.write(f"Total Orders: {len(filtered_df)}")
    if not filtered_df.empty:
        plot_order_distribution(filtered_df)
    else:
        st.warning("No data found for selected filters.")

# ==========================
# PAYMENT MODULE
# ==========================
def payment_analysis_ui():
    st.title("E-Commerce Public Dataset")
    st.subheader("💳 Payment Analysis")
    data = load_data()

    st.sidebar.header("Filters - Payment")

    payment_types = data['payment_type'].dropna().unique()
    selected_payment_types = st.sidebar.multiselect("Select Payment Types", payment_types, default=payment_types)

    min_payment = float(data['payment_value'].min())
    max_payment = float(data['payment_value'].max())
    payment_range = st.sidebar.slider("Select Payment Value Range", min_value=min_payment, max_value=max_payment,
                                      value=(min_payment, max_payment))

    filtered_payment = data[
        (data['payment_type'].isin(selected_payment_types)) &
        (data['payment_value'] >= payment_range[0]) &
        (data['payment_value'] <= payment_range[1])
    ]

    st.write(f"Total Payments: {len(filtered_payment)}")
    fig, ax = plt.subplots()
    sns.histplot(filtered_payment['payment_value'], bins=30, kde=True, ax=ax)
    ax.set_title("Distribution of Payment Values")
    ax.set_xlabel("Payment Value")
    st.pyplot(fig)

# ==========================
# MAIN STREAMLIT APP
# ==========================
def main():
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Go to", ["Order Distribution", "Payment Analysis"])

    if page == "Order Distribution":
        order_distribution_ui()

    elif page == "Payment Analysis":
        payment_analysis_ui()

if __name__ == "__main__":
    main()
