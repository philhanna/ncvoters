from dataclasses import dataclass, field


@dataclass
class Configuration:
    selected_columns: list[str]
    sanitize_columns: list[str]


@dataclass
class Column:
    name: str
    data_type: str
    description: str


@dataclass
class Layout:
    all_columns: list[Column] = field(default_factory=list)
    status_codes: dict[str, str] = field(default_factory=dict)
    race_codes: dict[str, str] = field(default_factory=dict)
    ethnic_codes: dict[str, str] = field(default_factory=dict)
    county_codes: dict[int, str] = field(default_factory=dict)
    reason_codes: dict[str, str] = field(default_factory=dict)
