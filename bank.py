import simpy
import random
import matplotlib.pyplot as plt

# Parameters
RANDOM_SEED = 42
NUM_TELLERS = 3  # Number of tellers in the bank
INTER_ARRIVAL_TIME = 5  # Average time between customer arrivals
SERVICE_TIME = 10  # Average service time for each customer
SIM_TIME = 50  # Simulation time in minutes

# Lists to track metrics
wait_times = []
queue_lengths = []
teller_utilization = []
total_customers = 0

def customer(env, name, bank):
    """Customer arrives, waits in line if no teller is available, and gets served."""
    arrival_time = env.now
    print(f'{name} arrives at the bank at time {arrival_time:.2f}')

    with bank.request() as request:
        yield request
        # Customer has to wait for service if no teller is available
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)
        
        print(f'{name} starts service at time {env.now:.2f}, waited for {wait_time:.2f}')
        yield env.timeout(random.expovariate(1.0 / SERVICE_TIME))  # Service time
        
        print(f'{name} finishes service at time {env.now:.2f}')

def customer_arrivals(env, bank):
    """Generate customers arriving at the bank randomly."""
    global total_customers
    while True:
        inter_arrival = random.expovariate(1.0 / INTER_ARRIVAL_TIME)
        yield env.timeout(inter_arrival)
        total_customers += 1
        env.process(customer(env, f'Customer {total_customers}', bank))
        # Track queue length
        queue_lengths.append(len(bank.queue))

def monitor_teller_utilization(env, bank):
    """Monitor the utilization of tellers over time."""
    while True:
        # Calculate the number of busy tellers
        busy_tellers = NUM_TELLERS - bank.count
        utilization = busy_tellers / NUM_TELLERS
        teller_utilization.append(utilization)
        yield env.timeout(1)

# Simulation setup
def run_simulation():
    global wait_times, queue_lengths, teller_utilization
    random.seed(RANDOM_SEED)
    
    # Reset metrics
    wait_times, queue_lengths, teller_utilization = [], [], []
    
    # Create environment and bank resources (tellers)
    env = simpy.Environment()
    bank = simpy.Resource(env, capacity=NUM_TELLERS)
    
    # Start processes
    env.process(customer_arrivals(env, bank))
    env.process(monitor_teller_utilization(env, bank))
    
    # Run the simulation
    env.run(until=SIM_TIME)

# Run the simulation
run_simulation()

# Results and Analysis

# Average wait time
avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
print(f'Average wait time: {avg_wait_time:.2f} minutes')

# Average queue length
avg_queue_length = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0
print(f'Average queue length: {avg_queue_length:.2f} customers')

# Average teller utilization
avg_teller_utilization = sum(teller_utilization) / len(teller_utilization) if teller_utilization else 0
print(f'Teller utilization: {avg_teller_utilization:.2%}')

# Visualization of results
plt.figure(figsize=(12, 8))

# Plot queue length over time
plt.subplot(2, 1, 1)
plt.plot(queue_lengths, label='Queue Length')
plt.title('Queue Length Over Time')
plt.xlabel('Time (minutes)')
plt.ylabel('Number of Customers in Queue')
plt.legend()

# Plot teller utilization over time
plt.subplot(2, 1, 2)
plt.plot(teller_utilization, label='Teller Utilization')
plt.title('Teller Utilization Over Time')
plt.xlabel('Time (minutes)')
plt.ylabel('Utilization (%)')
plt.legend()

plt.tight_layout()
plt.show()
