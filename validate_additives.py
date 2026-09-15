import yaml, collections

P = "/Users/khleecnce/cmp-sim/cmp_sim/data/params/additives.yaml"
d = yaml.safe_load(open(P))

adds = d["additives"]
FILMS = list(d["films"])
print("=" * 72)
print("PARSE OK:", P)
print("additives           :", len(adds))
print("films declared      :", len(FILMS), FILMS)
print("interaction_rules   :", len(d["interaction_rules"]))

# every additive covers every film?
missing = {k: sorted(set(FILMS) - set(v["film_effects"])) for k, v in adds.items()
           if set(FILMS) - set(v["film_effects"])}
print("additives missing a film entry:", missing or "none - all %d x %d pairs present"
      % (len(adds), len(FILMS)))

# roles
roles = collections.Counter(v["role"] for v in adds.values())
print("\nroles:", dict(roles))

# ---- numeric audit: any mapping with a 'value' key is a numeric entry
sourced, nulled, by_conf = 0, 0, collections.Counter()
todo = 0
sources = set()

def walk(node):
    global sourced, nulled, todo
    if isinstance(node, dict):
        if "value" in node and "confidence" in node:
            by_conf[node["confidence"]] += 1
            if node.get("value") is None:
                nulled += 1
            if node.get("value") is not None and node.get("source"):
                sourced += 1
            if "TODO(owner)" in str(node.get("note", "")):
                todo += 1
            if node.get("source"):
                sources.add(node["source"])
        for v in node.values():
            walk(v)
    elif isinstance(node, list):
        for v in node:
            walk(v)

walk(adds)
walk(d["interaction_rules"])

print("\n--- numeric entries ---")
print("total numeric entries      :", sum(by_conf.values()))
print("with real value + source   :", sourced)
print("value: null (declared gap) :", nulled)
print("carrying TODO(owner)       :", todo)
print("by confidence              :", dict(by_conf))

# ---- film_effects audit
fe_dir = collections.Counter()
fe_known = collections.Counter()
for k, v in adds.items():
    for film, eff in v["film_effects"].items():
        fe_dir[eff.get("direction")] += 1
        if eff.get("direction") != "unknown":
            fe_known[film] += 1
print("\n--- film_effects (%d entries) ---" % sum(fe_dir.values()))
print("directions:", dict(fe_dir))
print("entries with real content per film:")
for f in FILMS:
    print("   %-8s %3d / %d" % (f, fe_known[f], len(adds)))

# ---- citations
dois = sorted({s for s in sources if "doi:" in s or "10." in s})
pats = sorted({s for s in sources if s.split()[0].startswith(("US", "WO", "EP", "KR", "TW", "CN"))})
print("\n--- citations ---")
print("distinct source strings:", len(sources))
print("DOI-bearing            :", len(dois))
print("patent-first           :", len(pats))

assert sourced > 0 and len(adds) >= 30
print("\nVALIDATION PASSED")
