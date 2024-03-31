import json
import threading
import matplotlib.pyplot as plt
from datetime import datetime

def generate_and_show_graph():
    with open('exercise_data.json', 'r') as json_file:
        data = json.load(json_file)

    # Extract the relevant data
    dates = []
    reps = []

    for entry in data:
        if 'date' in entry and 'time' in entry:
            date_time_str = entry['date'] + ' ' + entry['time']
            dates.append(datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S'))
            reps.append(entry.get('total_reps', 0))

    # Create a line plot for the total reps over time
    plt.figure(figsize=(10, 6))
    plt.plot(dates, reps, label='Total Reps', marker='o')
    plt.xlabel('Date and Time')
    plt.ylabel('Total Reps')
    plt.title('Total Reps Over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Display the plot (this should be done on the main thread)
    plt.show()

# Create a thread to run the generate_and_show_graph function on the main thread
if __name__ == '__main__':
    main_thread = threading.Thread(target=generate_and_show_graph)
    main_thread.start()
