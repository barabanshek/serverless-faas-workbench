import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'raw_data_reap.csv'  # Replace with your file path
data = pd.read_csv(file_path, header=2)

text_size_ultrabig = 26
text_size_big = 20
text_size_medium = 18
text_size_small = 12

# Rename benchmarks
benchark_names = {
    'fibonacci': 'fibonacci',
    'python list': 'python-list',
    'image-processing-low': 'image-\nprocessing-\nlow',
    'image-processing-hd': 'image-\nprocessing-\nhd',
    'matmull': 'matmull',
    'chameleon': 'chameleon',
    'video-processing': 'video-\nprocessing',
    'rnn-serving': 'rnn-serving',
    'ml-serving': 'ml-serving',
    'cnn-image-classification': 'cnn-image-\nclassification',
    'bfs': 'bfs',
    'dna-visualization': 'dna-\nvisualization',
    'dna-visualization-1': 'dna-\nvisualization-1',
    'resnet-img-recognition': 'resnet-img\n-recognition',
    'pagerank': 'pagerank',
    'model-training': 'model-training-\n2MB',
    'model-training-1': 'model-training-\n10MB'
}

# Renaming columns for easier access
data.columns = ['Application', 'Mem_size_MB', 'REAP_snapshot_size_B', 'Warm_compute_ms', 
                'REAP_VM_load', 'REAP_Restore', 'REAP_Cold_Start', 'REAP_Total', 
                'Accelerated_VM_load', 'Accelerated_Restore', 'Accelerated_Cold_Start', 
                'Accelerated_Total', 'Accelerated_Snapshot_Size_B', 'CompressionRatio', 
                'Speedup_over_REAP_percent', 'Restoration_Speedup_over_REAP_percent']

# Convert the relevant columns to appropriate data types
data['REAP_snapshot_size_B'] = pd.to_numeric(data['REAP_snapshot_size_B'], errors='coerce')
data['Accelerated_Snapshot_Size_B'] = pd.to_numeric(data['Accelerated_Snapshot_Size_B'], errors='coerce')
data['CompressionRatio'] = pd.to_numeric(data['CompressionRatio'], errors='coerce')
# Dropping unnecessary columns
# data = data.drop(['MemSize_MB', 'VanilaSnapshotSize_MB', 'SnapshotSize', 
                #   'SpeedupPercentage'], axis=1)

# Dropping any row where 'Application' is NaN
data = data.dropna(subset=['Application'])

# Converting time columns from microseconds to milliseconds
# time_columns = [
#     'VanilaVMLoad_us', 'VanilaColdStart_us', 'VanilaTotal_us',
#     'AcceleratedVMLoad_us', 'AcceleratedColdStart_us', 'AcceleratedTotal_us'
# ]
# data[time_columns] = data[time_columns].astype(int) / 1_000  # Convert to milliseconds

data['REAP_snapshot_size_MB'] = data['REAP_snapshot_size_B'] / (1024 * 1024)
data['Accelerated_Snapshot_Size_MB'] = data['Accelerated_Snapshot_Size_B'] / (1024 * 1024)

# Ensure 'CompressionRatio' is a float
# data['CompressionRatio'] = pd.to_numeric(data['CompressionRatio'], errors='coerce').fillna(0)

# Define colors
vanila_colors = ['gray', 'darkred']  # Two shades for Vanila
accelerated_colors = ['gray', 'darkred']  # Two shades for Accelerated

width = 0.25

# Plotting
fig, ax = plt.subplots(figsize=(24, 10))
for i, app in enumerate(data['Application']):
    # Vanila times
    # vanila_total = data.loc[i, 'REAP_snapshot_size_MB']
    # ax.bar(i - width/1.8, data.loc[i, 'REAP_snapshot_size_MB'], width=width, color=vanila_colors[0], label='REAP' if i == 0 else "", zorder=3)
    # # ax.bar(i - width/1.8, data.loc[i, 'VanilaColdStart_us'], width=width, color=vanila_colors[1], bottom=data.loc[i, 'VanilaVMLoad_us'], 
    #         # label='Baseline function invocation' if i == 0 else "", zorder=3)

    # Accelerated times
    # accelerated_total = data.loc[i, 'Accelerated_Snapshot_Size_MB']
    ax.bar(i + width/1.8, data.loc[i, 'CompressionRatio'], width=width, color=accelerated_colors[1], label='Sabre' if i == 0 else "", zorder=3, hatch='')
    # ax.bar(i + width/1.8, data.loc[i, 'AcceleratedColdStart_us'], width=width, color=accelerated_colors[1], bottom=data.loc[i, 'AcceleratedVMLoad_us'], 
            # label='Our function invocation' if i == 0 else "", zorder=3, hatch='//')

    # # Adding compression ratio annotations
    # compression_ratio = data.loc[i, 'CompressionRatio']
    # # Positioning the annotation above the highest bar
    # highest_point = max(vanila_total, accelerated_total)
    # ax.text(i, highest_point, f'{compression_ratio:.2f}x', ha='center', va='bottom', zorder=4, fontsize=text_size_big, color='black')

b_names = [benchark_names[b] for b in data['Application']]
ax.set_xticks(range(len(data['Application'])), b_names, rotation=45, fontsize=text_size_big)
ax.set_ylabel('Compression Ratio', fontsize=text_size_ultrabig)
# ax.set_yticks(range(0, 6000, 1000))
for label in ax.get_yticklabels():
    label.set_fontsize(text_size_ultrabig)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
# plt.title('VM Boot and Cold Start Times for Applications (in milliseconds)')
plt.grid(axis='y', zorder=0)
plt.gca().set_axisbelow(True)
plt.legend(ncol=1, fontsize=text_size_ultrabig)
plt.tight_layout()
# plt.show()  # Uncomment to display the plot in an interactive window
plt.savefig("snapshot_size_results_only.png")
plt.savefig("snapshot_size_results_only.pdf", format="pdf", bbox_inches="tight")
