import gurobipy as gp
from gurobipy import GRB
import json

nodes = ["S", "A", "B", "C", "D", "T"]
products = ["K1", "K2"]

arcs = [
    ("S", "A"),
    ("S", "B"),
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
    ("B", "D"),
    ("C", "D"),
    ("C", "T"),
    ("D", "T"),
]

fixed_cost = {
    ("S", "A"): 55,
    ("S", "B"): 50,
    ("A", "B"): 18,
    ("A", "C"): 38,
    ("B", "C"): 22,
    ("B", "D"): 35,
    ("C", "D"): 20,
    ("C", "T"): 48,
    ("D", "T"): 44,
}

capacity = {
    ("S", "A"): 35,
    ("S", "B"): 35,
    ("A", "B"): 15,
    ("A", "C"): 30,
    ("B", "C"): 25,
    ("B", "D"): 25,
    ("C", "D"): 20,
    ("C", "T"): 35,
    ("D", "T"): 35,
}

unit_cost = {
    ("S", "A"): {"K1": 2, "K2": 3},
    ("S", "B"): {"K1": 3, "K2": 2},
    ("A", "B"): {"K1": 1, "K2": 2},
    ("A", "C"): {"K1": 2, "K2": 3},
    ("B", "C"): {"K1": 2, "K2": 1},
    ("B", "D"): {"K1": 3, "K2": 2},
    ("C", "D"): {"K1": 1, "K2": 2},
    ("C", "T"): {"K1": 3, "K2": 2},
    ("D", "T"): {"K1": 2, "K2": 3},
}

demand = {"K1": 28, "K2": 22}

model = gp.Model("H10_rete_multi_prodotto")
model.Params.OutputFlag = 0
model.Params.Threads = 1
model.Params.Seed = 0
model.Params.MIPGap = 0.0
model.ModelSense = GRB.MINIMIZE

y = {
    arc: model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{arc[0]}_{arc[1]}"
    )
    for arc in arcs
}

x = {
    (arc, k): model.addVar(
        lb=0,
        vtype=GRB.INTEGER,
        name=f"x_{arc[0]}_{arc[1]}_{k}"
    )
    for arc in arcs
    for k in products
}

primary_objective = (
    gp.quicksum(fixed_cost[arc] * y[arc] for arc in arcs)
    + gp.quicksum(
        unit_cost[arc][k] * x[(arc, k)]
        for arc in arcs
        for k in products
    )
)

# Obiettivo primario del problema.
model.setObjectiveN(
    primary_objective,
    index=0,
    priority=2,
    weight=1.0,
    abstol=0.0,
    reltol=0.0,
    name="costo_totale"
)

# Criterio secondario esclusivamente per selezionare una soluzione
# deterministica tra quelle con lo stesso costo totale ottimo.
model.setObjectiveN(
    x[(("C", "D"), "K1")],
    index=1,
    priority=1,
    weight=1.0,
    abstol=0.0,
    reltol=0.0,
    name="tie_break"
)

for k in products:
    for v in nodes:
        outgoing = gp.quicksum(
            x[(arc, k)] for arc in arcs if arc[0] == v
        )
        incoming = gp.quicksum(
            x[(arc, k)] for arc in arcs if arc[1] == v
        )

        if v == "S":
            rhs = demand[k]
        elif v == "T":
            rhs = -demand[k]
        else:
            rhs = 0

        model.addConstr(
            outgoing - incoming == rhs,
            name=f"balance_{v}_{k}"
        )

for arc in arcs:
    model.addConstr(
        gp.quicksum(x[(arc, k)] for k in products)
        <= capacity[arc] * y[arc],
        name=f"capacity_{arc[0]}_{arc[1]}"
    )

model.addConstr(y[("S", "A")] == 1, name="resilience_S_A")
model.addConstr(y[("S", "B")] == 1, name="resilience_S_B")

model.addConstr(
    gp.quicksum(y[arc] for arc in arcs) <= 7,
    name="maximum_active_arcs"
)

model.optimize()

status_map = {
    1: "LOADED",
    2: "OPTIMAL",
    3: "INFEASIBLE",
    4: "INF_OR_UNBD",
    5: "UNBOUNDED",
    6: "CUTOFF",
    7: "ITERATION_LIMIT",
    8: "NODE_LIMIT",
    9: "TIME_LIMIT",
    10: "SOLUTION_LIMIT",
    11: "INTERRUPTED",
    12: "NUMERIC",
    13: "SUBOPTIMAL",
    14: "INPROGRESS",
    15: "USER_OBJ_LIMIT",
    16: "WORK_LIMIT",
    17: "MEM_LIMIT",
}

status = status_map.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    all_variables = (
        [y[arc] for arc in arcs]
        + [x[(arc, k)] for arc in arcs for k in products]
    )

    variable_values = {}
    for var in all_variables:
        value = float(round(var.X))
        if value == -0.0:
            value = 0.0
        variable_values[var.VarName] = value

    objective_value = float(round(primary_objective.getValue(), 10))

    result = {
        "status": "OPTIMAL",
        "objective": objective_value,
        "variables": variable_values,
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
