from typing import Callable, Optional, Union

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
        if isinstance(from_state, list):
            raise TypeError("from_state as list is not yet supported")

        self._transitions = [
            t
            for t in self._transitions
            if not (t.name == name and from_state in t.from_states)
        ]

        t = Transition(
            name=name,
            from_states=[from_state],
            to_state=to_state,
            guard=guard,
            action=action,
            description=description,
        )
        self._transitions.append(t)
        return self

    def send(self, event: str, context: dict) -> TransitionResult:
        for t in self._transitions:
            if t.name == event and self._current in t.from_states:
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
            reason=(
                f"No matching transition for event '{event}' "
                f"from state '{self._current}'"
            ),
        )
