import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configure page
st.set_page_config(page_title="Receipt Analytics Dashboard", layout="wide")
st.title(":material/receipt_long: Receipt Data Analysis Dashboard")

# Sample JSON structure for user reference
st.sidebar.subheader("Expected JSON Format")
st.sidebar.code("""
[
  {
    "brand": "Brand A",
    "item": "Product X",
    "price": 29.99,
    "quantity": 2,
    "channel": "D2C",
    "location": "New York",
    "date": "2023-07-15T14:30:00",
    "discount": 5.00
  },
  ...
]
""")
st.sidebar.markdown("**Note:** Upload JSON files with this structure")

# File uploader
uploaded_file = st.file_uploader("Upload receipts JSON file", type="json")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        df = pd.DataFrame(data)
        
        # Convert and clean data
        df['date'] = pd.to_datetime(df['date'])
        df['total_price'] = df['price'] * df['quantity']
        df['discount_pct'] = (df['discount'] / (df['total_price'] + df['discount'])) * 100
        
        # Store in session state
        st.session_state.df = df
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

if not st.session_state.df.empty:
    df = st.session_state.df
    st.success(f"Loaded {len(df)} records")
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs([
        "🏷️ Brand Performance", 
        "🛒 Shopping Habits", 
        "💲 Pricing & Discounts"
    ])
    
    with tab1:
        st.subheader("Brand Performance Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            # Brand sales volume
            brand_counts = df['brand'].value_counts().head(10)
            fig, ax = plt.subplots()
            brand_counts.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_title('Top 10 Brands by Purchase Frequency')
            ax.set_ylabel('Number of Purchases')
            st.pyplot(fig)
            
        with col2:
            # Brand revenue
            brand_revenue = df.groupby('brand')['total_price'].sum().nlargest(10)
            fig, ax = plt.subplots()
            brand_revenue.plot(kind='bar', ax=ax, color='lightgreen')
            ax.set_title('Top 10 Brands by Total Revenue')
            ax.set_ylabel('Total Revenue ($)')
            st.pyplot(fig)
            
        # Brand-channel relationship
        st.subheader("Brand Preference by Channel")
        brand_channel = pd.crosstab(df['brand'], df['channel']).head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        brand_channel.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title('Top Brands: D2C vs Retail Distribution')
        ax.set_ylabel('Purchase Count')
        st.pyplot(fig)
    
    with tab2:
        st.subheader("Shopping Habits Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            # Location analysis
            location_counts = df['location'].value_counts().head(10)
            fig, ax = plt.subplots()
            location_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_title('Top 10 Purchase Locations')
            ax.set_ylabel('')
            st.pyplot(fig)
            
        with col2:
            # Time of day analysis
            df['hour'] = df['date'].dt.hour
            time_counts = df['hour'].value_counts().sort_index()
            fig, ax = plt.subplots()
            time_counts.plot(kind='line', marker='o', ax=ax)
            ax.set_title('Purchase Activity by Hour of Day')
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Number of Purchases')
            ax.set_xticks(range(0, 24))
            st.pyplot(fig)
            
        # Channel distribution
        st.subheader("Purchase Channel Distribution")
        channel_counts = df['channel'].value_counts()
        fig, ax = plt.subplots()
        channel_counts.plot(kind='pie', autopct='%1.1f%%', colors=['lightcoral', 'lightblue'])
        ax.set_title('D2C vs Retail Distribution')
        ax.set_ylabel('')
        st.pyplot(fig)
    
    with tab3:
        st.subheader("Pricing & Discount Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            # Price distribution
            fig, ax = plt.subplots()
            sns.histplot(df['price'], bins=20, kde=True, ax=ax)
            ax.set_title('Price Distribution')
            ax.set_xlabel('Price ($)')
            st.pyplot(fig)
            
        with col2:
            # Discount patterns
            fig, ax = plt.subplots()
            sns.scatterplot(data=df, x='price', y='discount_pct', ax=ax)
            ax.set_title('Discount % vs Original Price')
            ax.set_xlabel('Price ($)')
            ax.set_ylabel('Discount (%)')
            st.pyplot(fig)
            
        # Discounts by brand
        st.subheader("Discount Patterns by Brand")
        brand_discounts = df.groupby('brand')['discount_pct'].mean().nlargest(10)
        fig, ax = plt.subplots()
        brand_discounts.plot(kind='bar', color='gold', ax=ax)
        ax.set_title('Top 10 Brands by Average Discount %')
        ax.set_ylabel('Average Discount (%)')
        st.pyplot(fig)

else:
    st.info("Please upload a JSON file to get started")
