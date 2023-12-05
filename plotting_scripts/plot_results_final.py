import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'raw_data-vanilla.csv'  # Replace with your file path
data = pd.read_csv(file_path, header=2)

# Renaming columns for easier access
data.columns = [
    'Application', 'MemSize_MB', 'VanilaSnapshotSize_MB', "WarmCompute_ms",
    'VanilaVMLoad_us', 'VanilaColdStart_us', 'VanilaTotal_us',
    'AcceleratedVMLoad_us', 'AcceleratedColdStart_us', 'AcceleratedTotal_us',
    'SnapshotSize', 'CompressionRatio', 'SpeedupPercentage'
]

# Dropping unnecessary columns
data = data.drop(['MemSize_MB', 'VanilaSnapshotSize_MB', 'SnapshotSize', 
                  'SpeedupPercentage'], axis=1)

# Dropping any row where 'Application' is NaN
data = data.dropna(subset=['Application'])

# Converting time columns from microseconds to milliseconds
time_columns = [
    'VanilaVMLoad_us', 'VanilaColdStart_us', 'VanilaTotal_us',
    'AcceleratedVMLoad_us', 'AcceleratedColdStart_us', 'AcceleratedTotal_us'
]
data[time_columns] = data[time_columns].astype(int) / 1_000  # Convert to milliseconds

# Ensure 'CompressionRatio' is a float
data['CompressionRatio'] = pd.to_numeric(data['CompressionRatio'], errors='coerce').fillna(0)

# Define colors
vanila_colors = ['#1f77b4', '#2ca02c']  # Two shades for Vanila
accelerated_colors = ['#ff7f0e', '#d62728']  # Two shades for Accelerated

# Plotting
plt.figure(figsize=(12, 8))
for i, app in enumerate(data['Application']):
    # Vanila times
    vanila_total = data.loc[i, 'VanilaTotal_us']
    plt.bar(i - 0.2, data.loc[i, 'VanilaVMLoad_us'], width=0.4, color=vanila_colors[0], label='Vanila VM Load' if i == 0 else "", zorder=3)
    plt.bar(i - 0.2, data.loc[i, 'VanilaColdStart_us'], width=0.4, color=vanila_colors[1], bottom=data.loc[i, 'VanilaVMLoad_us'], 
            label='Vanila Cold Start' if i == 0 else "", zorder=3)

    # Accelerated times
    accelerated_total = data.loc[i, 'AcceleratedTotal_us']
    plt.bar(i + 0.2, data.loc[i, 'AcceleratedVMLoad_us'], width=0.4, color=accelerated_colors[0], label='Accelerated VM Load' if i == 0 else "", zorder=3)
    plt.bar(i + 0.2, data.loc[i, 'AcceleratedColdStart_us'], width=0.4, color=accelerated_colors[1], bottom=data.loc[i, 'AcceleratedVMLoad_us'], 
            label='Accelerated Cold Start' if i == 0 else "", zorder=3)

    # Adding compression ratio annotations
    compression_ratio = data.loc[i, 'CompressionRatio']
    # Positioning the annotation above the highest bar
    highest_point = max(vanila_total, accelerated_total)
    plt.text(i, highest_point, f'{compression_ratio:.2f}x', ha='center', va='bottom', zorder=4)

plt.xticks(range(len(data['Application'])), data['Application'], rotation=90)
plt.ylabel('Time (ms)')
plt.title('VM Boot and Cold Start Times for Applications (in milliseconds)')
plt.grid(axis='y', zorder=0)
plt.gca().set_axisbelow(True)
plt.legend()
plt.tight_layout()
#plt.show()  # Uncomment to display the plot in an interactive window
plt.savefig("results.png")
