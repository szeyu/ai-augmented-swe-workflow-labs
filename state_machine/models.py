from dataclasses import dataclass, field
from typing import Callable, Any, Optional


@dataclass
class Transition:
    name: str
    from_states: list
    to_state: str
    guard: Optional[str] = None
    action: Optional[Callable[[dict], Any]] = None
    description: str = ""
    _parsed_guard: Any = field(default=None, repr=False, compare=False, init=False)


@dataclass
class HistoryEntry:
    event: str
    from_state: str
    to_state: str
    transition_name: str


@dataclass
class TransitionResult:
    accepted: bool
    event: str
    from_state: str
    to_state: Optional[str]
    transition_name: Optional[str] = None
    reason: Optional[str] = None
