import gurobipy as gp
from gurobipy import GRB
import json

nodes = ["S", "A", "B", "C", "T"]
arcs = [
    ("S", "A"),
    ("S", "B"),
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
    ("B", "T"),
    ("C", "T"),
]

fixed = {
    ("S", "A"): 40,
    ("S", "B"): 35,
    ("A", "B"): 15,
    ("A", "C"): 30,
    ("B", "C"): 18,
    ("B", "T"): 45,
    ("C", "T"): 38,
}

cost = {
    ("S", "A"): 2,
    ("S", "B"): 3,
    ("A", "B"): 1,
    ("A", "C"): 2,
    ("B", "C"): 2,
    ("B", "T"): 4,
    ("C", "T"): 2,
}

capacity = {
    ("S", "A"): 30,
    ("S", "B"): 35,
    ("A", "B"): 15,
    ("A", "C"): 25,
    ("B", "C"): 20,
    ("B", "T"): 25,
    ("C", "T"): 35,
}

demand = 40

m = gp.Model("rete_distributiva")
m.Params.OutputFlag = 0

x = {}
y = {}

for i, j in arcs:
    x[(i, j)] = m.addVar(
        lb=0,
        ub=capacity[(i, j)],
        vtype=GRB.INTEGER,
        name=f"x_{i}{j}"
    )
    y[(i, j)] = m.addVar(
        vtype=GRB.BINARY,
        name=f"y_{i}{j}"
    )

m.update()

outgoing = {n: [] for n in nodes}
incoming = {n: [] for n in nodes}

for i, j in arcs:
    outgoing[i].append((i, j))
    incoming[j].append((i, j))

for n in nodes:
    lhs = gp.quicksum(x[a] for a in outgoing[n]) - gp.quicksum(x[a] for a in incoming[n])
    if n == "S":
        rhs = demand
    elif n == "T":
        rhs = -demand
    else:
        rhs = 0
    m.addConstr(lhs == rhs, name=f"flow_{n}")

for i, j in arcs:
    m.addConstr(x[(i, j)] <= capacity[(i, j)] * y[(i, j)], name=f"cap_{i}{j}")

m.setObjective(
    gp.quicksum(fixed[a] * y[a] + cost[a] * x[a] for a in arcs),
    GRB.MINIMIZE
)

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = m.ObjVal
    variables = {v.VarName: v.X for v in m.getVars()}
else:
    status = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.NODE_LIMIT: "NODE_LIMIT",
        GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
        GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
        GRB.INTERRUPTED: "INTERRUPTED",
        GRB.NUMERIC: "NUMERIC",
        GRB.SUBOPTIMAL: "SUBOPTIMAL",
    }.get(m.status, "UNKNOWN")
    objective = None
    variables = {}

result = {
    "status": status,
    "objective": objective,
    "variables": variables,
}

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
