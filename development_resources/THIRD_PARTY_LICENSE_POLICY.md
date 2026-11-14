# Third-party code and data policy
Original ATIAF code and docs: **MIT**. That does not override others' licenses. For each integrated component record upstream license, text, commit/version, attribution obligations, and whether commercial use, modification, bundling and redistribution are allowed.

- **IDB:** public browsing/free-ish does not equal permission to ship the entire API data. Its API terms prohibit distributing full data sets to third parties. Reference/link individual items as permitted; do not harvest and redistribute full records. Mentioning the site does not grant redistribution rights.
- **Awesome Spectral Indices:** open MIT project; use pinned/reviewed releases and preserve license/attribution, scientific citations. V1 is under active schema migration, so do not auto-sync unreviewed formulas into production.
- **Sensor image data:** do not bundle original ASTER, EnMAP, PRISMA, EMIT or other scene files into the software without explicit redistribution permission. Link official free download portals instead.
- **GPL applications:** QGIS/EnMAP-Box have different license obligations. Independently installed host applications and programmatic integration differ from copying their code into MIT components. Review redistribution/legal compatibility for any actual code reuse.
- **Vendor SDKs:** ArcGIS Pro/ArcPy provided by user's licensed host; do not bundle Esri binaries.
- **Security:** no hidden telemetric uploads, no credentials in a ZIP or public Git, no automatic execution of external repository setup scripts.
