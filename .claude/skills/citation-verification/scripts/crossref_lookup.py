"""Purpose: look up bibliographic metadata on Crossref for citation verification.
Inputs: one or more title queries as arguments.  Output: top-2 matches per query (title, authors, venue, vol, issue, pages, date, DOI).
Run: .venv/Scripts/python .claude/skills/citation-verification/scripts/crossref_lookup.py "Title one" "Title two"
"""

import json, sys, urllib.parse, urllib.request

for q in sys.argv[1:]:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {
            "query.bibliographic": q,
            "rows": 2,
            "select": "DOI,title,author,container-title,page,volume,issue,published",
        }
    )
    try:
        d = json.load(
            urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "paper-check"}),
                timeout=60,
            )
        )
    except Exception as e:
        print("##", q, "-> error", e)
        continue
    print("##", q)
    for it in d["message"]["items"]:
        a = ", ".join(
            (x.get("given", "") + " " + x.get("family", "")).strip()
            for x in it.get("author", [])
        )
        print(
            "  -",
            it.get("title"),
            "|",
            a,
            "|",
            it.get("container-title"),
            "| vol",
            it.get("volume"),
            "iss",
            it.get("issue"),
            "pp",
            it.get("page"),
            "|",
            it.get("published", {}).get("date-parts"),
            "|",
            it["DOI"],
        )
