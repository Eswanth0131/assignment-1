import pickle
import json
import networkx as nx
from pathlib import Path
import re
import requests

G = pickle.load(open("/app/data/kg_graph.gpickle", "rb"))

def extract_concepts(q):
    q = q.lower()
    tokens = re.findall(r"[a-zA-Z0-9\-]+", q)
    return list(set([t for t in tokens if len(t) > 3]))

def match_nodes(concepts):
    ids = list(G.nodes())
    out = {}
    for c in concepts:
        matches = [n for n in ids if c in n.lower()]
        if matches:
            out[c] = matches[:5]
    return out

def prereqs(n):
    return [a for a, _, d in G.in_edges(n, data=True) if d.get("relation") == "prereq_of"]

def neighbors(n):
    return list(set(list(G.successors(n)) + list(G.predecessors(n))))

def siblings(n):
    r = []
    for a, b, d in G.edges(n, data=True):
        if d.get("relation") == "near_transfer":
            if a != n: r.append(a)
            if b != n: r.append(b)
    return list(set(r))

def resources(n):
    out = []
    for x in G.predecessors(n):
        if G.nodes[x].get("node_type") == "resource":
            out.append(x)
    return out

def gather_subgraph(nodes):
    s = set()
    for n in nodes:
        if n in G and G.nodes[n].get("node_type") == "concept":
            s.add(n)
            for x in prereqs(n):
                if G.nodes[x].get("node_type") == "concept":
                    s.add(x)
            for x in neighbors(n):
                if G.nodes[x].get("node_type") == "concept":
                    s.add(x)
            for x in siblings(n):
                if G.nodes[x].get("node_type") == "concept":
                    s.add(x)
    return list(s)

def gather_resources(nodes):
    r = set()
    for n in nodes:
        for x in resources(n):
            r.add(x)
    return list(r)

def make_context(nodes):
    out = []
    for n in nodes:
        defs = G.nodes[n].get("definitions", [])
        if not defs or not isinstance(defs, list):
            d = ""
        else:
            d = defs[0] if defs else ""
        out.append(f"- {n}: {d}")
    return "\n".join(out)

def ask(system_prompt, question, context):
    prompt = system_prompt + "\n\nCONTEXT:\n" + context + "\n\nQUESTION:\n" + question
    r = requests.post("http://host.docker.internal:11434/api/generate",
                      json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False})
    return r.json().get("response", "")

def run(q):
    concepts = extract_concepts(q)
    matched = match_nodes(concepts)

    base = []
    for v in matched.values():
        base.extend(v)
    base = list(set(base))

    sub = gather_subgraph(base)
    res = gather_resources(base)

    context = make_context(sub)
    system_prompt = "You are an AI tutor. Use only the provided graph context. Explain from basic to advanced."

    answer = ask(system_prompt, q, context)

    Path("data").mkdir(exist_ok=True)
    with open("data/m4_subgraphs.jsonl", "a") as f:
        f.write(json.dumps({
            "question": q,
            "system_prompt": system_prompt,
            "subgraph": sub,
            "resources": res
        }) + "\n")

    return answer

if __name__ == "__main__":
    while True:
        q = input("Enter a question (or 'exit'): ")
        if q.lower().strip() == "exit":
            break
        answer = run(q)
        print("ANSWER\n")
        print(answer)
        print("\n---------------------------\n")