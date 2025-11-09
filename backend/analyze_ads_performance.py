#!/usr/bin/env python3
"""
Google Ads Performance Analysis Script
Analyzes campaign performance trends and identifies potential issues
"""

import sys
sys.path.append('.')
from app.services.google_ads import GoogleAdsService
from datetime import datetime, timedelta

def analyze_campaigns():
    print('📊 Google Ads Performance Analysis')
    print('=' * 50)

    service = GoogleAdsService()

    # Daten für längeren Zeitraum holen (14 Tage)
    print('📈 Analyzing campaign performance trends...')
    data = service.fetch_data_for_date_range(days_back=14)

    if not data:
        print('❌ No campaign data available')
        return

    print(f'\n📊 Found {len(data)} records from last 14 days')
    
    # Gruppiere nach Kampagnen
    campaigns = {}
    for record in data:
        campaign_name = record['campaign_name']
        date = str(record['date'])
        
        if campaign_name not in campaigns:
            campaigns[campaign_name] = []
        
        campaigns[campaign_name].append({
            'date': date,
            'impressions': record['impressions'],
            'clicks': record['clicks'],
            'cost': record['cost_micros'] / 1000000,
            'cpc': record.get('cpc', 0),
            'ctr': record.get('ctr', 0)
        })
    
    print(f'\n🎯 Active Campaigns: {len(campaigns)}')
    
    # Gesamtanalyse
    total_impressions = sum(r['impressions'] for r in data)
    total_clicks = sum(r['clicks'] for r in data)
    total_cost = sum(r['cost_micros'] for r in data) / 1000000
    avg_cpc = total_cost / total_clicks if total_clicks > 0 else 0
    avg_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
    
    print(f'\n📈 Overall Performance (14 days):')
    print(f'Total Impressions: {total_impressions:,}')
    print(f'Total Clicks: {total_clicks:,}')
    print(f'Total Cost: €{total_cost:.2f}')
    print(f'Average CPC: €{avg_cpc:.2f}')
    print(f'Average CTR: {avg_ctr:.2f}%')
    
    # Analysiere jede Kampagne
    for campaign_name, records in campaigns.items():
        print(f'\n📱 {campaign_name}')
        print('-' * 40)
        
        # Sortiere nach Datum
        records.sort(key=lambda x: x['date'])
        
        if len(records) >= 4:
            # Vergleiche erste Hälfte vs zweite Hälfte
            mid = len(records) // 2
            first_half = records[:mid]
            second_half = records[mid:]
            
            # Durchschnitte berechnen
            def safe_avg(values):
                return sum(values) / len(values) if values and len(values) > 0 else 0
            
            avg_impressions_first = safe_avg([r['impressions'] for r in first_half])
            avg_impressions_second = safe_avg([r['impressions'] for r in second_half])
            
            avg_cpc_first = safe_avg([r['cpc'] for r in first_half if r['cpc'] > 0])
            avg_cpc_second = safe_avg([r['cpc'] for r in second_half if r['cpc'] > 0])
            
            avg_ctr_first = safe_avg([r['ctr'] for r in first_half if r['ctr'] > 0])
            avg_ctr_second = safe_avg([r['ctr'] for r in second_half if r['ctr'] > 0])
            
            # Berechne Trends
            impressions_change = 0
            if avg_impressions_first > 0:
                impressions_change = ((avg_impressions_second - avg_impressions_first) / avg_impressions_first) * 100
            
            cpc_change = 0
            if avg_cpc_first > 0:
                cpc_change = ((avg_cpc_second - avg_cpc_first) / avg_cpc_first) * 100
            
            ctr_change = 0
            if avg_ctr_first > 0:
                ctr_change = ((avg_ctr_second - avg_ctr_first) / avg_ctr_first) * 100
            
            print(f'📊 Performance Trends:')
            print(f'  Impressions: {impressions_change:+.1f}%')
            print(f'  CPC: €{avg_cpc_second:.2f} ({cpc_change:+.1f}%)')
            print(f'  CTR: {avg_ctr_second:.2f}% ({ctr_change:+.1f}%)')
            
            # Identifiziere Probleme
            issues = []
            recommendations = []
            
            if impressions_change < -20:
                issues.append('⚠️ Significant impression drop (>20%)')
                recommendations.append('• Check keyword bids and budget')
                recommendations.append('• Review ad schedule and targeting')
                
            if cpc_change > 25:
                issues.append('💰 High CPC increase (>25%)')
                recommendations.append('• Review keyword competition')
                recommendations.append('• Optimize ad quality score')
                recommendations.append('• Consider negative keywords')
                
            if ctr_change < -15:
                issues.append('📉 CTR decline (>15%)')
                recommendations.append('• Test new ad copy variations')
                recommendations.append('• Review ad relevance to keywords')
            
            if issues:
                print('\n🚨 Issues Detected:')
                for issue in issues:
                    print(f'  {issue}')
                    
                print('\n💡 Recommendations:')
                for rec in recommendations:
                    print(f'  {rec}')
            else:
                print('\n✅ Campaign performance is stable')
        
        # Zeige letzte 5 Tage Details
        print(f'\n📅 Last 5 days performance:')
        for record in records[-5:]:
            print(f'  {record["date"]}: {record["impressions"]:3d} imp, '
                  f'{record["clicks"]:2d} clicks, €{record["cost"]:5.2f}, '
                  f'€{record["cpc"]:4.2f} CPC, {record["ctr"]:4.1f}% CTR')

if __name__ == "__main__":
    analyze_campaigns()