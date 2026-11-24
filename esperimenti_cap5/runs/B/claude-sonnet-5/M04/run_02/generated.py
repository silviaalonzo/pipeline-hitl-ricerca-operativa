import gurobipy as gp
from gurobipy import GRB
import json

# Dati
tipi = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]
volume = {"Van":18, "Autocarro":30, "Refrigerato":20, "Elettrico":16, "Bilico":42}
portata = {"Van":8,  "Autocarro":18, "Refrigerato":10, "Elettrico":7,  "Bilico":28}
costo   = {"Van":120,"Autocarro":180,"Refrigerato":210,"Elettrico":150,"Bilico":260}
emiss   = {"Van":12, "Autocarro":22, "Refrigerato":15, "Elettrico":4,  "Bilico":32}
disp    = {"Van":8,  "Autocarro":6,  "Refrigerato":4,  "Elettrico":5,  "Bilico":3}

VOL_MIN = 180
PORT_MIN = 95
EM_MAX = 145

model = gp.Model("Composizione_flotta")

x = model.addVars(tipi, vtype=GRB.INTEGER, lb=0, ub={t: disp[t] for t in tipi}, name="x")

model.setObjective(gp.quicksum(costo[t] * x[t] for t in tipi), GRB.MINIMIZE)

model.addConstr(gp.quicksum(volume[t] * x[t] for t in tipi) >= VOL_MIN, name="volume_min")
model.addConstr(gp.quicksum(portata[t] * x[t] for t in tipi) >= PORT_MIN, name="portata_min")
model.addConstr(gp.quicksum(emiss[t] * x[t] for t in tipi) <= EM_MAX, name="emissioni_max")
model.addConstr(x["Refrigerato"] >= 1, name="min_refrigerato")
model.addConstr(x["Elettrico"] >= 1, name="min_elettrico")

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = model.ObjVal
    result["variables"] = {f"x_{t}": x[t].X for t in tipi}
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    result["status"] = status_map.get(status, str(status))

print("SOLUTION_JSON=" + json.dumps(result))
