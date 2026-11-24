import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
stations = ["A","B","C","D","E","F","G","H"]
fixed_cost = {"A":35,"B":32,"C":40,"D":30,"E":38,"F":33,"G":36,"H":31}
capacity   = {"A":42,"B":44,"C":46,"D":40,"E":45,"F":43,"G":44,"H":42}

West = ["A","B","C","D"]
East = ["E","F","G","H"]

demand = {
    "Z1":8, "Z2":7, "Z3":10, "Z4":6, "Z5":9, "Z6":8,
    "Z7":7, "Z8":11, "Z9":6, "Z10":9, "Z11":8, "Z12":7
}

reach = {
    "Z1":  {"A":3, "B":5},
    "Z2":  {"A":6, "B":8, "C":10},
    "Z3":  {"B":11,"C":4, "D":6},
    "Z4":  {"C":7, "D":9},
    "Z5":  {"A":6, "D":3, "E":5},
    "Z6":  {"B":11,"E":8, "F":10},
    "Z7":  {"C":7, "F":4, "G":6, "H":8},
    "Z8":  {"D":3, "G":9, "H":11},
    "Z9":  {"E":8, "F":10,"H":5},
    "Z10": {"F":4, "G":6, "H":8},
    "Z11": {"A":6, "E":5, "H":11},
    "Z12": {"B":11,"G":3, "H":5},
}

critical = ["Z3","Z8","Z11"]
zones = list(demand.keys())

# --- Modello ---
m = gp.Model("H08_emergency_network")

y = m.addVars(stations, vtype=GRB.BINARY, name="y")
x = {}
for z in zones:
    for s in reach[z]:
        x[z,s] = m.addVar(vtype=GRB.BINARY, name=f"x_{z}_{s}")

m.update()

# Obiettivo
fixed_part = gp.quicksum(fixed_cost[s]*y[s] for s in stations)
travel_part = gp.quicksum(demand[z]*reach[z][s]*x[z,s] for z in zones for s in reach[z])
m.setObjective(fixed_part + travel_part, GRB.MINIMIZE)

# Vincolo: esattamente 4 stazioni aperte
m.addConstr(gp.quicksum(y[s] for s in stations) == 4, name="num_stations")

# Vincolo: assegnazione unica per ogni zona
for z in zones:
    m.addConstr(gp.quicksum(x[z,s] for s in reach[z]) == 1, name=f"assign_{z}")

# Vincolo: assegnazione solo a stazioni aperte
for z in zones:
    for s in reach[z]:
        m.addConstr(x[z,s] <= y[s], name=f"link_{z}_{s}")

# Vincolo: capacità
for s in stations:
    m.addConstr(
        gp.quicksum(demand[z]*x[z,s] for z in zones if s in reach[z]) <= capacity[s]*y[s],
        name=f"cap_{s}"
    )

# Vincolo: copertura geografica
m.addConstr(gp.quicksum(y[s] for s in West) >= 1, name="west_min")
m.addConstr(gp.quicksum(y[s] for s in East) >= 1, name="east_min")

# Vincolo: backup zone critiche
for z in critical:
    m.addConstr(gp.quicksum(y[s] for s in reach[z]) >= 2, name=f"backup_{z}")

m.optimize()

# --- Output ---
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for s in stations:
        variables[f"y_{s}"] = round(y[s].X, 4)
    for z in zones:
        for s in reach[z]:
            variables[f"x_{z}_{s}"] = round(x[z,s].X, 4)
    result["variables"] = variables
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    result["status"] = status_map.get(m.status, str(m.status))

print("SOLUTION_JSON=" + json.dumps(result))
