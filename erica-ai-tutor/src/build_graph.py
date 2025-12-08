import json
import pickle
import networkx as nx
from pathlib import Path

def infer_node_type(node_id, desc):
    t = (node_id + " " + str(desc)).lower()
    if any(x in t for x in ["slide", "pdf", "video", "lecture", "scan"]):
        return "resource"
    if any(x in t for x in ["example", "snippet", "worked", "v_", "numeric"]):
        return "example"
    return "concept"

def clean_id(s):
    return str(s).strip().replace("\n", " ").replace("\t", " ")

def normalize_entity(ent):
    if isinstance(ent, dict):
        return {
            "id": clean_id(ent.get("id", "")),
            "type": ent.get("type", None),
            "desc": ent.get("desc", "")
        }
    if isinstance(ent, str):
        return {"id": clean_id(ent), "type": None, "desc": ""}
    return None

def normalize_relation(rel):
    if not isinstance(rel, dict):
        return None
    src = clean_id(rel.get("source", ""))
    tgt = clean_id(rel.get("target", ""))
    r = str(rel.get("relation", "")).lower()
    if not src or not tgt:
        return None
    return {"source": src, "target": tgt, "relation": r}

def build_graph(input_jsonl="data/entities_relations.jsonl",
                output_graph="data/kg_graph.gpickle"):

    G = nx.MultiDiGraph()
    seen_nodes = {}
    seen_edges = set()

    with open(input_jsonl, "r") as f:
        for line in f:
            row = json.loads(line)
            if row.get("status") != "success":
                continue

            ents = []
            for e in row.get("entities", []):
                e = normalize_entity(e)
                if e and e["id"]:
                    ents.append(e)

            for e in ents:
                nid = e["id"]
                desc = e["desc"]
                ntype = infer_node_type(nid, desc)
                if nid not in seen_nodes:
                    seen_nodes[nid] = ntype
                    G.add_node(nid,
                               node_type=ntype,
                               title=nid,
                               definitions=[desc] if desc else [],
                               aliases=[],
                               difficulty=None,
                               span=None,
                               timecodes=None)

            rels = []
            for r in row.get("relationships", []):
                r = normalize_relation(r)
                if r:
                    rels.append(r)

            for r in rels:
                src, tgt, rel = r["source"], r["target"], r["relation"]
                if src not in seen_nodes or tgt not in seen_nodes:
                    continue

                if "prereq" in rel:
                    etype = "prereq_of"
                elif "explain" in rel:
                    etype = "explains"
                elif "exempl" in rel:
                    etype = "exemplifies"
                else:
                    etype = "near_transfer"

                key = (src, tgt, etype)
                if key not in seen_edges:
                    seen_edges.add(key)
                    G.add_edge(src, tgt, relation=etype)

    Path(output_graph).parent.mkdir(parents=True, exist_ok=True)
    with open(output_graph, "wb") as f:
        pickle.dump(G, f)

    print("Graph built")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    print("Saved:", output_graph)

    return G

if __name__ == "__main__":
    build_graph()