from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import json
import time

class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class Diagnostic:
    severity: Severity
    file_path: str
    line: int
    col: int
    message: str
    snippet: str = ""

    def to_dict(self):
        return {
            "severity": self.severity.value,
            "file": self.file_path,
            "line": self.line,
            "col": self.col,
            "message": self.message,
            "snippet": self.snippet
        }

class SourceManager:
    def __init__(self):
        self.files = {} # path -> lines

    def load_file(self, path: str) -> str:
        try:
            with open(path, 'r') as f:
                content = f.read()
            self.files[path] = content.splitlines()
            return content
        except FileNotFoundError:
            return ""

    def get_line(self, path: str, line_idx: int) -> str:
        lines = self.files.get(path, [])
        if 0 <= line_idx < len(lines):
            return lines[line_idx]
        return ""

class DiagnosticsEngine:
    def __init__(self):
        self.diagnostics: List[Diagnostic] = []

    def report(self, diag: Diagnostic):
        self.diagnostics.append(diag)

    def has_errors(self) -> bool:
        return any(d.severity == Severity.ERROR for d in self.diagnostics)

    def to_json(self):
        return [d.to_dict() for d in self.diagnostics]

@dataclass
class Timer:
    stage: str
    start_time: float = field(default_factory=time.time)
    duration_ms: float = 0.0

    def stop(self):
        self.duration_ms = (time.time() - self.start_time) * 1000

class ResultManifest:
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        self.status = "success"
        self.artifacts = {}
        self.timings = {}
        self.diagnostics = []

    def add_artifact(self, key: str, path: str):
        self.artifacts[key] = path

    def add_timing(self, stage: str, ms: float):
        self.timings[stage] = round(ms, 2)

    def save(self):
        data = {
            "status": self.status,
            "diagnostics": self.diagnostics,
            "artifacts": self.artifacts,
            "timings": self.timings,
            "timestamp": time.time()
        }
        with open(f"{self.out_dir}/result.json", "w") as f:
            json.dump(data, f, indent=2)
