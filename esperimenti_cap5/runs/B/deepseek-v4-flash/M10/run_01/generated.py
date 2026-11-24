import gurobipy as gp
from gurobipy import GRB
import json

arcs = [
    ("S", "A", 40, 2, 30),
    ("S", "B", 35, 3, 35),
    ("A", "B", 15, 1, 15),
    ("A", "C", 30, 2, 25),
    ("B", "C", 18, 2, 20),
    ("B", "T", 45, 4, 25),
    ("C", "T", 38, 2, 35),
]

nodes = ["S", "A", "B", "C", "T"]
E = [(i, j) for i, j, _, _, _ in arcs]

f = {(i, j): f for i, j, f, _, _ in arcs}
c = {(i, j): c for i, j, _, c, _ in arcs}
u = {(i, j): u for i, j, _, _, u in arcs}

m = gp.Model("rete_distributiva")
m.Params.OutputFlag = 0

x = {}
y = {}

for (i, j) in E:
    x[(i, j)] = m.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        ub=u[(i, j)],
        name=f"x_{i}{j}"
    )
    y[(i, j)] = m.addVar(
        vtype=GRB.BINARY,
        name=f"y_{i}{j}"
    )

m.setObjective(
    sum(f[e] * y[e] + c[e] * x[e] for e in E),
    GRB.MINIMIZE
)

balance = {"S": 40, "A": 0, "B": 0, "C": 0, "T": -40}

for n in nodes:
    m.addConstr(
        sum(x[e] for e in E if e[0] == n) -
        sum(x[e] for e in E if e[1] == n) == balance[n],
        name=f"balance_{n}"
    )

for e in E:
    m.addConstr(x[e] <= u[e] * y[e], name=f"link_{e[0]}{e[1]}")

m.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
}

status = status_names.get(m.Status, f"STATUS_{m.Status}")

if status == "OPTIMAL":
    result = {
        "status": status,
        "objective": m.ObjVal,
        "variables": {v.VarName: v.X for v in m.getVars()},
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
