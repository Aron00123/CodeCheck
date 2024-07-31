import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = [
        # fmt: off
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
        # fmt: on
    ]
    # Coordinates of the nodes (for visualization)
    data["locations"] = [
        [456, 320], [228, 0], [912, 0], [0, 80], [114, 80], [570, 160],
        [798, 160], [342, 240], [684, 240], [570, 400], [912, 400],
        [114, 480], [228, 480], [342, 560], [684, 560], [0, 640], [798, 640]
    ]
    data["demands"] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    data["vehicle_capacities"] = [15, 15, 15, 15]
    data["num_vehicles"] = 4
    data["depot"] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    routes = []
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        routes.append(route)
        # print(routes)
    return routes


def animate_solution(data, manager, routing, solution):
    routes = print_solution(data, manager, routing, solution)
    fig, ax = plt.subplots()
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 700)

    for location in data["locations"]:
        ax.plot(location[0], location[1], 'ko')

    colors = ['r', 'g', 'b', 'y']
    lines = [ax.plot([], [], color=colors[i])[0] for i in range(len(routes))]
    points = [ax.plot([], [], 'o', color=colors[i])[0] for i in range(len(routes))]

    def init():
        for line in lines:
            line.set_data([], [])
        for point in points:
            point.set_data([], [])
        return lines + points

    # def update(frame):
    #     for i, route in enumerate(routes):
    #         if frame < len(route):
    #             xdata = [data["locations"][node][0] for node in route[:frame + 1]]
    #             ydata = [data["locations"][node][1] for node in route[:frame + 1]]
    #             lines[i].set_data(xdata, ydata)
    #             points[i].set_data([data["locations"][route[frame]][0]], [data["locations"][route[frame]][1]])
    #     return lines + points

    num_frames = 120

    def update(frame):
        for i, route in enumerate(routes):
            route_length = len(route)
            total_frames_per_route = num_frames / route_length

            if frame < (total_frames_per_route * (route_length - 1)):
                start_node_index = int(frame // total_frames_per_route)
                t = (frame % total_frames_per_route) / total_frames_per_route
                
                start_node = route[start_node_index]
                end_node = route[start_node_index + 1]
                
                xdata = [data["locations"][node][0] for node in route[:start_node_index + 1]]
                ydata = [data["locations"][node][1] for node in route[:start_node_index + 1]]
                
                xdata.append(data["locations"][start_node][0] * (1 - t) + data["locations"][end_node][0] * t)
                ydata.append(data["locations"][start_node][1] * (1 - t) + data["locations"][end_node][1] * t)
                
                lines[i].set_data(xdata, ydata)
                points[i].set_data([xdata[-1]], [ydata[-1]])
            else:
                xdata = [data["locations"][node][0] for node in route]
                ydata = [data["locations"][node][1] for node in route]
                lines[i].set_data(xdata, ydata)
                points[i].set_data([xdata[-1]], [ydata[-1]])
        return lines + points

    ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=1000 / 60.0,
                                  init_func=init, blit=True, repeat=False)
    plt.show()


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data["vehicle_capacities"],  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        animate_solution(data, manager, routing, solution)


if __name__ == "__main__":
    main()
