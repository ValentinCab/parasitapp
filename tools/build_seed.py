"""Build the initial Atlas data without adding facts not present in the sources."""
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "upload" / "PARÁSITOS.xlsx"
OUT = ROOT / "dist" / "data" / "seed.json"

FIELDS = [
    "granGroup", "group", "subgroup", "family", "subfamily", "genus", "species",
    "commonName", "importance", "location", "definitiveHost", "cycle", "ppp",
    "morphologyGeneral", "morphologyMale", "morphologyFemale", "egg", "infectiveForm",
    "intermediateHost", "paratenicHost",
]
HEADERS = [
    "GRAN GRUPO", "GRUPO", "SUBGRUPO", "FAMILIA", "SUBFAMILIA", "GÉNERO", "ESPECIE",
    "NOMBRE VULGAR", "IMPORTANCIA", "LOCALIZACIÓN", "HOSPEDADOR DEFINITIVO", "CICLO", "PPP",
    "MORFOLOGÍA GENERAL", "MORFOLOGÍA MACHO", "MORFOLOGÍA HEMBRA", "HUEVO", "FORMA INFECTANTE",
    "HOSPEDADOR INTERMEDIARIO", "HOSPEDADOR PARATÉNICO",
]
LEVELS = [("granGroup", "granGroup"), ("group", "group"), ("subgroup", "subgroup"),
          ("family", "family"), ("subfamily", "subfamily"), ("genus", "genus"), ("species", "species")]

def clean(value):
    return "" if value is None else str(value).strip()

def slug(value):
    base = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")

def cell_color(cell):
    color = cell.fill.fgColor
    return color.rgb if color.type == "rgb" and color.rgb not in (None, "00000000") else ""

def scientific_name(node):
    if node["level"] == "species":
        return f"{node['path'][-2]['name']} {node['name'].lower()}"
    return node["name"]

wb = load_workbook(SOURCE, data_only=True)
ws = wb["TODOS"]
nodes = {}
issues = []

for row_no, row in enumerate(ws.iter_rows(min_row=2, max_col=len(FIELDS)), 2):
    values = {field: clean(row[i].value) for i, field in enumerate(FIELDS)}
    if not any(values.values()):
        continue
    ancestry = []
    parent_id = None
    deepest = None
    for field, level in LEVELS:
        value = values[field]
        if not value:
            continue
        path_piece = {"level": level, "name": value}
        ancestry.append(path_piece)
        node_id = "/".join(f"{part['level']}:{slug(part['name'])}" for part in ancestry)
        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id, "level": level, "name": value, "parentId": parent_id,
                "path": list(ancestry), "fields": {}, "tags": [], "notes": [],
                "sourceRows": [], "initialColor": cell_color(row[FIELDS.index(field)]),
                "createdFrom": "excel",
            }
        node = nodes[node_id]
        node["sourceRows"].append(row_no)
        if cell_color(row[FIELDS.index(field)]):
            node["initialColor"] = cell_color(row[FIELDS.index(field)])
        parent_id = node_id
        deepest = node
    if not deepest:
        continue
    for field in FIELDS[7:]:
        if values[field]:
            current = deepest["fields"].get(field, "")
            if current and current != values[field]:
                deepest["notes"].append({"type":"import-conflict", "message":f"Fila {row_no}: valor adicional importado para {field}.", "value":values[field]})
            elif not current:
                deepest["fields"][field] = values[field]

