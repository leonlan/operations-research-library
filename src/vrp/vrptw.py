from itertools import product

import docplex.cp.model as docp
import vrplib


def vehicle_routing_problem_time_windows() -> docp.CpoModel:
    """
    Creates a CP model for the Vehicle Routing Problem with Time Windows
    (VRPTW) based on the formulation presented in [Laborie2018].

    References
    ----------
    [Laborie2018]: https://doi.org/10.1007/s10601-018-9281-x
    Laborie, P., Rogerie, J., Shaw, P., & Vilím, P. (2018).
    IBM ILOG CP optimizer for scheduling. Constraints, 23(2), 210–250.
    """
    # TODO figure out how the referencing works in mkdocstrings
    model = docp.CpoModel()

    # TODO transform the data to work with the model
    data = vrplib.read("instances/R101.txt")

    visits = create_visit_variables(model, data)
    vvisits = create_vehicle_visit_variables(model, data)
    routes = create_route_variables(model, data, vvisits)

    no_overlap_between_visits(model, data, routes)
    routes_start_and_end_at_depot(model, data, vvisits, routes)
    assign_each_client_to_one_vehicle(model, data, visits, vvisits)

    return model


def create_visit_variables(model, data):
    """
    Creates the visit variables $T_{i}$ for each client $i \\in N$.

    A visit variable is an interval variable that represents the time that
    is spent at a client location to perform the service. This does not
    include the travel time to the client location.
    """
    visits = {}

    for client in range(1, data["dimnesion"]):
        size = data["service_time"][client]
        visits[client] = model.interval_var(name=f"T_{client}", size=size)

    return visits


def create_vehicle_visit_variables(model, data):
    vvisits = {}

    for vehicle, client in product(
        range(data["num_vehicles"]), range(1, data["dimension"])
    ):
        var = model.interval_var(name=f"T_{vehicle}_{client}")
        vvisits[(vehicle, client)] = var

    return vvisits


def create_route_variables(model, data, vvisits):
    routes = {}

    for vehicle in range(data["num_vehicles"]):
        intervals = [
            vvisits[(vehicle, client)]
            for client in range(1, data["dimension"])
        ]
        routes[vehicle] = model.sequence_var(intervals, name=f"R_{vehicle}")

    return routes


def no_overlap_between_visits(model, data, routes):
    """
    This constraint ensures that no visits overlap in time, and that
    travel time between visits is respected.

    \\begin{equation}
        \\texttt{NoOverlap}(R_{k}, D),
        \\quad \\forall k \\in K,
    \\end{equation}

    where $D$ is the matrix of travel times between visits.
    """
    for vehicle in range(data["num_vehicles"]):
        model.add(model.no_overlap(routes[vehicle], data["edge_weights"]))


def routes_start_and_end_at_depot(model, data, vvisits, routes):
    """
    This constraint ensures that each route starts and ends at the depot.

    \\begin{align}
        \\texttt{PresenceOf}(V_{0k}) = 1,
        &\\quad \\forall k \\in K, \\\\
        \\texttt{PresenceOf}(V_{n+1,k}) = 1,
        &\\quad \\forall k \\in K, \\\\
        \\texttt{First}(R_{k}, V_{0k}),
        &\\quad \\forall k \\in K, \\\\
        \\texttt{Last}(R_{k}, V_{n+1,k}),
        &\\quad \\forall k \\in K.
    \\end{align}

    """
    for vehicle in range(data["num_vehicles"]):
        start_depot = 0
        first_visit = vvisits[(vehicle, start_depot)]

        cons = model.presence_of(first_visit) == 1
        model.add(cons)

        end_depot = len(data["dimension"]) + 1
        last_visit = vvisits[(vehicle, end_depot)]

        cons = model.presence_of(last_visit) == 1
        model.add(cons)

        cons = model.first(routes[vehicle], first_visit)
        model.add(cons)

        cons = model.last(routes[vehicle], last_visit)
        model.add(cons)


def assign_each_client_to_one_vehicle(model, data, visit, vvisits):
    """
    Each client must be assigned to exactly one vehicle.

    \\begin{equation}
        \\texttt{Alternative}(V_{i},\\{ V_{ik} : k \\in K \\}),
        \\quad \\forall i \\in N.
    \\end{equation}
    """
    for i in range(1, data["dimension"]):
        optional = [vvisits[(i, k)] for k in data.vehicles]
        model.add(model.alternative(visit[i], optional))
