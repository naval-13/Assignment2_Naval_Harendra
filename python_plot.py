import re
import matplotlib.pyplot as plt


lis = ['h1_client_bbr.txt', 'h1_client_cubic.txt', 'h1_client_reno.txt', 'h1_client_vegas.txt']

interVals = []
throughPut = []

for item in lis:
    # Read data from the file
    with open(item, 'r') as file:
        data = file.readlines()

    # Extract necessary information
    intervals = []
    throughput = []

    for line in data[6:11]:  
        print(line)
        values = re.split(r'\s+', line.strip())
        print(values)
        interval_start = float(values[2][:-1])
        interval_end = float(values[3])
        time_interval = (interval_start + interval_end) / 2.0
        throughput_value = float(values[7])
        
        intervals.append(time_interval)
        throughput.append(throughput_value)
    interVals.append(intervals)
    throughPut.append(throughput)

#plot

plt.figure(figsize=(10, 5))
lt = ['h1_client_bbr.txt', 'h1_client_cubic.txt', 'h1_client_reno.txt', 'h1_client_vegas.txt']

for i in range(len(interVals)):
    plt.plot(interVals[i], throughPut[i], marker='o', linestyle='-', label=lt[i])

plt.xlabel('Intervals (seconds)')
plt.ylabel('Bandwidth (Gbits/sec)')
plt.title('Throughput Over Time Part C.')
plt.grid(True)
plt.legend()
plt.show()