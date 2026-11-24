#!/usr/bin/env python3
"""Genera i documenti Word e i prompt del dataset Cap. 4."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
BLUE = RGBColor(31, 78, 121)
DARK = RGBColor(24, 43, 63)
MUTED = RGBColor(92, 103, 112)
LIGHT = "E8EEF5"
PALE = "F4F6F9"
WHITE = "FFFFFF"
GRID = "B8C4D0"
CONTENT_DXA = 9400


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=110, bottom=80, end=110) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, val in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(val)); node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=GRID, size="4") -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single"); node.set(qn("w:sz"), size); node.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_table_geometry(table, widths: list[int]) -> None:
    table.autofit = False
    total = sum(widths)
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW"); tbl_pr.insert(0, tbl_w)
    tbl_w.set(qn("w:w"), str(total)); tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd"); tbl_pr.insert(1, tbl_ind)
    tbl_ind.set(qn("w:w"), "120"); tbl_ind.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid): grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol"); col.set(qn("w:w"), str(width)); grid.append(col)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW"); tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(widths[idx])); tc_w.set(qn("w:type"), "dxa")


def proportional_widths(headers, rows, total=CONTENT_DXA) -> list[int]:
    scores = []
    for i, header in enumerate(headers):
        values = [str(header)] + [str(row[i]) for row in rows]
        max_len = max(len(x) for x in values)
        avg_len = sum(len(x) for x in values) / len(values)
        score = max(8, min(30, 0.6 * max_len + 0.4 * avg_len))
        scores.append(score)
    raw = [max(650, int(total * s / sum(scores))) for s in scores]
    diff = total - sum(raw)
    raw[-1] += diff
    return raw


def add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar"); fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar"); fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr, fld_char2])


def new_numbering_id(doc: Document) -> int:
    """Crea una lista numerata indipendente che riparte da 1."""
    numbering = doc.part.numbering_part.element
    abstract_ids = [int(x.get(qn("w:abstractNumId"))) for x in numbering.findall(qn("w:abstractNum"))]
    num_ids = [int(x.get(qn("w:numId"))) for x in numbering.findall(qn("w:num"))]
    abstract_id = max(abstract_ids, default=-1) + 1
    num_id = max(num_ids, default=0) + 1

    abstract = OxmlElement("w:abstractNum"); abstract.set(qn("w:abstractNumId"), str(abstract_id))
    multi = OxmlElement("w:multiLevelType"); multi.set(qn("w:val"), "singleLevel"); abstract.append(multi)
    lvl = OxmlElement("w:lvl"); lvl.set(qn("w:ilvl"), "0")
    start = OxmlElement("w:start"); start.set(qn("w:val"), "1"); lvl.append(start)
    fmt = OxmlElement("w:numFmt"); fmt.set(qn("w:val"), "decimal"); lvl.append(fmt)
    text = OxmlElement("w:lvlText"); text.set(qn("w:val"), "%1."); lvl.append(text)
    jc = OxmlElement("w:lvlJc"); jc.set(qn("w:val"), "left"); lvl.append(jc)
    ppr = OxmlElement("w:pPr")
    tabs = OxmlElement("w:tabs"); tab = OxmlElement("w:tab"); tab.set(qn("w:val"), "num"); tab.set(qn("w:pos"), "720"); tabs.append(tab); ppr.append(tabs)
    ind = OxmlElement("w:ind"); ind.set(qn("w:left"), "720"); ind.set(qn("w:hanging"), "360"); ppr.append(ind)
    lvl.append(ppr); abstract.append(lvl)
    first_num = numbering.find(qn("w:num"))
    if first_num is None: numbering.append(abstract)
    else: numbering.insert(list(numbering).index(first_num), abstract)
    num = OxmlElement("w:num"); num.set(qn("w:numId"), str(num_id))
    aid = OxmlElement("w:abstractNumId"); aid.set(qn("w:val"), str(abstract_id)); num.append(aid); numbering.append(num)
    return num_id


def add_numbered_items(doc: Document, items: list[str]) -> None:
    num_id = new_numbering_id(doc)
    for item in items:
        p = doc.add_paragraph(style="List Number"); p.add_run(item)
        ppr = p._p.get_or_add_pPr()
        num_pr = OxmlElement("w:numPr")
        ilvl = OxmlElement("w:ilvl"); ilvl.set(qn("w:val"), "0"); num_pr.append(ilvl)
        num = OxmlElement("w:numId"); num.set(qn("w:val"), str(num_id)); num_pr.append(num)
        ppr.append(num_pr)


def configure_document(doc: Document, short_title: str) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21); section.page_height = Cm(29.7)
    section.top_margin = Cm(2); section.bottom_margin = Cm(2)
    section.left_margin = Cm(2); section.right_margin = Cm(2)
    section.header_distance = Cm(0.8); section.footer_distance = Cm(0.8)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"; normal.font.size = Pt(10.5); normal.font.color.rgb = DARK
    normal.paragraph_format.space_after = Pt(6); normal.paragraph_format.line_spacing = 1.15
    for name, size, color, before, after in [
        ("Title", 27, DARK, 0, 8), ("Subtitle", 14, MUTED, 0, 16),
        ("Heading 1", 16, BLUE, 16, 8), ("Heading 2", 13, BLUE, 12, 6),
        ("Heading 3", 11.5, DARK, 8, 4),
    ]:
        style = styles[name]; style.font.name = "Aptos Display" if name != "Normal" else "Aptos"
        style.font.size = Pt(size); style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before); style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
    styles["Title"].font.bold = True
    styles["Heading 1"].font.bold = True; styles["Heading 2"].font.bold = True; styles["Heading 3"].font.bold = True
    for name in ["List Bullet", "List Number"]:
        styles[name].font.name = "Aptos"; styles[name].font.size = Pt(10.5)
        styles[name].paragraph_format.left_indent = Cm(0.65); styles[name].paragraph_format.first_line_indent = Cm(-0.35)
        styles[name].paragraph_format.space_after = Pt(4); styles[name].paragraph_format.line_spacing = 1.15
    if "Problem Meta" not in styles:
        st = styles.add_style("Problem Meta", WD_STYLE_TYPE.PARAGRAPH)
        st.font.name = "Aptos"; st.font.size = Pt(9); st.font.bold = True; st.font.color.rgb = MUTED
        st.paragraph_format.space_after = Pt(5)

    header = section.header
    hp = header.paragraphs[0]; hp.text = short_title; hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    hp.runs[0].font.name = "Aptos"; hp.runs[0].font.size = Pt(8.5); hp.runs[0].font.color.rgb = MUTED
    footer = section.footer
    fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = fp.add_run("Silvia Alonzo  |  "); r.font.name = "Aptos"; r.font.size = Pt(8.5); r.font.color.rgb = MUTED
    add_page_field(fp)


def add_cover(doc: Document, title: str, subtitle: str, label: str, warning: str | None = None) -> None:
    for _ in range(5): doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(label.upper()); r.bold = True; r.font.name = "Aptos"; r.font.size = Pt(10); r.font.color.rgb = BLUE
    p.paragraph_format.space_after = Pt(14)
    p = doc.add_paragraph(title, style="Title"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(subtitle, style="Subtitle"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("Tesi MSc — Human-in-the-Loop Optimization", style="Problem Meta"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("Silvia Alonzo · Sapienza Università di Roma · luglio 2026", style="Problem Meta"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if warning:
        doc.add_paragraph()
        table = doc.add_table(rows=1, cols=1); table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_geometry(table, [7200]); set_table_borders(table, color="C7A54A", size="6")
        set_cell_shading(table.cell(0,0), "FFF7DE")
        p = table.cell(0,0).paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rr = p.add_run(warning); rr.bold = True; rr.font.color.rgb = RGBColor(110, 80, 0); rr.font.size = Pt(10.5)
        set_cell_margins(table.cell(0,0), top=160, bottom=160, start=180, end=180)
    doc.add_page_break()


def add_data_table(doc: Document, item: dict, font_size=8.5) -> None:
    p = doc.add_paragraph(item["title"], style="Heading 3")
    p.paragraph_format.keep_with_next = True
    headers, rows = item["headers"], item["rows"]
    table = doc.add_table(rows=1, cols=len(headers)); table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]; cell.text = str(h); set_cell_shading(cell, LIGHT); cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for run in cell.paragraphs[0].runs: run.bold = True; run.font.color.rgb = DARK; run.font.size = Pt(font_size)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_repeat_table_header(table.rows[0])
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val); cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 or len(str(val)) > 18 else WD_ALIGN_PARAGRAPH.CENTER
            for run in cells[i].paragraphs[0].runs: run.font.size = Pt(font_size); run.font.name = "Aptos"
    widths = proportional_widths(headers, rows)
    set_table_geometry(table, widths); set_table_borders(table)
    for row in table.rows:
        for cell in row.cells: set_cell_margins(cell)


def add_summary_table(doc: Document, records: list[dict], include_objective=False) -> None:
    headers = ["ID", "Difficoltà", "Dominio", "Classe"]
    if include_objective: headers += ["Variabili", "Vincoli", "Ottimo"]
    rows = []
    for rec in records:
        row = [rec["id"], rec["difficulty"], rec["domain"], rec["model_class"]]
        if include_objective:
            s = rec["structural_size"]; row += [s["variables"], s["constraints"], fmt_num(rec["solution"]["objective"])]
        rows.append(row)
    add_data_table(doc, {"title":"Quadro sintetico delle istanze", "headers":headers, "rows":rows}, font_size=8.2)


def add_problem_header(doc: Document, rec: dict, page_break: bool = True) -> None:
    p = doc.add_paragraph(f"{rec['id']}  ·  {rec['title']}", style="Heading 1")
    p.paragraph_format.page_break_before = page_break
    table = doc.add_table(rows=1, cols=4); table.alignment = WD_TABLE_ALIGNMENT.CENTER
    values = [("Dominio", rec["domain"]), ("Difficoltà", rec["difficulty"]), ("Classe", rec["model_class"]), ("Coppia", str(rec["pair"]))]
    for idx, (label, value) in enumerate(values):
        cell = table.cell(0,idx); set_cell_shading(cell, PALE); cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        r = p.add_run(label.upper()+"\n"); r.bold=True; r.font.size=Pt(7.5); r.font.color.rgb=MUTED
        r = p.add_run(value); r.bold=True; r.font.size=Pt(9); r.font.color.rgb=DARK
        set_cell_margins(cell, top=100, bottom=100, start=80, end=80)
    set_table_geometry(table, [2350]*4); set_table_borders(table, color="D6DEE6")
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def fmt_num(value) -> str:
    if isinstance(value, float) and abs(value-round(value))<1e-8: return str(int(round(value)))
    return f"{value:.4f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def pretty_var(name: str) -> str:
    if "_" not in name: return name
    first, *rest = name.split("_")
    return f"{first}[{', '.join(rest)}]"


def variable_groups(rec: dict) -> list[list[str]]:
    groups = defaultdict(list)
    for spec in rec["variables"]:
        prefix = spec["name"].split("_")[0]
        groups[(prefix, spec["vartype"])].append(spec["name"])
    rows=[]
    labels={"B":"binaria","I":"intera","C":"continua"}
    for (prefix,typ),names in groups.items():
        example=", ".join(pretty_var(n) for n in names[:3])
        if len(names)>3: example += ", …"
        rows.append([prefix, labels[typ], len(names), example])
    return rows


def constraint_families(rec: dict) -> list[list[str]]:
    cnt=Counter()
    for con in rec["constraints"]:
        name=con["name"]
        prefix=name.split("_")[0]
        cnt[prefix]+=1
    return [[k,v] for k,v in sorted(cnt.items())]


def add_solution_table(doc: Document, nonzero_values: dict) -> None:
    pairs = [[pretty_var(name), fmt_num(value)] for name, value in nonzero_values.items()]
    rows = []
    for start in range(0, len(pairs), 3):
        row = []
        for pair in pairs[start:start+3]: row.extend(pair)
        while len(row) < 6: row.extend(["", ""])
        rows.append(row)
    add_data_table(
        doc,
        {"title":"Variabili non nulle (le altre valgono zero)",
         "headers":["Variabile","Valore","Variabile","Valore","Variabile","Valore"],
         "rows":rows},
        font_size=8.0,
    )


def write_prompt_files(public_records: list[dict]) -> None:
    prompt_dir = ROOT / "prompts"
    prompt_dir.mkdir(exist_ok=True)
    for rec in public_records:
        lines=[f"# {rec['id']} — {rec['title']}","",f"Difficoltà: {rec['difficulty']}",f"Classe: {rec['model_class']}",""]
        lines += rec["intro"] + [""]
        for table in rec["tables"]:
            lines += [f"## {table['title']}",""," | ".join(str(x) for x in table["headers"])," | ".join("---" for _ in table["headers"])]
            lines += [" | ".join(str(x) for x in row) for row in table["rows"]]
            lines.append("")
        lines += ["## Consegna",""]+[f"{i}. {x}" for i,x in enumerate(rec["request"],1)]
        (prompt_dir/f"{rec['id']}.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def build_public_doc(records: list[dict]) -> Path:
    doc=Document(); configure_document(doc,"Dataset sperimentale · Tracce")
    add_cover(doc,"Dataset sperimentale IP/MILP","20 problemi per il confronto fra esperto, LLM e pipeline ibrida","Documento di somministrazione")
    doc.add_heading("Protocollo di utilizzo",level=1)
    doc.add_paragraph("Questo documento contiene esclusivamente le tracce da sottoporre ai tre scenari. Le soluzioni e i modelli certificati sono conservati in un documento separato per evitare contaminazioni.")
    for text in [
        "Utilizzare lo stesso testo, senza semplificazioni o chiarimenti aggiuntivi, in tutti gli scenari.",
        "Registrare modello, snapshot, parametri, prompt di sistema, ora di inizio/fine e numero di tentativi.",
        "Richiedere sempre formulazione, codice Gurobi e soluzione nello stesso formato.",
        "Non mostrare il ground truth né i risultati di run precedenti al partecipante o al modello sotto test.",
    ]: doc.add_paragraph(text,style="List Bullet")
    add_summary_table(doc,records)
    doc.add_heading("Parte I — Difficoltà media",level=1)
    doc.add_paragraph("Dieci problemi con struttura combinatoria esplicita ma numero contenuto di relazioni logiche o temporali.")
    for rec in [x for x in records if x["difficulty"]=="Media"]:
        add_problem_header(doc,rec)
        for para in rec["intro"]: doc.add_paragraph(para)
        for table in rec["tables"]: add_data_table(doc,table)
        doc.add_heading("Consegna standard",level=2)
        add_numbered_items(doc,rec["request"])
    doc.add_heading("Parte II — Difficoltà elevata",level=1)
    doc.add_paragraph("Dieci problemi accoppiati agli stessi domini, con vincoli logici, relazioni dense, più periodi o risorse condivise.")
    for rec in [x for x in records if x["difficulty"]=="Elevata"]:
        add_problem_header(doc,rec)
        for para in rec["intro"]: doc.add_paragraph(para)
        for table in rec["tables"]: add_data_table(doc,table)
        doc.add_heading("Consegna standard",level=2)
        add_numbered_items(doc,rec["request"])
    out=ROOT/"Dataset_20_problemi_IP_MILP.docx"; doc.save(out); return out


def build_truth_doc(records: list[dict]) -> Path:
    doc=Document(); configure_document(doc,"Dataset sperimentale · Ground truth")
    add_cover(doc,"Ground truth e soluzioni certificate","Modelli di riferimento per i 20 problemi IP/MILP","Documento riservato",warning="RISERVATO — non somministrare a esperto o LLM durante le prove")
    doc.add_heading("Metodo di certificazione",level=1)
    doc.add_paragraph("Ogni istanza è stata costruita come modello lineare intero o misto-intero, risolta con HiGHS e sottoposta a un ricalcolo indipendente di funzione obiettivo e vincoli. Il file ground_truth.json contiene la matrice completa del modello; verify_with_gurobi.py permette di ricostruirla e certificarla nuovamente con Gurobi.")
    doc.add_paragraph("La soluzione riportata è una soluzione ottima. Se esistono ottimi alternativi, una risposta diversa è corretta quando supera tutti i vincoli e raggiunge lo stesso valore obiettivo entro la tolleranza prevista.")
    add_summary_table(doc,records,include_objective=True)
    for idx,rec in enumerate(records):
        add_problem_header(doc,rec,page_break=(idx == 0 or rec["id"] == "H01"))
        sol=rec["solution"]; s=rec["structural_size"]
        doc.add_paragraph(f"Ottimo certificato: {fmt_num(sol['objective'])} · Stato: {sol['status']} · Violazione massima: {sol['max_constraint_violation']:.2e}",style="Problem Meta")
        doc.add_paragraph("Modello numerico completo: record corrispondente in ground_truth.json.",style="Problem Meta")
        if rec.get("notes"):
            for note in rec["notes"]: doc.add_paragraph("Nota: "+note)
        doc.add_heading("Struttura del modello",level=2)
        doc.add_paragraph(rec["difficulty_rationale"])
        add_data_table(doc,{"title":"Famiglie di variabili","headers":["Simbolo","Dominio","Numero","Esempi"],"rows":variable_groups(rec)},font_size=8.5)
        add_data_table(doc,{"title":"Famiglie di vincoli","headers":["Famiglia","Numero"],"rows":constraint_families(rec)},font_size=8.5)
        doc.add_heading("Soluzione ottima di riferimento",level=2)
        add_solution_table(doc,sol["nonzero_values"])
    out=ROOT/"Ground_truth_20_problemi_IP_MILP.docx"; doc.save(out); return out


def write_readme(records: list[dict]) -> None:
    text="""# Dataset sperimentale — Capitolo 4

