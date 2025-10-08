import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import io
from datetime import datetime
from backend.data_loader import preprocess_data, calculate_comprehensive_metrics
from backend.forecast_model import forecast_expenses, calculate_seasonal_trends

def generate_comprehensive_pdf(df, category, metrics=None, monthly_df=None, forecast_df=None):
    """Generate a comprehensive PDF report for expense analysis"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title
    elements.append(Paragraph(f"SMART EXPENSE ANALYSIS REPORT - {category.upper()}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Executive Summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    if metrics:
        summary_data = [
            ["Metric", "Value", "Assessment"],
            ["Total Expenditure", f"₹{metrics['total_spent']:,.0f}", "Overall Spend"],
            ["Monthly Average", f"₹{metrics['avg_monthly']:,.0f}", "Budget Baseline"],
            ["Growth Rate", f"{metrics['growth_rate']:+.1f}%", metrics['trend_description']],
            ["Efficiency Score", f"{metrics['efficiency_score']}/10", metrics['efficiency_comment']],
            ["Analysis Period", f"{metrics['analysis_period']} months", "Data Coverage"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(summary_table)
    
    elements.append(Spacer(1, 20))
    
    # Key Insights
    elements.append(Paragraph("KEY STRATEGIC INSIGHTS", heading_style))
    
    if metrics:
        insights = [
            f"• Your expense efficiency score is {metrics['efficiency_score']}/10 - {metrics['efficiency_comment'].lower()}",
            f"• Monthly spending varies by {metrics['variance']*100:.1f}% - {'Excellent stability' if metrics['variance'] < 0.3 else 'Moderate variation' if metrics['variance'] < 0.6 else 'High volatility'}",
            f"• Growth trend shows {metrics['growth_rate']:+.1f}% - {metrics['trend_description']}",
            f"• Peak spending occurred in {metrics['highest_month_name']} at ₹{metrics['highest_month_amount']:,.0f}",
            f"• Most efficient month was {metrics['lowest_month_name']} at ₹{metrics['lowest_month_amount']:,.0f}"
        ]
        
        for insight in insights:
            elements.append(Paragraph(insight, styles['Normal']))
            elements.append(Spacer(1, 6))
    
    elements.append(Spacer(1, 20))
    
    # Expense Distribution
    if "Expense Head" in df.columns:
        elements.append(Paragraph("EXPENSE CATEGORY BREAKDOWN", heading_style))
        
        expense_dist = df.groupby('Expense Head')['Amount'].sum().sort_values(ascending=False)
        category_data = [["Category", "Amount", "Percentage"]]
        
        total_spent = expense_dist.sum()
        for category_name, amount in expense_dist.head(8).items():
            percentage = (amount / total_spent * 100)
            category_data.append([
                category_name,
                f"₹{amount:,.0f}",
                f"{percentage:.1f}%"
            ])
        
        category_table = Table(category_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(category_table)
    
    elements.append(Spacer(1, 20))
    
    # Monthly Trends
    if monthly_df is not None and len(monthly_df) > 0:
        elements.append(Paragraph("MONTHLY TREND ANALYSIS", heading_style))
        
        trend_data = [["Month", "Amount", "Growth"]]
        for _, row in monthly_df.iterrows():
            trend_data.append([
                row['YearMonth'].strftime('%b %Y'),
                f"₹{row['Total_Amount']:,.0f}",
                f"{row.get('MoM_Growth', 0):.1f}%" if 'MoM_Growth' in row else "N/A"
            ])
        
        trend_table = Table(trend_data, colWidths=[1.5*inch, 1.5*inch, 1*inch])
        trend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(trend_table)
    
    elements.append(Spacer(1, 20))
    
    # Forecast Insights
    if forecast_df is not None and len(forecast_df) > 0:
        elements.append(Paragraph("FUTURE FORECAST", heading_style))
        
        forecast_data = [["Month", "Predicted Amount"]]
        total_forecast = 0
        for _, row in forecast_df.iterrows():
            forecast_data.append([
                row['Date'].strftime('%b %Y'),
                f"₹{row['Forecast']:,.0f}"
            ])
            total_forecast += row['Forecast']
        
        forecast_table = Table(forecast_data, colWidths=[1.5*inch, 1.5*inch])
        forecast_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(forecast_table)
        
        # Forecast summary
        elements.append(Spacer(1, 12))
        forecast_growth = ((forecast_df['Forecast'].iloc[-1] - forecast_df['Forecast'].iloc[0]) / forecast_df['Forecast'].iloc[0]) * 100
        elements.append(Paragraph(f"Total Forecasted Spend: ₹{total_forecast:,.0f} over {len(forecast_df)} months", styles['Normal']))
        elements.append(Paragraph(f"Predicted Growth Trend: {forecast_growth:+.1f}%", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # Strategic Recommendations
    elements.append(Paragraph("STRATEGIC RECOMMENDATIONS", heading_style))
    
    recommendations = [
        "1. IMPLEMENT PROACTIVE BUDGET CONTROLS",
        "• Set monthly spending limits with 15% contingency",
        "• Establish weekly expense review cadence",
        "• Implement variance threshold alerts",
        "",
        "2. OPTIMIZE COST STRUCTURE",
        "• Focus on highest-spend categories for maximum impact",
        "• Renegotiate vendor contracts annually",
        "• Implement process efficiency improvements",
        "",
        "3. ENHANCE FORECASTING ACCURACY",
        "• Use predictive analytics for budget planning",
        "• Monitor leading indicators for trend changes",
        "• Adjust forecasts based on actual performance",
        "",
        "4. DRIVE EFFICIENCY IMPROVEMENTS",
        "• Target 8+ efficiency score in next quarter",
        "• Reduce monthly variance below 25%",
        "• Implement continuous improvement program"
    ]
    
    for rec in recommendations:
        if rec.startswith("•"):
            elements.append(Paragraph(rec, styles['Normal']))
        elif rec and not rec.isupper():
            elements.append(Paragraph(rec, styles['Normal']))
        elif rec:
            elements.append(Paragraph(rec, styles['Heading3']))
        else:
            elements.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_company_pdf_report(data):
    """Generate comprehensive company-wide PDF report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title Page
    elements.append(Paragraph("COMPREHENSIVE COMPANY EXPENSE ANALYSIS", title_style))
    elements.append(Paragraph("Complete Financial Intelligence Report", styles['Heading2']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
    elements.append(Paragraph("Confidential Business Intelligence", styles['Normal']))
    elements.append(Spacer(1, 40))
    
    # Company Overview
    elements.append(Paragraph("🏢 COMPANY OVERVIEW", heading_style))
    
    # Calculate company-wide metrics
    all_data = []
    category_metrics = {}
    total_company_spend = 0
    total_transactions = 0
    
    for category_name, df in data.items():
        monthly_df = preprocess_data(df)
        if not monthly_df.empty:
            metrics = calculate_comprehensive_metrics(monthly_df, df, category_name)
            category_metrics[category_name] = metrics
            all_data.append(df)
            total_company_spend += metrics['total_spent']
            total_transactions += metrics['transaction_count']
    
    # Combine all data for overall metrics
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_monthly = preprocess_data(combined_df)
        company_metrics = calculate_comprehensive_metrics(combined_monthly, combined_df, "All Categories")
        
        # Company Summary
        summary_data = [
            ["COMPANY METRIC", "VALUE", "BUSINESS IMPACT"],
            ["Total Company Spend", f"₹{total_company_spend:,.0f}", "Overall Financial Outlay"],
            ["Average Monthly Spend", f"₹{company_metrics['avg_monthly']:,.0f}", "Budget Planning Baseline"],
            ["Overall Growth Rate", f"{company_metrics['growth_rate']:+.1f}%", "Financial Trajectory"],
            ["Company Efficiency Score", f"{company_metrics['efficiency_score']}/10", "Spending Management Quality"],
            ["Total Transactions", f"{total_transactions:,}", "Operational Volume"],
            ["Departments Analyzed", f"{len(category_metrics)}", "Business Coverage"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(summary_table)
    
    elements.append(PageBreak())
    
    # Department Performance Comparison
    elements.append(Paragraph("📊 DEPARTMENT PERFORMANCE ANALYSIS", heading_style))
    
    if category_metrics:
        # Create department comparison table
        dept_data = [["DEPARTMENT", "TOTAL SPEND", "MONTHLY AVG", "GROWTH RATE", "EFFICIENCY"]]
        
        for dept_name, metrics in category_metrics.items():
            growth_color = "🟢" if metrics['growth_rate'] <= 5 else "🟡" if metrics['growth_rate'] <= 15 else "🔴"
            efficiency_color = "🟢" if metrics['efficiency_score'] >= 7 else "🟡" if metrics['efficiency_score'] >= 5 else "🔴"
            
            dept_data.append([
                dept_name,
                f"₹{metrics['total_spent']:,.0f}",
                f"₹{metrics['avg_monthly']:,.0f}",
                f"{growth_color} {metrics['growth_rate']:+.1f}%",
                f"{efficiency_color} {metrics['efficiency_score']}/10"
            ])
        
        dept_table = Table(dept_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        dept_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(dept_table)
        
        elements.append(Spacer(1, 20))
        
        # Department Insights
        elements.append(Paragraph("🎯 KEY DEPARTMENT INSIGHTS", heading_style))
        
        # Find top performers
        highest_spend_dept = max(category_metrics.items(), key=lambda x: x[1]['total_spent'])
        most_efficient_dept = max(category_metrics.items(), key=lambda x: x[1]['efficiency_score'])
        fastest_growing_dept = max(category_metrics.items(), key=lambda x: x[1]['growth_rate'])
        
        insights = [
            f"• <b>Highest Spending Department:</b> {highest_spend_dept[0]} (₹{highest_spend_dept[1]['total_spent']:,.0f}) - {highest_spend_dept[1]['total_spent']/total_company_spend*100:.1f}% of total",
            f"• <b>Most Efficient Department:</b> {most_efficient_dept[0]} ({most_efficient_dept[1]['efficiency_score']}/10 score) - Excellent cost control",
            f"• <b>Fastest Growing Department:</b> {fastest_growing_dept[0]} ({fastest_growing_dept[1]['growth_rate']:+.1f}% growth) - Monitor for budget impact",
            f"• <b>Overall Company Health:</b> {company_metrics['efficiency_comment']} with {company_metrics['growth_rate']:+.1f}% growth trend"
        ]
        
        for insight in insights:
            elements.append(Paragraph(insight, styles['Normal']))
            elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # Detailed Department Analysis
    elements.append(Paragraph("🔍 DETAILED DEPARTMENT BREAKDOWN", heading_style))
    
    for dept_name, metrics in category_metrics.items():
        elements.append(Paragraph(f"📁 {dept_name.upper()} DEPARTMENT", styles['Heading3']))
        
        dept_detail_data = [
            ["METRIC", "VALUE", "PERFORMANCE"],
            ["Total Expenditure", f"₹{metrics['total_spent']:,.0f}", f"{metrics['total_spent']/total_company_spend*100:.1f}% of company total"],
            ["Monthly Average", f"₹{metrics['avg_monthly']:,.0f}", "Department baseline"],
            ["Growth Trend", f"{metrics['growth_rate']:+.1f}%", metrics['trend_description']],
            ["Efficiency Score", f"{metrics['efficiency_score']}/10", metrics['efficiency_comment']],
            ["Peak Month", f"{metrics['highest_month_name']}", f"₹{metrics['highest_month_amount']:,.0f}"],
            ["Transactions", f"{metrics['transaction_count']}", "Volume processed"]
        ]
        
        dept_table = Table(dept_detail_data, colWidths=[1.8*inch, 1.5*inch, 2*inch])
        dept_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#95a5a6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(dept_table)
        elements.append(Spacer(1, 15))
    
    elements.append(PageBreak())
    
    # Strategic Recommendations
    elements.append(Paragraph("🚀 STRATEGIC BUSINESS RECOMMENDATIONS", heading_style))
    
    recommendations = [
        "BUSINESS-WIDE STRATEGIES",
        "1. ENTERPRISE COST OPTIMIZATION",
        "• Implement cross-departmental cost-sharing initiatives",
        "• Centralize procurement for better negotiation power", 
        "• Establish company-wide expense policies and controls",
        "",
        "2. DEPARTMENTAL PERFORMANCE MANAGEMENT",
        "• Set department-specific efficiency targets",
        "• Implement monthly performance dashboards",
        "• Create incentive programs for cost savings",
        "",
        "3. FINANCIAL FORECASTING & PLANNING",
        "• Develop rolling 12-month expense forecasts",
        "• Implement scenario planning for different growth rates",
        "• Establish contingency budgets for unexpected expenses",
        "",
        "4. TECHNOLOGY & AUTOMATION",
        "• Implement automated expense tracking systems",
        "• Use AI-powered analytics for pattern detection",
        "• Create real-time budget monitoring dashboards",
        "",
        "5. CONTINUOUS IMPROVEMENT",
        "• Conduct quarterly expense reviews",
        "• Benchmark against industry standards",
        "• Implement best practice sharing across departments"
    ]
    
    for rec in recommendations:
        if rec.startswith("•"):
            elements.append(Paragraph(rec, styles['Normal']))
        elif rec and not rec.isupper():
            elements.append(Paragraph(rec, styles['Normal']))
        elif rec:
            elements.append(Paragraph(rec, styles['Heading3']))
        else:
            elements.append(Spacer(1, 6))
    
    elements.append(Spacer(1, 20))
    
    # Risk Assessment
    elements.append(Paragraph("🛡️ COMPANY RISK ASSESSMENT", heading_style))
    
    risk_factors = [
        f"• <b>Spending Volatility:</b> {company_metrics['variance']*100:.1f}% monthly variation - {'Low Risk' if company_metrics['variance'] < 0.3 else 'Medium Risk' if company_metrics['variance'] < 0.6 else 'High Risk'}",
        f"• <b>Growth Sustainability:</b> {company_metrics['growth_rate']:+.1f}% trend - {'Sustainable' if abs(company_metrics['growth_rate']) < 10 else 'Monitor Closely'}",
        f"• <b>Efficiency Management:</b> {company_metrics['efficiency_score']}/10 score - {'Well Managed' if company_metrics['efficiency_score'] >= 7 else 'Needs Improvement'}",
        "• <b>Recommendation:</b> Implement monthly financial health checks and early warning systems"
    ]
    
    for risk in risk_factors:
        elements.append(Paragraph(risk, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(Spacer(1, 20))
    
    # Conclusion
    elements.append(Paragraph("📈 BUSINESS OUTLOOK", heading_style))
    conclusion_text = f"""
    Based on the comprehensive analysis of {len(category_metrics)} departments and {total_transactions:,} transactions, 
    the company demonstrates {company_metrics['efficiency_comment'].lower()}. 
    
    The overall growth trend of {company_metrics['growth_rate']:+.1f}% indicates {'healthy expansion' if company_metrics['growth_rate'] > 0 else 'cost optimization efforts'}. 
    With strategic implementation of the recommended actions, the company can achieve improved financial performance 
    and sustainable growth in the coming quarters.
    
    Next Review Date: {(datetime.now() + pd.DateOffset(months=1)).strftime('%B %d, %Y')}
    """
    
    elements.append(Paragraph(conclusion_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_quick_insights_pdf(df, category):
    """Generate a quick insights PDF for filtered data"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=1
    )
    
    # Title
    elements.append(Paragraph(f"QUICK EXPENSE INSIGHTS - {category.upper()}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Basic Statistics
    elements.append(Paragraph("📊 BASIC STATISTICS", styles['Heading2']))
    
    stats_data = [
        ["Metric", "Value"],
        ["Total Records", f"{len(df):,}"],
        ["Total Amount", f"₹{df['Amount'].sum():,.0f}"],
        ["Average Amount", f"₹{df['Amount'].mean():,.0f}"],
        ["Maximum Amount", f"₹{df['Amount'].max():,.0f}"],
        ["Minimum Amount", f"₹{df['Amount'].min():,.0f}"],
        ["Date Range", f"{df['Date'].min().strftime('%d/%m/%Y')} to {df['Date'].max().strftime('%d/%m/%Y')}"]
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
    ]))
    elements.append(stats_table)
    
    elements.append(Spacer(1, 20))
    
    # Category Breakdown (if available)
    if "Expense Head" in df.columns:
        elements.append(Paragraph("📋 CATEGORY BREAKDOWN", styles['Heading2']))
        
        category_dist = df.groupby('Expense Head')['Amount'].sum().sort_values(ascending=False).head(10)
        category_data = [["Category", "Amount", "Percentage"]]
        
        total = category_dist.sum()
        for cat, amount in category_dist.items():
            percentage = (amount / total * 100)
            category_data.append([cat, f"₹{amount:,.0f}", f"{percentage:.1f}%"])
        
        cat_table = Table(category_data, colWidths=[2*inch, 1.5*inch, 1*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(cat_table)
    
    elements.append(Spacer(1, 20))
    
    # Recent Transactions
    elements.append(Paragraph("🕒 RECENT TRANSACTIONS", styles['Heading2']))
    
    recent_data = [["Date", "Category", "Amount"]]
    recent_df = df.nlargest(10, 'Date') if len(df) > 10 else df
    
    for _, row in recent_df.iterrows():
        category_name = row['Expense Head'] if 'Expense Head' in row else 'N/A'
        recent_data.append([
            row['Date'].strftime('%d/%m/%Y'),
            category_name,
            f"₹{row['Amount']:,.0f}"
        ])
    
    recent_table = Table(recent_data, colWidths=[1.2*inch, 2*inch, 1*inch])
    recent_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
    ]))
    elements.append(recent_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
