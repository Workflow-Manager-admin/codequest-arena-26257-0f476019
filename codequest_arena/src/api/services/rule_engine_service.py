"""
Service logic for Rule Engine: admin-configurable code quality/static analysis rules.

Handles:
- Defining rules (code quality, static analysis, process policy)
- CRUD operations for rules (in-memory, for now)
- DTOs for rules

Classes:
    - RuleSeverity: Enum of rule severities
    - RuleType: Enum of rule types
    - RuleDTO: DTO for a rule
    - RuleEngineService: Service for managing rules
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import threading
import uuid


# PUBLIC_INTERFACE
class RuleSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# PUBLIC_INTERFACE
class RuleType(str, Enum):
    CODE_QUALITY = "CODE_QUALITY"
    STATIC_ANALYSIS = "STATIC_ANALYSIS"
    PROCESS_POLICY = "PROCESS_POLICY"


# PUBLIC_INTERFACE
class RuleDTO(BaseModel):
    """
    Data transfer object for a policy/rule.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str]
    severity: RuleSeverity
    type: RuleType
    config: Optional[Dict[str, Any]] = None  # Arbitrary config dict
    enabled: bool = True

    class Config:
        schema_extra = {
            "example": {
                "id": "e3a8b9c7-f580-41b9-97ad-735bbb4762f5",
                "name": "No TODO comments",
                "description": "Prevents TODO comments in committed code.",
                "severity": "LOW",
                "type": "CODE_QUALITY",
                "config": {"pattern": "TODO"},
                "enabled": True
            }
        }


# PUBLIC_INTERFACE
class RuleEngineService:
    """
    Service for admin-configurable rule management.
    NOTE: Storage is in-memory; replace with DB in production.
    Threadsafe via a lock for demo purposes.
    """
    _lock = threading.Lock()
    _rules: Dict[str, RuleDTO] = {}

    def __init__(self):
        # Seed some rules if empty
        with self._lock:
            if not self._rules:
                rule1 = RuleDTO(
                    name="No TODO Comments",
                    description="Disallow committing TODO comments.",
                    severity=RuleSeverity.LOW,
                    type=RuleType.CODE_QUALITY,
                    config={"pattern": "TODO"},
                    enabled=True,
                )
                rule2 = RuleDTO(
                    name="Max File Length",
                    description="Warn if file exceeds 500 lines.",
                    severity=RuleSeverity.MEDIUM,
                    type=RuleType.STATIC_ANALYSIS,
                    config={"max_lines": 500},
                    enabled=True,
                )
                self._rules[rule1.id] = rule1
                self._rules[rule2.id] = rule2

    # PUBLIC_INTERFACE
    def list_rules(self) -> List[RuleDTO]:
        """List all rules."""
        with self._lock:
            return list(self._rules.values())

    # PUBLIC_INTERFACE
    def get_rule(self, rule_id: str) -> Optional[RuleDTO]:
        """Get a rule by its ID."""
        with self._lock:
            return self._rules.get(rule_id)

    # PUBLIC_INTERFACE
    def create_rule(self, rule: RuleDTO) -> RuleDTO:
        """Add a new rule."""
        with self._lock:
            self._rules[rule.id] = rule
            return rule

    # PUBLIC_INTERFACE
    def update_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> Optional[RuleDTO]:
        """Update an existing rule."""
        with self._lock:
            rule = self._rules.get(rule_id)
            if not rule:
                return None
            rule_for_update = rule.copy(update=rule_data, deep=True)
            rule_for_update.id = rule_id  # Don't allow ID overwrite
            self._rules[rule_id] = rule_for_update
            return rule_for_update

    # PUBLIC_INTERFACE
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule by its ID."""
        with self._lock:
            return self._rules.pop(rule_id, None) is not None
