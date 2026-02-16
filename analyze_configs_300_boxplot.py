import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load both CSV files
df_450 = pd.read_csv('data/ftm_data_450cm.csv', comment='#')

# Create config label for each dataset
df_450['config'] = df_450['frame_count'].astype(str) + ',' + df_450['burst_period'].astype(str)

# Define config order for consistent plotting
config_order = ['16,2', '16,4', '16,6', '16,8', '16,10', '16,12', '16,14', '16,16',
                '24,2', '24,4', '24,5', '32,2', '64,2']

# ============================================================================
plt.figure(figsize=(16, 8))
sns.boxplot(x='config', y='estimated_distance_cm', data=df_450, order=config_order,
            palette='viridis', showfliers=True)
plt.ylim(0, 1400)
plt.axhline(y=450, color='red', linestyle='--', linewidth=2, label='True distance (450cm)')
plt.xlabel('Configuration (frame_count, burst_period)', fontsize=12)
plt.ylabel('Estimated Distance (cm)', fontsize=12)
plt.title('FTM Distance Estimation by Configuration - Physical Distance: 450cm', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('configs_boxplot_450cm.png', dpi=150)
plt.show()

