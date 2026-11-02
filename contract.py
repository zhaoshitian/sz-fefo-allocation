"""Typed input and output declarations for FEFO Allocation."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    RUN = "allocate_stock"


class Task(Enum):
    RUN = "allocate-stock"


@dataclass
class Lot(Output):
    lot_id: Annotated[str, "Unique lot identifier"]
    expires_day: Annotated[int, "Last usable integer day, inclusive"]
    units: Annotated[int, "Available nonnegative units"]


@dataclass
class ResultRow(Output):
    lot_id: Annotated[str, "Allocated lot identifier"]
    units: Annotated[int, "Positive quantity taken from the lot"]


@dataclass
class TaskInput(Output):
    lots: Annotated[list[Lot], "At most 100 uniquely identified lots"]
    quantity: Annotated[int, "Requested units, from 0 through 1000000"]
    ship_day: Annotated[int, "Shipment day from 0 through 365000"]
    destination: Annotated[str, "New relative .json output path, never overwritten"]


@dataclass
class TaskOutput(Output):
    path: Annotated[str, "Artifact path matching destination"]
    records: Annotated[list[ResultRow], "Complete ordered task results"]
    total: Annotated[int, "Unfilled units after consuming all eligible lots"]


TOOLS = {Tool.RUN: (TaskInput, TaskOutput)}
TASKS = {Task.RUN: (TaskInput, TaskOutput)}
