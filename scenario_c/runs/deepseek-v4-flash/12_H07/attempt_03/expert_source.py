import json
import gurobipy as gp
from gurobipy import GRB


def main():
    suppliers = ["A", "B", "C", "D", "E", "F"]
    components = ["C1", "C2", "C3"]

    demand = {"C1": 80, "C2": 70, "C3": 60}
    fixed_cost = {"A": 120, "B": 140, "C": 100, "D": 150, "E": 90, "F": 110}
    capacity = {"A": 100, "B": 110, "C": 90, "D": 120, "E": 80, "F": 95}
    risk = {"A": 2, "B": 3, "C": 1, "D": 4, "E": 2, "F": 3}

    unit_cost = {
        ("A", "C1"): 9, ("A", "C2"): 12, ("A", "C3"): 11,
        ("B", "C1"): 10, ("B", "C2"): 9, ("B", "C3"): 12,
        ("C", "C1"): 11, ("C", "C2"): 10, ("C", "C3"): 9,
        ("D", "C2"): 11, ("D", "C3"): 10,
        ("E", "C1"): 12, ("E", "C2"): 8,
        ("F", "C1"): 10, ("F", "C3"): 8,
    }

    quality = {
        ("A", "C1"): 96, ("A", "C2"): 94, ("A", "C3"): 95,
        ("B", "C1"): 93, ("B", "C2"): 97, ("B", "C3"): 92,
        ("C", "C1"): 98, ("C", "C2"): 95, ("C", "C3"): 96,
        ("D", "C2"): 94, ("D", "C3"): 93,
        ("E", "C1"): 97, ("E", "C2"): 98,
        ("F", "C1"): 94, ("F", "C3"): 98,
    }

    available = [(i, j) for i in suppliers for j in components if (i, j) in unit_cost]

    model = gp.Model("sourcing_multicomponent")
    model.Params.OutputFlag = 0

    y = {i: model.addVar(vtype=GRB.BINARY, name=f"y_{i}") for i in suppliers}

    x = {}
    z = {}
    for i, j in available:
        x[i, j] = model.addVar(lb=0, vtype=GRB.INTEGER, name=f"x_{i}_{j}")
        z[i, j] = model.addVar(vtype=GRB.BINARY, name=f"z_{i}_{j}")

    model.update()

    model.setObjective(
        gp.quicksum(fixed_cost[i] * y[i] for i in suppliers)
        + gp.quicksum(unit_cost[i, j] * x[i, j] for (i, j) in available),
        GRB.MINIMIZE,
    )

    for j in components:
        model.addConstr(
            gp.quicksum(x[i, j] for i in suppliers if (i, j) in x) == demand[j],
            name=f"demand_{j}",
        )

    for j in components:
        model.addConstr(
            gp.quicksum(
                quality[i, j] * x[i, j] for i in suppliers if (i, j) in x
            )
            >= 95 * demand[j],
            name=f"quality_{j}",
        )

    for i in suppliers:
        model.addConstr(
            gp.quicksum(x[i, j] for j in components if (i, j) in x)
            <= capacity[i] * y[i],
            name=f"capacity_{i}",
        )

    model.addConstr(
        gp.quicksum(risk[i] * x[i, j] for (i, j) in x) <= 580,
        name="risk",
    )

    model.addConstr(
        gp.quicksum(y[i] for i in suppliers) <= 4,
        name="max_suppliers",
    )

    model.addConstr(
        y["A"] + y["B"] >= 1,
        name="at_least_one_AB",
    )

    for j in components:
        model.addConstr(
            gp.quicksum(z[i, j] for i in suppliers if (i, j) in z) >= 2,
            name=f"min_suppliers_{j}",
        )

    for i, j in available:
        model.addConstr(x[i, j] <= demand[j] * z[i, j], name=f"link_xz_{i}_{j}")
        model.addConstr(x[i, j] >= 10 * z[i, j], name=f"min_lot_{i}_{j}")
        model.addConstr(z[i, j] <= y[i], name=f"link_zy_{i}_{j}")

    model.optimize()

    if model.status == GRB.OPTIMAL:
        sol_status = "OPTIMAL"
        obj_value = model.ObjVal
        var_values = {v.VarName: v.X for v in model.getVars()}
    else:
        status_names = {
            GRB.INFEASIBLE: "INFEASIBLE",
            GRB.INF_OR_UNBD: "INF_OR_UNBD",
            GRB.UNBOUNDED: "UNBOUNDED",
            GRB.CUTOFF: "CUTOFF",
            GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
            GRB.NODE_LIMIT: "NODE_LIMIT",
            GRB.TIME_LIMIT: "TIME_LIMIT",
            GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
            GRB.INTERRUPTED: "INTERRUPTED",
            GRB.NUMERIC: "NUMERIC",
            GRB.SUBOPTIMAL: "SUBOPTIMAL",
            GRB.INPROGRESS: "INPROGRESS",
        }
        sol_status = status_names.get(model.status, str(model.status))
        obj_value = 0.0
        var_values = {}

    print(
        "SOLUTION_JSON="
        + json.dumps(
            {
                "status": sol_status,
                "objective": obj_value,
                "variables": var_values,
            }
        )
    )


if __name__ == "__main__":
    main()
