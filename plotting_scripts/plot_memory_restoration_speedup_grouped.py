import pandas as pd
import matplotlib.pyplot as plt

# Load the data
file_path = 'raw_data_reap.csv'  # Replace with your file path
data = pd.read_csv(file_path, header=1)  # Adjust the header row if needed

# Rename columns for easier access (adjust these based on your file's actual headers)
data.columns = ['Application', 'Mem_size_MB', 'REAP_snapshot_size_B', 'Warm_compute_ms', 
                'REAP_VM_load', 'REAP_Restore', 'REAP_Cold_Start', 'REAP_Total', 
                'Accelerated_VM_load', 'Accelerated_Restore', 'Accelerated_Cold_Start', 
                'Accelerated_Total', 'Accelerated_Snapshot_Size_B', 'Compression_Ratio', 
                'Speedup_over_REAP_percent', 'Restoration_Speedup_over_REAP_percent']

# Convert the relevant columns to appropriate data types
data['REAP_Restore'] = pd.to_numeric(data['REAP_Restore'], errors='coerce')/1_000
data['Accelerated_Restore'] = pd.to_numeric(data['Accelerated_Restore'], errors='coerce')/1_000
data['Restoration_Speedup_over_REAP_percent'] = pd.to_numeric(data['Restoration_Speedup_over_REAP_percent'], errors='coerce')

# Drop rows with NaN values in the columns of interest
data.dropna(subset=['Application', 'REAP_Restore', 'Accelerated_Restore', 'Restoration_Speedup_over_REAP_percent'], inplace=True)

# Splitting data into two groups
selected_apps = ['python list', 'dna-visualization-1', "img-processing-hd", "model-training", "model-training-1"]
group1 = data[data['Application'].isin(selected_apps)]
group2 = data[~data['Application'].isin(selected_apps)]

# Function to plot a group
def plot_group(group, ax, title):
    applications = group['Application']
    reap_restore = group['REAP_Restore']
    accelerated_restore = group['Accelerated_Restore']
    restoration_speedup = group['Restoration_Speedup_over_REAP_percent']

    bar_width = 0.35
    index = range(len(applications))

    
    bar1 = ax.bar(index, reap_restore, bar_width, label='REAP Restore Time (ms)')
    bar2 = ax.bar([i + bar_width for i in index], accelerated_restore, bar_width, label='Accelerated Restore Time (ms)')

    # Adding a single annotation for restoration speed-up
    for idx in range(len(applications)):
        max_height = max(reap_restore.iloc[idx], accelerated_restore.iloc[idx])
        ax.text(idx + bar_width / 2, max_height, f'{restoration_speedup.iloc[idx]:.2f}%', 
                ha='center', va='bottom')

    ax.set_xlabel('Applications')
    ax.set_ylabel('Restore Time (ms)')
    ax.set_title(title)
    ax.set_xticks([r + bar_width / 2 for r in range(len(applications))])
    ax.set_xticklabels(applications, rotation=45)
    ax.legend()

# Plotting in subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

plot_group(group1, ax1, 'Selected Applications (python-list and dna-visualization-1)')
plot_group(group2, ax2, 'Other Applications')

plt.tight_layout()
plt.show()
