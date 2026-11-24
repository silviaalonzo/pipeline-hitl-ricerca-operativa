import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
arcs = ["SA", "SB", "AB", "AC", "BC", "BT", "CT"]

fixed_cost = {
    "SA": 40, "SB": 35, "AB": 15, "AC": 30,
    "BC": 18, "BT": 45, "CT": 38
}
unit_cost = {
    "SA": 2, "SB": 3, "AB": 1, "AC": 2,
    "BC": 2, "BT": 4, "CT": 2
}
capacity = {
    "SA": 30, "SB": 35, "AB": 15, "AC": 25,
    "BC": 20, "BT": 25, "CT": 35
}

D = 40  # domanda S->T

model = gp.Model("Rete_Distributiva")
model.Params.OutputFlag = 0

# --- Variabili ---
x = model.addVars(arcs, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(arcs, vtype=GRB.BINARY, name="y")

# --- Funzione obiettivo ---
model.setObjective(
    gp.quicksum(fixed_cost[a] * y[a] + unit_cost[a] * x[a] for a in arcs),
    GRB.MINIMIZE
)

# --- Vincoli di capacità/attivazione ---
for a in arcs:
    model.addConstr(x[a] <= capacity[a] * y[a], name=f"cap_{a}")

# --- Conservazione del flusso ---
# Nodo S
model.addConstr(x["SA"] + x["SB"] == D, name="flow_S")

# Nodo A
model.addConstr(x["SA"] == x["AB"] + x["AC"], name="flow_A")

# Nodo B
model.addConstr(x["SB"] + x["AB"] == x["BC"] + x["BT"], name="flow_B")

# Nodo C
model.addConstr(x["AC"] + x["BC"] == x["CT"], name="flow_C")

# Nodo T
model.addConstr(x["BT"] + x["CT"] == D, name="flow_T")

# --- Risoluzione ---
model.optimize()

# --- Output ---
result = {"status": None, "objective": None, "variables": {}}

if model.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 4)
    variables = {}
    for a in arcs:
        variables[f"x_{a}"] = round(x[a].X, 4)
        variables[f"y_{a}"] = round(y[a].X, 4)
    result["variables"] = variables
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
    }
    result["status"] = status_map.get(model.Status, str(model.Status))
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
