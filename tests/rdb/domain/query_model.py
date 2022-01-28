from dataclasses import dataclass, field


@dataclass
class MemoQuery:
    id: int = field(init=False)
    content: str
