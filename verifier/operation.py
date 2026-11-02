from dataclasses import asdict

from .checks import destination_problem, encoded, identifier, result, safe_path


def input_problem(v):
    problem = destination_problem(v.destination)
    if problem:
        return problem
    if len(v.lots) > 100 or not 0 <= v.quantity <= 1000000 or not 0 <= v.ship_day <= 365000:
        return "quantity, shipment day, or lot count is out of bounds"
    if len({r.lot_id for r in v.lots}) != len(v.lots):
        return "lot identifiers must be unique"
    if any(not identifier(r.lot_id) or not 0 <= r.expires_day <= 365000 or not 0 <= r.units <= 1000000 for r in v.lots):
        return "invalid lot identifier, expiry, or quantity"
    return None


def verify_input(value):
    problem = input_problem(value)
    return result(not problem, problem or "input is valid")


def expected(v):
    eligible = [r for r in v.lots if r.expires_day >= v.ship_day]
    rows = []
    for lot in sorted(eligible, key=lambda r: (r.expires_day, r.lot_id)):
        preceding = sum(r.units for r in eligible if (r.expires_day, r.lot_id) < (lot.expires_day, lot.lot_id))
        take = min(lot.units, max(0, v.quantity - preceding))
        if take:
            rows.append({"lot_id": lot.lot_id, "units": take})
    return rows, max(0, v.quantity - sum(r.units for r in eligible))


def verify_output(input_value, output_value, workspace):
    problem = input_problem(input_value)
    if problem:
        return result(False, problem)
    rows, total = expected(input_value)
    actual = [asdict(r) for r in output_value.records]
    if actual != rows or output_value.total != total:
        return result(False, "returned rows or total do not match the task rules")
    if output_value.path != input_value.destination:
        return result(False, "returned path does not match destination")
    path = safe_path(workspace, input_value.destination)
    if path is None or not path.is_file():
        return result(False, "artifact is missing, is a symlink, or escapes the workspace")
    try:
        content = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError):
        return result(False, "artifact cannot be read as UTF-8")
    if content != encoded(rows, total):
        return result(False, "artifact is not the exact canonical JSON result")
    return result(True, "verified rows, total, destination, and artifact bytes", rows=len(rows), total=total)


def verify_task(arguments, output, reference, workspace):
    return verify_output(arguments, output, workspace)
