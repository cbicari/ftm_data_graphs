import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load both CSV files
df_150 = pd.read_csv('cleaned_ftm_data_150cm.csv')
df_300 = pd.read_csv('cleaned_ftm_data_300cm.csv')

# Combine into one dataframe
df = pd.concat([df_150, df_300], ignore_index=True)

# Now you have all 26000 samples in one dataframe
print(f"Total samples: {len(df)}")
print(df.groupby('physical_distance_cm').size())

# Example: Compare accuracy at both distances
plt.figure(figsize=(12, 6))
sns.boxplot(x='physical_distance_cm', y='estimated_distance_cm', data=df)
plt.axhline(y=150, color='blue', linestyle='--', alpha=0.5, label='True 150cm')
plt.axhline(y=300, color='orange', linestyle='--', alpha=0.5, label='True 300cm')
plt.title('FTM Distance Estimation Accuracy')
plt.legend()
plt.savefig('comparison.png', dpi=150)
plt.show()

# Example: Scatter plot colored by true distance
plt.figure(figsize=(12, 6))
colors = {150: 'blue', 300: 'orange'}
for dist in [150, 300]:
    subset = df[df['physical_distance_cm'] == dist]
    plt.scatter(subset['elapsed_ms'], subset['estimated_distance_cm'], 
                alpha=0.2, s=5, c=colors[dist], label=f'{dist}cm')
    plt.axhline(y=dist, color=colors[dist], linestyle='--', alpha=0.7)

plt.xlabel('Elapsed Time (ms)')
plt.ylabel('Estimated Distance (cm)')
plt.title('FTM Measurements at 150cm and 300cm')
plt.legend()
plt.savefig('scatter_both.png', dpi=150)
plt.show()
