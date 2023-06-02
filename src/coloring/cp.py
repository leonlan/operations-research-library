import docplex.cp.model as docp
from ProblemData import ProblemData


def cp(data: ProblemData):
    """
    Creates a CP model for the graph coloring problem.
    """
    model = docp.CpoModel()

    colors = [
        model.integer_var(0, data.num_nodes - 1, name=f"C_{i}")
        for i in data.nodes
    ]
    different_colors_adjacent_nodes(data, model, colors)

    model.minimize(model.max(colors))

    return model


def different_colors_adjacent_nodes(data, model, colors):
    """
    For any given node, all its adjacent nodes must have different colors.
    This can be implemented using the all different constraint.

    \\begin{equation}
        \\texttt{AllDifferent}(\\{C_j : (i, j) \\in E \\}),
        \\quad \\forall i \\in V.
    \\end{equation}
    """
    for i in data.nodes:
        cons = model.all_diff([colors[j] for j in data.adjacency_list[i]])
        model.add(cons)
