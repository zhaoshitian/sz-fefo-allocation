# FEFO Allocation

Allocate a shipment from unexpired lots in first-expiring-first-out order, with an explicit shortage.

## Tools

- `allocate_stock` accepts `TaskInput` and returns `TaskOutput`.
- `allocate-stock` is a `runner: tool` task using `allocate_stock`. It requires no model or external service. A RUSH Lab agent can select the task from its structured interface.

### Exact success conditions

Eligible means expires_day >= ship_day. Order lots by (expires_day, lot_id); consume each before the next. Omit zero allocations. total is the nonnegative shortage.

The tool creates a new file at `destination`. The exact file format is UTF-8 JSON of `{"records": [...], "total": integer}`, sorted object keys, compact separators `(',', ':')`, ASCII escapes, and one final newline. Returned records, total, and destination must match the file and the independently computed answer. A matching claim without a matching file fails. Existing files are never overwritten. Paths must be canonical relative `.json` paths, at most 200 characters, with identifier-style directories and filename stems; symlinks are rejected. Identifiers match `[A-Za-z0-9][A-Za-z0-9_-]{0,31}`. Input sizes and numeric bounds are declared in `contract.py` and enforced in `verifier/operation.py`.

The tool consumes a sorted queue. The verifier computes each allocation from the sum of all lexicographically preceding eligible lots.

### Example input

```json
{
  "destination": "results/out.json",
  "lots": [
    {
      "lot_id": "old",
      "expires_day": 9,
      "units": 99
    },
    {
      "lot_id": "B",
      "expires_day": 10,
      "units": 4
    },
    {
      "lot_id": "A",
      "expires_day": 10,
      "units": 3
    },
    {
      "lot_id": "C",
      "expires_day": 12,
      "units": 5
    }
  ],
  "quantity": 9,
  "ship_day": 10
}
```

## Layout

- `contract.py`: typed schemas and tool/task tables.
- `nanoagent.yaml`: tool runner, no network hosts, workspace-only writes.
- `src/plugin/`: MCP runtime and deterministic implementation.
- `verifier/`: independent deterministic checks; no LLM, clock, network, randomness, or writes.
- `tests/test_verifier.py`: known answers, adversarial outputs, boundaries, malformed inputs, artifact changes, and safe paths.
- `ui/` and `product/`: result schema rendering and marketplace presentation.
- `uv.lock`: pinned dependency versions and Git revision of slimconfig.

## Develop and run

Requires Python 3.12 or later, Git, uv, and NanoAgent implementing `nanoagent.plugin/v0001` (tested with the RUSH Lab bundled CLI). First-time dependency installation requires the package index and GitHub; execution requires no network or environment secrets.

```sh
uv sync --frozen --extra dev
uv run --frozen pytest -q
uv run --frozen ruff check .
uv lock --check
rushlab nanoagent plugin inspect .
```

To run: save the example as `/absolute/path/input.json`, then create a YAML file outside the repository:

```yaml
_ > nanoagent.cli.plugin.PluginRunConfig:
plugin: /absolute/path/sz-fefo-allocation
task: allocate-stock
arguments: /absolute/path/input.json
inputs: []
timeout: 60.0
```

Run `rushlab nanoagent plugin run config=/absolute/path/run.yaml home=/absolute/path/new-run-folder`.
The new run folder contains `workspace/results/out.json`, `result.json`, and `verdict.json`. A successful verifier returns `valid: true` and `score: 1.0`. Use a fresh run folder and destination for each run. Evidence and validation logs belong in the milestone report, outside this repository.

Limitations: Single product and single shipment; integer day and quantity units; no reservations, substitutions, or real inventory integration.
