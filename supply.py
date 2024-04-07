import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt


class Customer:
    def __init__(self, env, name, manufacturer):
        self.env = env
        self.name = name
        self.manufacturer = manufacturer
        self.action = env.process(self.run())
        self.orders_placed = []

    def run(self):
        while True:
            yield self.env.timeout(random.randint(1, 5))  # Customer places order
            order_quantity = random.randint(1, 10)
            self.orders_placed.append((self.env.now, order_quantity))  # Record order
            yield self.manufacturer.order.put(
                order_quantity
            )  # Send order to manufacturer
            print(
                f"{self.name} placed an order for {order_quantity} units at {self.env.now}"
            )


class Manufacturer:
    def __init__(self, env, distributor):
        self.env = env
        self.distributor = distributor
        self.order = simpy.Store(env)
        self.action = env.process(self.process_orders())
        self.units_produced = []

    def process_orders(self):
        while True:
            order_quantity = yield self.order.get()
            self.units_produced.append(
                (self.env.now, order_quantity)
            )  # Record production
            yield self.env.timeout(random.randint(2, 5))  # Manufacturing time
            yield self.distributor.inventory.put(
                order_quantity
            )  # Send manufactured items to distributor
            print(f"Manufacturer produced {order_quantity} units at {self.env.now}")


class Distributor:
    def __init__(self, env):
        self.env = env
        self.inventory = simpy.Store(env)
        self.action = env.process(self.process_inventory())
        self.units_received = []

    def process_inventory(self):
        while True:
            order_quantity = yield self.inventory.get()
            self.units_received.append(
                (self.env.now, order_quantity)
            )  # Record inventory
            yield self.env.timeout(random.randint(1, 3))  # Transportation time
            print(f"Distributor received {order_quantity} units at {self.env.now}")


def simulate_supply_chain(env):
    distributor = Distributor(env)
    manufacturer = Manufacturer(env, distributor)
    customers = [Customer(env, f"Customer {i}", manufacturer) for i in range(3)]

    yield env.timeout(10)  # Simulation duration

    # Save data to Excel
    customer_data = pd.DataFrame(
        [(c.name, t, q) for c in customers for t, q in c.orders_placed],
        columns=["Customer", "Time", "Order Quantity"],
    )
    manufacturer_data = pd.DataFrame(
        manufacturer.units_produced, columns=["Time", "Units Produced"]
    )
    distributor_data = pd.DataFrame(
        distributor.units_received, columns=["Time", "Units Received"]
    )

    with pd.ExcelWriter("supply_chain_simulation_data.xlsx") as writer:
        customer_data.to_excel(writer, sheet_name="Customers", index=False)
        manufacturer_data.to_excel(writer, sheet_name="Manufacturer", index=False)
        distributor_data.to_excel(writer, sheet_name="Distributor", index=False)

    # Plot data
    plt.figure(figsize=(10, 6))
    plt.plot(
        manufacturer_data["Time"],
        manufacturer_data["Units Produced"],
        label="Units Produced",
        marker="o",
    )
    plt.plot(
        distributor_data["Time"],
        distributor_data["Units Received"],
        label="Units Received",
        marker="o",
    )
    plt.xlabel("Time")
    plt.ylabel("Units")
    plt.title("Supply Chain Simulation")
    plt.legend()
    plt.grid(True)
    plt.savefig("supply_chain_simulation_graph.png")
    plt.show()


# Run the simulation
env = simpy.Environment()
env.process(simulate_supply_chain(env))  # Start the simulation process
env.run(until=50)  # Run the simulation until the specified time (e.g., 50)
