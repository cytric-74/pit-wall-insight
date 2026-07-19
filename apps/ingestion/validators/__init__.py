"""Per-record schema validation (docs/06_DATA_ENGINEERING.md "Validators").

This layer sits between `collectors/` (which return loosely-typed raw
records, deliberately unvalidated) and the future bronze-loader phase
(which will only ever see records that already passed through here). Its
job is exactly what docs/06 assigns it: missing values, schema/type
validation, and (implicitly, by rejecting malformed records one at a time)
duplicate/invalid-timestamp detection at the individual-record level —
never at the batch level, because "Validation failures are logged. Pipeline
should continue where possible."
"""
