"""Preview of the Session 3 'wow' graph: NordWind as an interactive physics network."""
import json
from pathlib import Path
from pyvis.network import Network

DS = Path(__file__).parent / "dataset"
teams = json.loads((DS / "entities/teams.json").read_text())
engineers = json.loads((DS / "entities/engineers.json").read_text())
services = json.loads((DS / "entities/services.json").read_text())
incidents = json.loads((DS / "entities/incidents.json").read_text())
rels = json.loads((DS / "relationships.json").read_text())

COLORS = {
    "Team":     "#f59e0b",  # amber
    "Engineer": "#60a5fa",  # blue
    "Service":  "#34d399",  # green
    "Incident": "#f87171",  # red
}

net = Network(height="780px", width="100%", bgcolor="#0f172a",
              font_color="#e2e8f0", notebook=False, directed=True)
net.barnes_hut(gravity=-9000, central_gravity=0.25,
               spring_length=140, spring_strength=0.02, damping=0.35)

for t in teams:
    net.add_node(t["name"], label=t["name"], color=COLORS["Team"], shape="hexagon",
                 size=34, title=f"Team — {t['focus']}")
for e in engineers:
    net.add_node(e["name"], label=e["name"].split()[0], color=COLORS["Engineer"],
                 size=16, title=f"{e['name']} — {e['role']}, {e['team_name']}")
for s in services:
    net.add_node(s["name"], label=s["name"], color=COLORS["Service"], shape="box",
                 size=24, title=f"Service ({s['language']}) — {s['description']}\nOwner: {s['owner_team']}")
for i in incidents:
    net.add_node(i["id"], label=i["id"], color=COLORS["Incident"], shape="diamond",
                 size=20, title=f"{i['severity']} — {i['title']} ({i['date']})")

EDGE_STYLE = {
    "MEMBER_OF":    {"color": "#64748b", "width": 1},
    "OWNS":         {"color": "#f59e0b", "width": 2},
    "DEPENDS_ON":   {"color": "#34d399", "width": 2, "dashes": True},
    "AFFECTED":     {"color": "#f87171", "width": 2},
    "RESPONDED_TO": {"color": "#93c5fd", "width": 1},
}
for r in rels:
    st = EDGE_STYLE[r["type"]]
    net.add_edge(r["from"], r["to"], title=r["type"], **st)

net.write_html(str(Path(__file__).parent / "nordwind_graph_preview.html"),
               notebook=False, open_browser=False)
print("nodes:", len(net.nodes), "edges:", len(net.edges))