# Curated name-only records explicitly mentioned in the supplied study material.
# They are deliberately left without inferred traits; their provenance remains visible in the UI.
supplemental = [
    ([('granGroup','HELMINTO'),('group','NEMATODO'),('family','Strongylidae'),('subfamily','Strongylinae'),('genus','Strongylus'),('species','vulgaris')], 'Guía de preparados 2025'),
    ([('granGroup','HELMINTO'),('group','NEMATODO'),('family','Strongylidae'),('subfamily','Strongylinae'),('genus','Strongylus'),('species','edentatus')], 'Guía de preparados 2025'),
    ([('granGroup','HELMINTO'),('group','NEMATODO'),('family','Strongylidae'),('subfamily','Strongylinae'),('genus','Strongylus'),('species','equinus')], 'Guía de preparados 2025'),
    ([('granGroup','HELMINTO'),('group','NEMATODO'),('family','Onchocercidae'),('genus','Dirofilaria'),('species','immitis')], 'Transcritos Parasitología'),
    ([('granGroup','HELMINTO'),('group','NEMATODO'),('family','Onchocercidae'),('genus','Dirofilaria'),('species','repens')], 'Transcritos Parasitología'),
    ([('granGroup','HELMINTO'),('group','CESTODO'),('family','Dilepididae'),('genus','Dipylidium'),('species','caninum')], 'Transcritos Parasitología'),
    ([('granGroup','HELMINTO'),('group','TREMATODO'),('family','Fasciolidae'),('genus','Fasciola'),('species','hepatica')], 'Guía de preparados 2025'),
    ([('granGroup','HELMINTO'),('group','ACANTOCEPHALA'),('family','Oligacanthorhynchidae'),('genus','Macracanthorhynchus'),('species','hirudinaceus')], 'Transcritos Parasitología'),
    ([('granGroup','ARTRÓPODO'),('group','ACARINA'),('family','Ixodidae'),('genus','Rhipicephalus'),('species','microplus')], 'Transcritos Parasitología'),
    ([('granGroup','ARTRÓPODO'),('group','ACARINA'),('family','Ixodidae'),('genus','Rhipicephalus'),('species','sanguineus')], 'Transcritos Parasitología'),
    ([('granGroup','ARTRÓPODO'),('group','ACARINA'),('family','Sarcoptidae'),('genus','Sarcoptes'),('species','scabiei')], 'Guía de preparados 2025'),
]
for path_pairs, source_name in supplemental:
    ancestry=[]; parent_id=None
    for level, name in path_pairs:
        ancestry.append({'level':level,'name':name})
        node_id='/'.join(f"{p['level']}:{slug(p['name'])}" for p in ancestry)
        if node_id not in nodes:
            nodes[node_id] = {"id":node_id,"level":level,"name":name,"parentId":parent_id,"path":list(ancestry),"fields":{},"tags":[],"notes":[],"sourceRows":[],"initialColor":"","createdFrom":"course-material"}
        parent_id=node_id
    nodes[parent_id]["notes"].append({"type":"source-mention","message":f"Nombre mencionado en {source_name}; sin atributos inferidos."})

# Observed wording/spelling discrepancies are surfaced instead of silently normalised.
for pattern, message in [
    ('trychostrongylus', 'El Excel escribe “Trychostrongylus”; los apuntes contienen variantes de grafía. Revisar antes de normalizar.'),
    ('trhichomonadidae', 'El Excel escribe “Trhichomonadidae”; conservar hasta revisión editorial.'),
    ('gaserophilus', 'El Excel escribe “Gaserophilus”; conservar hasta revisión editorial.'),
    ('anoplocesphalidae', 'El Excel incluye “Anoplocesphalidae” y “Anoplocephalidae” como familias distintas; revisar la clasificación antes de consolidar.'),
]:
    matches=[n['id'] for n in nodes.values() if pattern in n['id']]
    if matches: issues.append({'kind':'review','message':message,'nodeIds':matches})

for node in nodes.values():
    node['sourceRows'] = sorted(set(node['sourceRows']))
    node['scientificName'] = scientific_name(node) if node['level'] in ('genus','species') else ''

payload = {
    "schemaVersion": 1,
    "createdAt": datetime.now(timezone.utc).isoformat(),
    "source": {"workbook":"PARÁSITOS.xlsx", "worksheet":"TODOS", "courseMaterials":["Guía práctica Cátedra 2025", "Transcritos Parasitología"]},
    "nodes": sorted(nodes.values(), key=lambda n:(len(n['path']),n['id'])),
    "issues": issues,
    "importSummary": {"excelRows":98, "supplementalNameOnlyRecords":len(supplemental), "noFactsInferred": True}
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"Wrote {OUT} with {len(nodes)} nodes")
