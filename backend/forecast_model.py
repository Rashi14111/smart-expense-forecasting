import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def forecast_expenses(monthly_data, periods=6):
    """Generate simple expense forecast without sklearn"""
    try:
        if len(monthly_data) < 3:
            return pd.DataFrame()
        
        # Simple forecasting using linear regression from numpy
        X = np.array(range(len(monthly_data)))
        y = monthly_data['Total_Amount'].values
        
        # Manual linear regression
        x_mean = np.mean(X)
        y_mean = np.mean(y)
        
        numerator = np.sum((X - x_mean) * (y - y_mean))
        denominator = np.sum((X - x_mean) ** 2)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        intercept = y_mean - slope * x_mean
        
        # Generate future predictions
        future_X = np.array(range(len(monthly_data), len(monthly_data) + periods))
        predictions = slope * future_X + intercept
        
        # Ensure positive predictions
        predictions = np.maximum(predictions, 0)
        
        # Generate future dates
        last_date = monthly_data['YearMonth'].iloc[-1]
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=periods,
            freq='M'
        )
        
        forecast_df = pd.DataFrame({
            'Date': future_dates,
            'Forecast': predictions.round(2)
        })
        
        return forecast_df
        
    except Exception as e:
        print(f"Error in forecasting: {e}")
        return pd.DataFrame()

def calculate_seasonal_trends(monthly_data):
    """Calculate seasonal trends in simple language"""
    if len(monthly_data) < 6:
        return "📊 We're still learning your patterns. As we get more months of data, we'll spot your seasonal spending habits."
    
    try:
        monthly_data['Month'] = monthly_data['YearMonth'].dt.month
        monthly_avg = monthly_data.groupby('Month')['Total_Amount'].mean()
        
        if len(monthly_avg) >= 3:
            peak_month = monthly_avg.idxmax()
            low_month = monthly_avg.idxmin()
            
            months = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            
            return f"🎯 We noticed you tend to spend most in {months[peak_month]} and least in {months[low_month]}. Plan your budget around these patterns!"
        else:
            return "📈 Keep tracking your expenses - we're starting to see some monthly patterns emerge."
            
    except Exception as e:
        return "🔍 Looking for patterns in your monthly spending..."

def advanced_ml_analysis(monthly_data, df):
    """Provide simple ML insights in plain language"""
    insights = {}
    
    try:
        # Pattern analysis
        if len(monthly_data) >= 4:
            # Manual trend calculation
            X = np.array(range(len(monthly_data)))
            y = monthly_data['Total_Amount'].values
            
            x_mean = np.mean(X)
            y_mean = np.mean(y)
            
            numerator = np.sum((X - x_mean) * (y - y_mean))
            denominator = np.sum((X - x_mean) ** 2)
            
            if denominator == 0:
                trend = 0
            else:
                trend = numerator / denominator
                
            if trend > monthly_data['Total_Amount'].mean() * 0.1:
                insights['patterns'] = "📈 Your expenses are growing steadily month-over-month. This could be due to business growth or price increases."
            elif trend < -monthly_data['Total_Amount'].mean() * 0.1:
                insights['patterns'] = "📉 Great news! Your expenses are trending downward, showing good cost control."
            else:
                insights['patterns'] = "➡️ Your spending is quite stable month-to-month, which is excellent for budget planning."
        else:
            insights['patterns'] = "🔄 We're still learning your spending patterns. More data will help us provide better insights."
        
        # Optimization insights
        if "Expense Head" in df.columns:
            category_stats = df.groupby('Expense Head')['Amount'].sum()
            top_category = category_stats.idxmax()
            top_percentage = (category_stats.max() / category_stats.sum() * 100)
            
            if top_percentage > 40:
                insights['optimization'] = f"💡 {top_category} is your biggest expense area ({top_percentage:.1f}%). Small savings here could make a big difference to your bottom line."
            else:
                insights['optimization'] = "✅ Your spending is well distributed. Look for small savings across all categories rather than focusing on one area."
        else:
            insights['optimization'] = "🎯 Regular expense reviews can help identify savings opportunities. Consider setting monthly budget targets."
        
        # Forecasting insights
        if len(monthly_data) >= 3:
            volatility = monthly_data['Total_Amount'].std() / monthly_data['Total_Amount'].mean()
            if volatility < 0.2:
                insights['forecasting'] = "✅ Your spending is very predictable! This makes budget planning reliable and straightforward."
            else:
                insights['forecasting'] = "📊 Your spending varies month-to-month. Consider setting aside extra funds for unpredictable months."
        else:
            insights['forecasting'] = "🔮 We're building a better understanding of your future expenses as we collect more data."
        
        # Risk assessment
        volatility = monthly_data['Total_Amount'].std() / monthly_data['Total_Amount'].mean() if len(monthly_data) > 1 else 0
        efficiency_score = max(0, 10 - (volatility * 8)) 
        if efficiency_score >= 8:
            insights['risk'] = "🟢 Excellent expense management! Your spending patterns are stable and well-controlled."
        elif efficiency_score >= 6:
            insights['risk'] = "🟡 Good expense control. Some monthly variation, but overall well managed."
        else:
            insights['risk'] = "🔴 Higher spending variation detected. Regular monitoring can help smooth out the fluctuations."
        
    except Exception as e:
        insights = {
            'patterns': "🤖 Analyzing your spending patterns...",
            'optimization': "💡 Looking for money-saving opportunities...",
            'forecasting': "🔮 Preparing future expense insights...",
            'risk': "🛡️ Checking your expense stability..."
        }
    
    return insights