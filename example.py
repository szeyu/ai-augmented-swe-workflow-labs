"""Basic order lifecycle demo — works with the partial stub (no guards, single from_state)."""

from state_machine import StateMachine

sm = StateMachine(initial="draft")

sm.transition("submit", from_state="draft", to_state="submitted")
sm.transition("process", from_state="submitted", to_state="processing")
sm.transition("ship", from_state="processing", to_state="shipped")
sm.transition("deliver", from_state="shipped", to_state="delivered")

print("=== Happy path (stub — guards and actions not evaluated) ===")
print(f"State: {sm.current_state}")

for event in ["submit", "process", "ship", "deliver"]:
    result = sm.send(event, {})
    if result.accepted:
        print(f"[OK]   {result.from_state} --{event}--> {result.to_state}")
    else:
        print(f"[FAIL] {event}: {result.reason}")

print(f"Final state: {sm.current_state}")

print("\n=== Wrong state rejection ===")
result = sm.send("submit", {})
print(f"Rejected: {result.reason}")
