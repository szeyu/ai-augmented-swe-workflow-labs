from typing import Callable, Optional, Union

from .evaluator import EvaluationError, evaluate_parsed, parse_condition
from .models import Transition, TransitionResult


class StateMachine:
    """Partial stub per requirements.pdf §3 — basic registration and send only."""

    def __init__(self, initial: str):
        self._initial = initial
        self._current = initial
        self._transitions: list = []

    @property
    def current_state(self) -> str:
        return self._current

    @property
    def history(self) -> list:
        return []

    @property
    def states(self) -> set[str]:
        result = {self._initial}
        for t in self._transitions:
            result.update(t.from_states)
            result.add(t.to_state)
        return result

    def transition(
        self,
        name: str,
        *,
        from_state: Union[str, list],
        to_state: str,
        guard: Optional[str] = None,
        action: Optional[Callable] = None,
        description: str = "",
    ) -> "StateMachine":
        if isinstance(from_state, str):
            from_states = [from_state]
        else:
            from_states = list(from_state)

        if not from_states:
            raise ValueError("from_state must not be empty")

        for existing in self._transitions:
            if existing.name != name:
                continue
            overlap = set(existing.from_states) & set(from_states)
            if overlap:
                raise ValueError(
                    f"Transition '{name}' already registered from state(s) "
                    f"{sorted(overlap)}"
                )

        parsed_guard = None
        if guard is not None:
            try:
                parsed_guard = parse_condition(guard)
            except ValueError as e:
                raise ValueError(
                    f"Invalid guard for transition '{name}': {e}"
                ) from e

        t = Transition(
            name=name,
            from_states=from_states,
            to_state=to_state,
            guard=guard,
            action=action,
            description=description,
        )
        if parsed_guard is not None:
            t._parsed_guard = parsed_guard

        self._transitions.append(t)
        return self

    def send(self, event: str, context: dict) -> TransitionResult:
        if not isinstance(context, dict):
            return TransitionResult(
                accepted=False,
                event=event,
                from_state=self._current,
                to_state=None,
                reason="Invalid context: context must be a dict",
            )

        for t in self._transitions:
            if t.name != event or self._current not in t.from_states:
                continue

            if t._parsed_guard is not None:
                try:
                    guard_passed = evaluate_parsed(t._parsed_guard, context)
                except EvaluationError as e:
                    return TransitionResult(
                        accepted=False,
                        event=event,
                        from_state=self._current,
                        to_state=None,
                        reason=f"Guard error: {e}",
                    )
                if not guard_passed:
                    return TransitionResult(
                        accepted=False,
                        event=event,
                        from_state=self._current,
                        to_state=None,
                        reason=f"Guard condition not met: {t.guard}",
                    )

            old_state = self._current
            self._current = t.to_state
            return TransitionResult(
                accepted=True,
                event=event,
                from_state=old_state,
                to_state=t.to_state,
                transition_name=t.name,
            )

        return TransitionResult(
            accepted=False,
            event=event,
            from_state=self._current,
            to_state=None,
            reason=f"No transition '{event}' from state '{self._current}'",
        )
