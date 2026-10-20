# Literature corpus for the loop agents

Each agent reads `common.md` plus its own role file at the start of a step. The lists are *starting
points*: broad reviews and the key primary papers. Agents are expected to search (WebSearch, arXiv,
INSPIRE `https://inspirehep.net/api/literature?q=refersto:arxiv:<id>` for citing papers) and follow
citations to the specific formalism or analysis they need. References were checked against INSPIRE
(authors, title, journal, arXiv id) when the lists were written (2026-10).

Reading full texts: `https://arxiv.org/abs/<id>` (abstract), `https://arxiv.org/pdf/<id>` (PDF).
