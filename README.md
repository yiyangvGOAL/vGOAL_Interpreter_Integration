# vGOAL Interpreter — Real-World Version (Integration)

**Real-world version** of the vGOAL agent-reasoning interpreter. It drives **physical
AMRs (Autonomous Mobile Robots)**: it reads each robot's live state over a ROS rosbridge
WebSocket and sends the decided actions back to the robot to execute.

> ⚠️ **This version requires real AMR hardware** and cannot run offline (see "Runtime
> requirements"). For logic comparison / offline testing use
> `../vGOAL_Interpreter_SAT_V2/` (which reads pre-recorded trace files). The two
> `Interpreter.py` files are **logically identical except for the input source**.

## Dependencies
- `python3.9`
- `pysat` (`from pysat.formula import CNF` / `from pysat.solvers import Solver`)
- `ws4py` (WebSocket client for ROS rosbridge)
```bash
/opt/homebrew/bin/python3.9 -c "import pysat, ws4py; print('ok')"
```

## Runtime requirements (real AMRs)
- Three AMRs with IDs **14 / 15 / 16** (mapped to agents A1 / A2 / A3).
- Each robot reachable on the network, running ROS rosbridge at
  `ws://172.21.<id>.90:9090/` (see `amr_agent.py`).
- Robots at/near their initial poses: AMR14→P3, AMR15→P4, AMR16→P5
  (`Interpreter.py` calls `set_init_pose` on startup).

> **Important:** `import Interpreter` immediately runs `AMR_Agent(14/15/16).connect()` to
> all three robots. **Without the robots present, the import blocks until it times out** —
> which is why this version cannot be run offline.

## Directory structure

**Interpreter core**
- `Interpreter.py` — the interpreter (same reasoning logic as the test version): reasoning
  cycle, least-fixpoint derivation, action/event/communication analysis, SAT cross-check
  (`_sat_verify`). **At module load** it creates and connects `AMR14/15/16` and calls
  `set_init_pose` on each; after a decision is generated it dispatches it to the robot via
  `AMRxx.send_action(...)`.
- `Interpreter_Improved.py` / `Interpreter_V1.py` — alternative/legacy variants
  (self-contained; not imported by the main entry point).

**Robot interface**
- `amr_agent.py` — `AMR_Agent(WebSocketClient)`: connects to
  `ws://172.21.<amr_id>.90:9090/`, subscribes to robot state, sends actions / initial pose.

**Specs + entry points**
- `AMR_Spec.py` — AMR delivery spec (nullary holding), `Agents=[A1,A2,A3,C]`; `main()`
  calls `DG.interpreter(...)`. Launch directly with `python3.9 AMR_Spec.py`
  (`if __name__ == '__main__': main()`).
- `SimpleExample.py` — a simpler example spec.

**Other**
- `Interpreter.py.prerename.bak` — backup of the interpreter from before it was synced with
  the test version (rollback point).
- `Record*.txt` — run records / timing.

## How to run
1. Ensure the three AMRs (14/15/16) are powered on, networked, running rosbridge, and near
   their initial poses.
2. Run:
```bash
/opt/homebrew/bin/python3.9 AMR_Spec.py
```
   On import it connects to the robots, then each reasoning cycle generates safe decisions
   for the robots and dispatches them over WebSocket (e.g. `A1 pickup(1)`), until there are
   no active goals.

## Consistency with the test version (SAT_V2)
The two are identical apart from the input source:
- **Same**: function names (`least_fixpoint` / `pattern_match` / `process_beliefs`),
  performance infrastructure (`_fast_deepcopy` / `_memoize_pure`), bug fixes (arity-aware
  unification, empty-body CNF, `fully_instantiated_rep` guard, bare-holding guard,
  `state_transformer` guard), SAT structure (`_sat_verify`, 4 sites), and cleanups.
- **Different (= the input)**: this version reads live sensors from the robots via
  `amr_agent`; the test version reads `MG_*.txt` / `STORY_*.txt` (the
  `info_parse` / `sensor_files` / reactive-sensor machinery exists only in the test version).
- One retained difference: `transform_vGOAL_to_CNF` uses the more complete
  `premise` + `multiply_list` encoding here vs. the simplified form in the test version
  (both carry the empty-body fix).
