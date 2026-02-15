import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load both CSV files
df_150 = pd.read_csv('data/ftm_data_150cm.csv', comment='#') 
df_300 = pd.read_csv('data/ftm_data_300cm.csv', comment='#') 
df_450 = pd.read_csv('data/ftm_data_450cm.csv', comment='#')
df_600 = pd.read_csv('data/ftm_data_600cm.csv', comment='#')
df_750 = pd.read_csv('data/ftm_data_750cm.csv', comment='#')

# Create config label for each dataset
df_150['config'] = df_150['frame_count'].astype(str) + ',' + df_150['burst_period'].astype(str)
df_300['config'] = df_300['frame_count'].astype(str) + ',' + df_300['burst_period'].astype(str)
df_450['config'] = df_450['frame_count'].astype(str) + ',' + df_450['burst_period'].astype(str)
df_600['config'] = df_600['frame_count'].astype(str) + ',' + df_600['burst_period'].astype(str)
df_750['config'] = df_750['frame_count'].astype(str) + ',' + df_750['burst_period'].astype(str)

# Define config order for consistent plotting
config_order = ['16,2', '16,4', '16,6', '16,8', '16,10', '16,12', '16,14', '16,16',
                '24,2', '24,4', '24,5', '32,2', '64,2']


# ============================================================================
# FIGURE 1: Boxplot comparison of all configs - 150cm
# ============================================================================
plt.figure(figsize=(16, 8))
sns.boxplot(x='config', y='estimated_distance_cm', data=df_150, order=config_order, 
            palette='viridis', showfliers=True)  