Questa cartella contiene 20 problemi IP/MILP originali e deterministici: 10 di difficoltà media e 10 di difficoltà elevata, organizzati in coppie per dominio.

## File da usare

- `Dataset_20_problemi_IP_MILP.docx`: tracce da somministrare nei tre scenari.
- `Ground_truth_20_problemi_IP_MILP.docx`: soluzioni riservate e riepilogo dei modelli.
- `problems.jsonl`: versione machine-readable delle sole tracce.
- `prompts/M01.md` … `prompts/H10.md`: un prompt autonomo per ogni istanza.
- `ground_truth.json`: matrice completa di variabili, funzione obiettivo, vincoli e soluzione.
- `solutions_summary.csv`: riepilogo degli ottimi e delle dimensioni.
- `verify_with_gurobi.py`: ricostruzione e soluzione con Gurobi.
- `build_dataset.py`: sorgente deterministica e certificazione HiGHS.

## Regola anti-contaminazione

Durante i test distribuire soltanto il DOCX delle tracce oppure il singolo file nella cartella `prompts`. Non mostrare `ground_truth.json`, il Word delle soluzioni o output di run precedenti.

## Riproduzione

Con Gurobi installato:

```bash
python verify_with_gurobi.py
python verify_with_gurobi.py --id H03
```

Le risposte non devono necessariamente coincidere con il vettore salvato: un ottimo alternativo è valido se è ammissibile e raggiunge lo stesso valore obiettivo entro tolleranza.
"""
    (ROOT/"README.md").write_text(text,encoding="utf-8")


def main() -> None:
    public=[]
    for line in (ROOT/"problems.jsonl").read_text(encoding="utf-8").splitlines(): public.append(json.loads(line))
    truth=json.loads((ROOT/"ground_truth.json").read_text(encoding="utf-8"))
    write_prompt_files(public); write_readme(truth)
    p1=build_public_doc(public); p2=build_truth_doc(truth)
    print(p1); print(p2)


if __name__=="__main__": main()
