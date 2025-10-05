import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import io
from datetime import datetime

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