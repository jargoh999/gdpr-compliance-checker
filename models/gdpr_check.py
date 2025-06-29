from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

class CheckStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    INFO = "INFO"
    ERROR = "ERROR"

@dataclass
class GDPRSolution:
    """Represents a solution for a GDPR compliance issue"""
    description: str
    code_snippet: str
    language: str = "javascript"
    complexity: str = "low"  # low, medium, high

@dataclass
class GDPRCheckResult:
    """Represents the result of a single GDPR check"""
    check_id: str
    check_name: str
    status: CheckStatus
    severity: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    solution: Optional[GDPRSolution] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary"""
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "status": self.status.value,
            "severity": self.severity,
            "description": self.description,
            "details": self.details,
            "solution": {
                "description": self.solution.description if self.solution else None,
                "code_snippet": self.solution.code_snippet if self.solution else None,
                "language": self.solution.language if self.solution else None,
                "complexity": self.solution.complexity if self.solution else None
            } if self.solution else None,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class GDPRReport:
    """Represents a complete GDPR compliance report"""
    url: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    results: List[GDPRCheckResult] = field(default_factory=list)
    
    def add_result(self, result: GDPRCheckResult) -> None:
        """Add a check result to the report"""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAILED)
        warnings = sum(1 for r in self.results if r.status == CheckStatus.WARNING)
        
        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "compliance_score": round((passed / total) * 100, 2) if total > 0 else 0,
            "url": self.url,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the report to a dictionary"""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.get_summary(),
            "results": [r.to_dict() for r in self.results]
        }