plt.axhline(y=150, color='red', linestyle='--', linewidth=2, label='True distance (150cm)')
plt.xlabel('Configuration (frame_count, burst_period)', fontsize=12)
plt.ylabel('Estimated Distance (cm)', fontsize=12)
plt.title('FTM Distance Estimation by Configuration - Physical Distance: 150cm', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('figures/configs_boxplot_150cm.png', dpi=150)
plt.show()

# ============================================================================
# FIGURE 2: Boxplot comparison of all configs - 300cm
# ============================================================================
plt.figure(figsize=(16, 8))
sns.boxplot(x='config', y='estimated_distance_cm', data=df_300, order=config_order,
            palette='viridis', showfliers=True)
plt.axhline(y=300, color='red', linestyle='--', linewidth=2, label='True distance (300cm)')
plt.xlabel('Configuration (frame_count, burst_period)', fontsize=12)
plt.ylabel('Estimated Distance (cm)', fontsize=12)
plt.title('FTM Distance Estimation by Configuration - Physical Distance: 300cm', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('figures/configs_boxplot_300cm.png', dpi=150)
plt.show()

# ============================================================================
# FIGURE 3: Boxplot comparison of all configs - 450cm
# ============================================================================
plt.figure(figsize=(16, 8))
sns.boxplot(x='config', y='estimated_distance_cm', data=df_450, order=config_order, 
            palette='viridis', showfliers=True)  
plt.axhline(y=450, color='red', linestyle='--', linewidth=2, label='True distance (450cm)')
plt.xlabel('Configuration (frame_count, burst_period)', fontsize=12)
plt.ylabel('Estimated Distance (cm)', fontsize=12)
plt.title('FTM Distance Estimation by Configuration - Physical Distance: 450cm', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('figures/configs_boxplot_450cm.png', dpi=150)
plt.show()

# ============================================================================
# FIGURE 4: Boxplot comparison of all configs - 600cm
# ============================================================================
plt.figure(figsize=(16, 8))
sns.boxplot(x='config', y='estimated_distance_cm', data=df_600, order=config_order,
            palette='viridis', showfliers=True)
plt.axhline(y=600, color='red', linestyle='--', linewidth=2, label='True distance (600cm)')
plt.xlabel('Configuration (frame_count, burst_period)', fontsize=12)
plt.ylabel('Estimated Distance (cm)', fontsize=12)
plt.title('FTM Distance Estimation by Configuration - Physical Distance: 600cm', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('figures/configs_boxplot_600cm.png', dpi=150)
plt.show()

# ============================================================================
# FIGURE 5: Boxplot comparison of all configs - 750cm
# ============================================================================
plt.figure(figsize=(16, 8))
sns.boxplot(x='config', y='estimated_distance_cm', data=df_750, order=config_order, 
            palette='viridis', showfliers=True) 
plt.axhline(y=750, color='red', linestyle='--', linewidth=2, label='True distance (750cm)')
plt.xlabel('Configuration (frame_count, burst_period)', fontsize=12)
plt.ylabel('Estimated Distance (cm)', fontsize=12)
plt.title('FTM Distance Estimation by Configuration - Physical Distance: 750cm', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('figures/configs_boxplot_750cm.png', dpi=150)
plt.show()





# ============================================================================
# FIGURE 6: Violin plot (shows distribution shape better)
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

sns.violinplot(x='config', y='estimated_distance_cm', data=df_150, order=config_order,
               palette='Blues', ax=axes[0], inner='quartile')
axes[0].axhline(y=150, color='red', linestyle='--', linewidth=2)
axes[0].set_xlabel('Configuration (frame_count, burst_period)')
axes[0].set_ylabel('Estimated Distance (cm)')
axes[0].set_title('150cm - Distribution by Configuration')
axes[0].tick_params(axis='x', rotation=45)

sns.violinplot(x='config', y='estimated_distance_cm', data=df_300, order=config_order,
               palette='Oranges', ax=axes[1], inner='quartile')
axes[1].axhline(y=300, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Configuration (frame_count, burst_period)')
axes[1].set_ylabel('Estimated Distance (cm)')
axes[1].set_title('300cm - Distribution by Configuration')
axes[1].tick_params(axis='x', rotation=45)

sns.violinplot(x='config', y='estimated_distance_cm', data=df_450, order=config_order,
               palette='Blues', ax=axes[0], inner='quartile')
axes[0].axhline(y=450, color='red', linestyle='--', linewidth=2)
axes[0].set_xlabel('Configuration (frame_count, burst_period)')
axes[0].set_ylabel('Estimated Distance (cm)')
axes[0].set_title('450cm - Distribution by Configuration')
axes[0].tick_params(axis='x', rotation=45)

sns.violinplot(x='config', y='estimated_distance_cm', data=df_600, order=config_order,
               palette='Oranges', ax=axes[1], inner='quartile')
axes[1].axhline(y=600, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Configuration (frame_count, burst_period)')
axes[1].set_ylabel('Estimated Distance (cm)')
axes[1].set_title('600cm - Distribution by Configuration')
axes[1].tick_params(axis='x', rotation=45)

sns.violinplot(x='config', y='estimated_distance_cm', data=df_750, order=config_order,
               palette='Blues', ax=axes[0], inner='quartile')
axes[0].axhline(y=750, color='red', linestyle='--', linewidth=2)
axes[0].set_xlabel('Configuration (frame_count, burst_period)')
axes[0].set_ylabel('Estimated Distance (cm)')
axes[0].set_title('750cm - Distribution by Configuration')
axes[0].tick_params(axis='x', rotation=45)

sns.violinplot(x='config', y='estimated_distance_cm', data=df_300, order=config_order,
               palette='Oranges', ax=axes[1], inner='quartile')
axes[1].axhline(y=300, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Configuration (frame_count, burst_period)')
axes[1].set_ylabel('Estimated Distance (cm)')
axes[1].set_title('300cm - Distribution by Configuration')
axes[1].tick_params(axis='x', rotation=45)


plt.tight_layout()
plt.savefig('figures/configs_violin_both.png', dpi=150)
plt.show()

# ============================================================================
# STATISTICS TABLE: Compare configs
# ============================================================================
def calc_stats(df, true_distance):
    stats = df.groupby('config').agg({
        'estimated_distance_cm': ['count', 'mean', 'median', 'std', 'min', 'max']
    }).round(2)
    stats.columns = ['count', 'mean', 'median', 'std', 'min', 'max']
    stats['error_from_true'] = (stats['median'] - true_distance).round(2)
    stats['abs_error'] = stats['error_from_true'].abs()
    stats = stats.sort_values('abs_error')
    return stats

print("\n" + "="*80)
print("STATISTICS FOR 150cm MEASUREMENTS")
print("="*80)
stats_150 = calc_stats(df_150, 150)
print(stats_150.to_string())
print(f"\nBest config for 150cm: {stats_150.index[0]} (median error: {stats_150['error_from_true'].iloc[0]}cm)")

print("\n" + "="*80)
print("STATISTICS FOR 300cm MEASUREMENTS")
print("="*80)
stats_300 = calc_stats(df_300, 300)
print(stats_300.to_string())
print(f"\nBest config for 300cm: {stats_300.index[0]} (median error: {stats_300['error_from_true'].iloc[0]}cm)")

print("\n" + "="*80)
print("STATISTICS FOR 450cm MEASUREMENTS")
print("="*80)
stats_450 = calc_stats(df_450, 450)
print(stats_450.to_string())
print(f"\nBest config for 450cm: {stats_450.index[0]} (median error: {stats_450['error_from_true'].iloc[0]}cm)")

print("\n" + "="*80)
print("STATISTICS FOR 600cm MEASUREMENTS")
print("="*80)
stats_600 = calc_stats(df_600, 600)
print(stats_600.to_string())
print(f"\nBest config for 600cm: {stats_600.index[0]} (median error: {stats_600['error_from_true'].iloc[0]}cm)")

print("\n" + "="*80)
print("STATISTICS FOR 750cm MEASUREMENTS")
print("="*80)
stats_750 = calc_stats(df_750, 750)
print(stats_750.to_string())
print(f"\nBest config for 750cm: {stats_750.index[0]} (median error: {stats_750['error_from_true'].iloc[0]}cm)")



# ============================================================================
# FIGURE 4: Error bar plot (median ± std)
# ============================================================================
#fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# 150cm
#stats_150_ordered = df_150.groupby('config').agg({'estimated_distance_cm': ['median', 'std']})
#stats_150_ordered.columns = ['median', 'std']
#stats_150_ordered = stats_150_ordered.reindex(config_order)

#axes[0].errorbar(range(len(config_order)), stats_150_ordered['median'], 
#                 yerr=stats_150_ordered['std'], fmt='o', capsize=5, capthick=2,
#                 color='blue', ecolor='lightblue', markersize=8)
#axes[0].axhline(y=150, color='red', linestyle='--', linewidth=2, label='True distance')
#axes[0].set_xticks(range(len(config_order)))
#axes[0].set_xticklabels(config_order, rotation=45, ha='right')
#axes[0].set_xlabel('Configuration (frame_count, burst_period)')
#axes[0].set_ylabel('Estimated Distance (cm)')
#axes[0].set_title('150cm - Median ± Std Dev by Configuration')
#axes[0].legend()
#axes[0].grid(True, alpha=0.3)

# 300cm
#stats_300_ordered = df_300.groupby('config').agg({'estimated_distance_cm': ['median', 'std']})
#stats_300_ordered.columns = ['median', 'std']
#stats_300_ordered = stats_300_ordered.reindex(config_order)

#axes[1].errorbar(range(len(config_order)), stats_300_ordered['median'], 
#                 yerr=stats_300_ordered['std'], fmt='o', capsize=5, capthick=2,
#                 color='orange', ecolor='moccasin', markersize=8)
#axes[1].axhline(y=300, color='red', linestyle='--', linewidth=2, label='True distance')
#axes[1].set_xticks(range(len(config_order)))
#axes[1].set_xticklabels(config_order, rotation=45, ha='right')
#axes[1].set_xlabel('Configuration (frame_count, burst_period)')
#axes[1].set_ylabel('Estimated Distance (cm)')
#axes[1].set_title('300cm - Median ± Std Dev by Configuration')
#axes[1].legend()
#axes[1].grid(True, alpha=0.3)

# 450cm
#stats_450_ordered = df_450.groupby('config').agg({'estimated_distance_cm': ['median', 'std']})
#stats_450_ordered.columns = ['median', 'std']
#stats_450_ordered = stats_450_ordered.reindex(config_order)

#axes[0].errorbar(range(len(config_order)), stats_450_ordered['median'], 
#                 yerr=stats_450_ordered['std'], fmt='o', capsize=5, capthick=2,
#                 color='blue', ecolor='lightblue', markersize=8)
#axes[0].axhline(y=450, color='red', linestyle='--', linewidth=2, label='True distance')
#axes[0].set_xticks(range(len(config_order)))
#axes[0].set_xticklabels(config_order, rotation=45, ha='right')
#axes[0].set_xlabel('Configuration (frame_count, burst_period)')
#axes[0].set_ylabel('Estimated Distance (cm)')
#axes[0].set_title('450cm - Median ± Std Dev by Configuration')
#axes[0].legend()
#axes[0].grid(True, alpha=0.3)

# 600cm
#stats_600_ordered = df_600.groupby('config').agg({'estimated_distance_cm': ['median', 'std']})
#stats_600_ordered.columns = ['median', 'std']
#stats_600_ordered = stats_600_ordered.reindex(config_order)

#axes[1].errorbar(range(len(config_order)), stats_600_ordered['median'], 
 #                yerr=stats_600_ordered['std'], fmt='o', capsize=5, capthick=2,
  #               color='orange', ecolor='moccasin', markersize=8)
#axes[1].axhline(y=600, color='red', linestyle='--', linewidth=2, label='True distance')
#axes[1].set_xticks(range(len(config_order)))
#axes[1].set_xticklabels(config_order, rotation=45, ha='right')
#axes[1].set_xlabel('Configuration (frame_count, burst_period)')
#axes[1].set_ylabel('Estimated Distance (cm)')
#axes[1].set_title('600cm - Median ± Std Dev by Configuration')
#axes[1].legend()
#axes[1].grid(True, alpha=0.3)

# 750cm
#stats_750_ordered = df_750.groupby('config').agg({'estimated_distance_cm': ['median', 'std']})
#stats_750_ordered.columns = ['median', 'std']
#stats_750_ordered = stats_750_ordered.reindex(config_order)

#axes[1].errorbar(range(len(config_order)), stats_750_ordered['median'], 
 #                yerr=stats_750_ordered['std'], fmt='o', capsize=5, capthick=2,
#                 color='orange', ecolor='moccasin', markersize=8)
#axes[1].axhline(y=750, color='red', linestyle='--', linewidth=2, label='True distance')
#axes[1].set_xticks(range(len(config_order)))
#axes[1].set_xticklabels(config_order, rotation=45, ha='right')
#axes[1].set_xlabel('Configuration (frame_count, burst_period)')
#axes[1].set_ylabel('Estimated Distance (cm)')
#axes[1].set_title('750cm - Median ± Std Dev by Configuration')
#axes[1].legend()
#axes[1].grid(True, alpha=0.3)

#plt.tight_layout()
#plt.savefig('configs_errorbar_both.png', dpi=150)
#plt.show()

# ============================================================================
# FIGURE 5: Heatmap of median error by frame_count vs burst_period
# ============================================================================
#def create_error_heatmap(df, true_distance, ax, title):
#    pivot = df.groupby(['frame_count', 'burst_period'])['estimated_distance_cm'].median().unstack()
#    error_pivot = pivot - true_distance
#    
#    sns.heatmap(error_pivot, annot=True, fmt='.0f', cmap='RdYlGn_r', center=0,
#                ax=ax, cbar_kws={'label': 'Median Error (cm)'})
#    ax.set_title(title)
#    ax.set_xlabel('Burst Period')
#    ax.set_ylabel('Frame Count')

#fig, axes = plt.subplots(1, 2, figsize=(16, 6))
#create_error_heatmap(df_150, 150, axes[0], 'Median Error at 150cm')
#create_error_heatmap(df_300, 300, axes[1], 'Median Error at 300cm')
#plt.tight_layout()
#plt.savefig('configs_heatmap_error.png', dpi=150)
#plt.show()

print("\n" + "="*80)
print("Plots saved:")
print("  - configs_boxplot_150cm.png")
print("  - configs_boxplot_300cm.png")
print("  - configs_violin_both.png")
print("  - configs_errorbar_both.png")
print("  - configs_heatmap_error.png")
print("="*80)
