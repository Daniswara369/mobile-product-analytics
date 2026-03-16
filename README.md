# ⚡ Product Analytics Dashboard

This is a modern, high-fidelity analytics dashboard built to bridge the gap between static charts and automated AI insights. Instead of just looking at numbers, you can actually **talk** to this dashboard to understand why your metrics are moving.

I built this using the **Google Merchandise Store** dataset to simulate a real-world e-commerce environment.

## 📊 The Data

This project analyzes real-world e-commerce data from the **Google Merchandise Store** (a live web store that sells Google-branded merchandise). 

The dataset provides a granular look at the customer journey, including:
- **User Personas**: Geographic location, device type (Mobile/Desktop/Tablet), and long-term value (LTV).
- **Behavioral Events**: Tracking the path from `session_start` → `view_item` → `add_to_cart` → `begin_checkout` → `purchase`.
- **Product Intelligence**: Revenue performance and transaction volume across different marketing regions.

By using this data, the dashboard can simulate how a "Senior Product Analyst" would investigate growth bottlenecks and conversion drop-offs.

## ✨ What's Inside?

- **🤖 AI Data Intelligence**: A dedicated assistant powered by **Gemini 2.0 Flash**. It reads the live context of your filters and answers questions like *"Why did our conversion drop on mobile last week?"*
- **📈 Growth Analytics**: Segmented views for **Acquisition** (where users come from), **Behavior** (what they do), and **Revenue** (how much they spend).
- **🔮 Predictive Forecasting**: Uses the **Prophet** engine to project user activity trends 30 days into the future.
- **🎯 Smart Funnels**: A clear visualization of the checkout process to pinpoint exactly where users are dropping off.

## 🛠️ Tech Stack

- **Frontend**: Streamlit (with custom CSS injection)
- **AI Engine**: Google Gemini API
- **Forecasting**: Facebook Prophet
- **Visuals**: Plotly (Interactive)
- **Data**: Pandas / NumPy

## 🚀 Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/Daniswara369/mobile-product-analytics.git
   cd mobile-product-analytics
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your API Key**
   Create a folder called `.streamlit` and a file inside it called `secrets.toml`:
   ```toml
   # .streamlit/secrets.toml
   GEMINI_API_KEY = "your_google_ai_key_here"
   ```

4. **Launch the Dashboard**
   ```bash
   streamlit run app.py
   ```

---
*Built with ❤️ for my Data Analytics Portfolio.*
