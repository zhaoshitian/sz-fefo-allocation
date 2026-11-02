from slimconfig import build_output

from contract import TaskOutput
from verifier.checks import encoded, safe_path
from verifier.operation import verify_input


def solve(v):
    remaining = v.quantity
    rows = []
    for lot in sorted(v.lots, key=lambda r: (r.expires_day, r.lot_id)):
        if lot.expires_day < v.ship_day:
            continue
        take = min(remaining, lot.units)
        if take:
            rows.append({"lot_id": lot.lot_id, "units": take})
        remaining -= take
    return rows, remaining


def operate(value, workspace):
    verdict = verify_input(value)
    if not verdict["valid"]:
        raise ValueError(verdict["message"])
    path = safe_path(workspace, value.destination)
    if path is None:
        raise ValueError("destination crosses a symlink or leaves the workspace")
    rows, total = solve(value)
    output = build_output({"path": value.destination, "records": rows, "total": total}, TaskOutput)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded(rows, total))
    return output
