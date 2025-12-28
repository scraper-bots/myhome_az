"""
Real Estate Market Analysis - Chart Generation Script
Generates business-focused visualizations for executive decision-making
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for professional business charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create charts directory
charts_dir = Path('charts')
charts_dir.mkdir(exist_ok=True)

# Load data
print("Loading dataset...")
df = pd.read_csv('myhome_listings_20250929_003143.csv')

# Clean price column
df['price_clean'] = df['price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
df['price_clean'] = pd.to_numeric(df['price_clean'], errors='coerce')

print(f"Total records: {len(df):,}")

# ============================================================================
# CHART 1: Market Composition - Sale vs Rent
# ============================================================================
print("Generating Chart 1: Market Composition...")
fig, ax = plt.subplots(figsize=(10, 6))
market_comp = df['announcement_type'].value_counts()
colors = ['#2E86AB', '#A23B72']
bars = ax.bar(market_comp.index, market_comp.values, color=colors, edgecolor='black', linewidth=1.2)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({height/len(df)*100:.1f}%)',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_xlabel('Listing Type', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Market Composition: Sales Dominate the Real Estate Market',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / '01_market_composition.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 2: Room Count Distribution
# ============================================================================
print("Generating Chart 2: Property Size Distribution...")
fig, ax = plt.subplots(figsize=(12, 6))
room_dist = df['room_count'].value_counts().sort_index()
room_dist = room_dist[room_dist.index <= 10]  # Focus on mainstream properties

bars = ax.bar(room_dist.index, room_dist.values, color='#06A77D',
              edgecolor='black', linewidth=1.2, alpha=0.8)

# Highlight 2-3 room properties (market majority)
for i, (idx, val) in enumerate(room_dist.items()):
    if idx in [2.0, 3.0]:
        bars[i].set_color('#F77F00')
        bars[i].set_alpha(1.0)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xlabel('Number of Rooms', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Property Size Distribution: 2-3 Room Properties Dominate (70% of Market)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(room_dist.index)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / '02_room_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 3: Top 10 Regions in Baku by Volume
# ============================================================================
print("Generating Chart 3: Regional Market Volume...")
baku_df = df[df['city'] == 'Bakı']
top_regions = baku_df['region'].value_counts().head(10)

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(range(len(top_regions)), top_regions.values, color='#4361EE',
               edgecolor='black', linewidth=1.2)

# Add value labels
for i, (region, count) in enumerate(top_regions.items()):
    ax.text(count, i, f'  {count:,}', va='center', fontsize=11, fontweight='bold')

ax.set_yticks(range(len(top_regions)))
ax.set_yticklabels(top_regions.index, fontsize=11)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Regions in Baku by Listing Volume',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(charts_dir / '03_top_regions_volume.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 4: Regional Pricing Comparison (Top 10 Baku Regions)
# ============================================================================
print("Generating Chart 4: Regional Price Analysis...")
regional_prices = []
for region in top_regions.index:
    median_price = baku_df[baku_df['region'] == region]['price_clean'].median()
    regional_prices.append(median_price)

# Sort by price
sorted_data = sorted(zip(top_regions.index, regional_prices), key=lambda x: x[1], reverse=True)
regions, prices = zip(*sorted_data)

fig, ax = plt.subplots(figsize=(12, 7))
colors_grad = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(regions)))
bars = ax.barh(range(len(regions)), prices, color=colors_grad,
               edgecolor='black', linewidth=1.2)

# Add value labels
for i, price in enumerate(prices):
    ax.text(price, i, f'  {price/1000:.0f}K AZN', va='center', fontsize=11, fontweight='bold')

ax.set_yticks(range(len(regions)))
ax.set_yticklabels(regions, fontsize=11)
ax.set_xlabel('Median Price (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Regional Price Positioning: Səbail Commands Premium, Sabunçu Offers Value',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(charts_dir / '04_regional_pricing.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 5: Sale Price by Room Count
# ============================================================================
print("Generating Chart 5: Sale Price Analysis by Property Size...")
sale_df = df[df['announcement_type'] == 'Sale']
room_price = sale_df.groupby('room_count')['price_clean'].agg(['median', 'count'])
room_price = room_price[(room_price['count'] >= 20) & (room_price.index <= 10)]

fig, ax = plt.subplots(figsize=(12, 6))
line = ax.plot(room_price.index, room_price['median']/1000, marker='o',
               linewidth=3, markersize=10, color='#E63946', label='Median Sale Price')

# Add value labels
for x, y in zip(room_price.index, room_price['median']/1000):
    ax.text(x, y, f'{y:.0f}K', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xlabel('Number of Rooms', fontsize=12, fontweight='bold')
ax.set_ylabel('Median Sale Price (Thousand AZN)', fontsize=12, fontweight='bold')
ax.set_title('Sale Price Scaling: Clear Premium for Larger Properties',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.set_xticks(room_price.index)
plt.tight_layout()
plt.savefig(charts_dir / '05_sale_price_by_rooms.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 6: Rental Price by Room Count
# ============================================================================
print("Generating Chart 6: Rental Market Pricing...")
rent_df = df[df['announcement_type'] == 'Rent']
rent_price = rent_df.groupby('room_count')['price_clean'].agg(['median', 'count'])
rent_price = rent_price[(rent_price['count'] >= 10) & (rent_price.index <= 6)]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(rent_price.index, rent_price['median'], color='#457B9D',
              edgecolor='black', linewidth=1.2, alpha=0.85)

# Add value labels
for i, (idx, row) in enumerate(rent_price.iterrows()):
    ax.text(idx, row['median'], f'{row["median"]:.0f} AZN\n({int(row["count"])} listings)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xlabel('Number of Rooms', fontsize=12, fontweight='bold')
ax.set_ylabel('Median Monthly Rent (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Rental Market Pricing: 2-3 Room Properties Offer Best Value',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(rent_price.index)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / '06_rental_price_by_rooms.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 7: Geographic Distribution - Top Cities
# ============================================================================
print("Generating Chart 7: Geographic Market Spread...")
city_dist = df['city'].value_counts().head(10)

fig, ax = plt.subplots(figsize=(12, 7))
colors = ['#E63946' if city == 'Bakı' else '#457B9D' for city in city_dist.index]
bars = ax.barh(range(len(city_dist)), city_dist.values, color=colors,
               edgecolor='black', linewidth=1.2)

# Add value labels with percentages
for i, (city, count) in enumerate(city_dist.items()):
    pct = count / len(df) * 100
    ax.text(count, i, f'  {count:,} ({pct:.1f}%)', va='center', fontsize=11, fontweight='bold')

ax.set_yticks(range(len(city_dist)))
ax.set_yticklabels(city_dist.index, fontsize=11)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Geographic Concentration: Bakı Dominates with 80% Market Share',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(charts_dir / '07_geographic_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 8: Credit Options Analysis
# ============================================================================
print("Generating Chart 8: Financing Options...")
sale_only = df[df['announcement_type'] == 'Sale']
credit_data = {
    'Credit Available': sale_only['credit_possible'].sum(),
    'No Credit Option': (sale_only['credit_possible'] == 0).sum()
}

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(credit_data.keys(), credit_data.values(),
              color=['#06A77D', '#D62828'], edgecolor='black', linewidth=1.2)

# Add value labels
for bar in bars:
    height = bar.get_height()
    pct = height / len(sale_only) * 100
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Number of Sale Listings', fontsize=12, fontweight='bold')
ax.set_title('Financing Accessibility: 1 in 5 Properties Offer Credit Options',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / '08_credit_options.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 9: Premium Features Adoption
# ============================================================================
print("Generating Chart 9: Premium Features Analysis...")
features = {
    'VIP Listings': df['is_vip'].sum(),
    'Premium Listings': df['is_premium'].sum(),
    'Price Decreased': df['is_price_decreased'].sum()
}

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(features.keys(), features.values(),
              color=['#F77F00', '#06A77D', '#E63946'],
              edgecolor='black', linewidth=1.2)

# Add value labels
for bar in bars:
    height = bar.get_height()
    pct = height / len(df) * 100
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Premium Features & Price Dynamics: Low Adoption, Stable Pricing',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / '09_premium_features.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 10: Sale Price Distribution by Ranges
# ============================================================================
print("Generating Chart 10: Price Segmentation...")
sale_prices = sale_df['price_clean'].dropna()
sale_prices = sale_prices[(sale_prices > 0) & (sale_prices < 1000000)]

# Define price ranges
bins = [0, 50000, 100000, 150000, 200000, 300000, 500000, 1000000]
labels = ['<50K', '50-100K', '100-150K', '150-200K', '200-300K', '300-500K', '500K+']
price_ranges = pd.cut(sale_prices, bins=bins, labels=labels)
price_dist = price_ranges.value_counts().sort_index()

fig, ax = plt.subplots(figsize=(12, 6))
colors_gradient = plt.cm.viridis(np.linspace(0.2, 0.9, len(price_dist)))
bars = ax.bar(range(len(price_dist)), price_dist.values,
              color=colors_gradient, edgecolor='black', linewidth=1.2)

# Add value labels
for i, (label, count) in enumerate(price_dist.items()):
    pct = count / len(sale_prices) * 100
    ax.text(i, count, f'{count:,}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xticks(range(len(price_dist)))
ax.set_xticklabels(labels, fontsize=11)
ax.set_xlabel('Price Range (AZN)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Properties', fontsize=12, fontweight='bold')
ax.set_title('Price Segmentation: Mid-Range Properties (100-300K) Dominate Sales Market',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / '10_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 11: Sale vs Rent - Room Count Comparison
# ============================================================================
print("Generating Chart 11: Market Segment Comparison...")
sale_rooms = sale_df['room_count'].value_counts().sort_index()
rent_rooms = rent_df['room_count'].value_counts().sort_index()

# Get common room counts
common_rooms = sorted(set(sale_rooms.index) & set(rent_rooms.index))
common_rooms = [r for r in common_rooms if r <= 6]

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(common_rooms))
width = 0.35

bars1 = ax.bar(x - width/2, [sale_rooms.get(r, 0) for r in common_rooms],
               width, label='Sale', color='#2E86AB', edgecolor='black', linewidth=1.2)
bars2 = ax.bar(x + width/2, [rent_rooms.get(r, 0) for r in common_rooms],
               width, label='Rent', color='#A23B72', edgecolor='black', linewidth=1.2)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Number of Rooms', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Market Dynamics: Sale and Rental Preferences Align on 2-3 Room Properties',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels([f'{int(r)}' for r in common_rooms])
ax.legend(fontsize=11, loc='upper right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(charts_dir / '11_sale_vs_rent_rooms.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 12: Market Activity by Region (Top 5 Regions - Volume vs Price)
# ============================================================================
print("Generating Chart 12: Regional Market Performance...")
top5_regions = baku_df['region'].value_counts().head(5)
region_data = []

for region in top5_regions.index:
    region_subset = baku_df[baku_df['region'] == region]
    region_data.append({
        'region': region,
        'volume': len(region_subset),
        'median_price': region_subset['price_clean'].median()
    })

region_df = pd.DataFrame(region_data)

fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

x = np.arange(len(region_df))
bars = ax1.bar(x, region_df['volume'], alpha=0.7, color='#4361EE',
               label='Listing Volume', edgecolor='black', linewidth=1.2)
line = ax2.plot(x, region_df['median_price']/1000, marker='D', color='#E63946',
                linewidth=3, markersize=10, label='Median Price')

# Add value labels
for i, row in region_df.iterrows():
    ax1.text(i, row['volume'], f"{row['volume']:,}", ha='center', va='bottom',
             fontsize=10, fontweight='bold')
    ax2.text(i, row['median_price']/1000, f"{row['median_price']/1000:.0f}K",
             ha='center', va='bottom', fontsize=10, fontweight='bold', color='#E63946')

ax1.set_xlabel('Region', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Listings', fontsize=12, fontweight='bold', color='#4361EE')
ax2.set_ylabel('Median Price (Thousand AZN)', fontsize=12, fontweight='bold', color='#E63946')
ax1.set_xticks(x)
ax1.set_xticklabels(region_df['region'], fontsize=11)
ax1.set_title('Top 5 Regions: Volume Leaders Don\'t Always Command Price Premium',
              fontsize=14, fontweight='bold', pad=20)
ax1.tick_params(axis='y', labelcolor='#4361EE')
ax2.tick_params(axis='y', labelcolor='#E63946')
ax1.grid(axis='y', alpha=0.3)

fig.tight_layout()
plt.savefig(charts_dir / '12_regional_performance.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"\n{'='*60}")
print("SUCCESS: All charts generated successfully!")
print(f"{'='*60}")
print(f"Location: {charts_dir.absolute()}")
print(f"Total charts: 12")
print("\nGenerated visualizations:")
print("  1. Market Composition (Sale vs Rent)")
print("  2. Property Size Distribution")
print("  3. Top Regional Markets by Volume")
print("  4. Regional Price Positioning")
print("  5. Sale Price by Property Size")
print("  6. Rental Price by Property Size")
print("  7. Geographic Market Concentration")
print("  8. Credit Options Availability")
print("  9. Premium Features Adoption")
print(" 10. Price Range Segmentation")
print(" 11. Sale vs Rent Market Comparison")
print(" 12. Regional Performance Matrix")
print(f"{'='*60}")
