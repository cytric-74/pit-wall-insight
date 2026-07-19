"""Data collectors — the only ingestion layer allowed to talk to an external
Formula One data source (FastF1, Jolpica-F1/Ergast).

docs/06_DATA_ENGINEERING.md is explicit about this layer's contract:
"Collectors never modify data." In practice that means every function in
`fastf1_client.py` and `ergast_client.py` does only the mechanical work of
calling an upstream API and flattening its native response shape (a pandas
DataFrame row, a nested Ergast `MRData` JSON envelope) into a plain
`dict[str, Any]` — no type coercion, no dropping of "invalid-looking"
fields, no schema enforcement. That responsibility belongs one layer up, in
`validators/`, which can reject a single bad record without losing the rest
of the batch. A collector raising on a single malformed upstream record
would be a validation decision leaking into a layer that isn't supposed to
make one.
"""
