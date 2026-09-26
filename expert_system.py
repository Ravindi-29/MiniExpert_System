from enum import Enum
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Union
from datetime import datetime
import json


class Operator(Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class Condition:
    fact: str
    operator: Operator
    value: Any

    def evaluate(self, fact_value: Any) -> bool:
        op = self.operator
        if op == Operator.EQUALS: return fact_value == self.value
        if op == Operator.NOT_EQUALS: return fact_value != self.value
        if op == Operator.GREATER_THAN: return fact_value > self.value
        if op == Operator.LESS_THAN: return fact_value < self.value
        if op == Operator.GREATER_EQUAL: return fact_value >= self.value
        if op == Operator.LESS_EQUAL: return fact_value <= self.value
        if op == Operator.IN: return fact_value in self.value
        if op == Operator.NOT_IN: return fact_value not in self.value
        return False


@dataclass
class Action:
    fact: str
    value: Any


@dataclass
class Rule:
    rule_id: str
    name: str
    conditions: List[Condition]
    actions: List[Action]
    priority: int = 1
    confidence: float = 1.0
    logic: str = "AND"  # "AND" or "OR"


@dataclass
class FactValue:
    value: Any
    confidence: float = 1.0


class EnterpriseExpertSystem:
    def __init__(self):
        self.facts: Dict[str, FactValue] = {}
        self.rules: List[Rule] = []
        self.fired_rules: List[str] = []
        self.audit_log: List[Dict[str, Any]] = []

    def set_fact(self, key: str, value: Any, confidence: float = 1.0):
        """Sets or combines certainty factor for a fact using MYCIN combination logic."""
        confidence = max(0.0, min(1.0, confidence))  # Clamp between 0.0 and 1.0

        if key in self.facts:
            # Combine certainty factors if fact value matches
            if self.facts[key].value == value:
                cf1 = self.facts[key].confidence
                cf2 = confidence
                combined_cf = cf1 + cf2 * (1.0 - cf1)
                self.facts[key].confidence = round(combined_cf, 3)
            else:
                # Overwrite if value differs and new confidence is higher
                if confidence > self.facts[key].confidence:
                    self.facts[key] = FactValue(value=value, confidence=confidence)
        else:
            self.facts[key] = FactValue(value=value, confidence=confidence)

        self._log("FACT_SET", f"Fact '{key}' set to '{value}' with CF={self.facts[key].confidence}")

    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def load_rules_from_json(self, json_data: Union[str, List[Dict]]):
        """Parses and loads JSON rule definitions."""
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        for r in data:
            conditions = [
                Condition(
                    fact=c["fact"],
                    operator=Operator(c["op"]),
                    value=c["val"]
                ) for c in r["conditions"]
            ]
            actions = [Action(fact=a["fact"], value=a["val"]) for a in r["actions"]]
            
            self.add_rule(Rule(
                rule_id=r["id"],
                name=r["name"],
                conditions=conditions,
                actions=actions,
                priority=r.get("priority", 1),
                confidence=r.get("confidence", 1.0),
                logic=r.get("logic", "AND").upper()
            ))

    def _eval_rule(self, rule: Rule) -> tuple[bool, float]:
        """Evaluates rule logic and calculates cumulative Certainty Factor."""
        matched_cfs = []

        for cond in rule.conditions:
            if cond.fact not in self.facts:
                if rule.logic == "AND":
                    return False, 0.0
                continue  # Skip for OR logic

            fact_entry = self.facts[cond.fact]
            is_met = cond.evaluate(fact_entry.value)

            if is_met:
                matched_cfs.append(fact_entry.confidence)
            elif rule.logic == "AND":
                return False, 0.0

        if not matched_cfs:
            return False, 0.0

        # Calculate rule certainty
        base_cf = min(matched_cfs) if rule.logic == "AND" else max(matched_cfs)
        rule_cf = round(base_cf * rule.confidence, 3)
        return True, rule_cf

    def run(self, auto_prompt: bool = False):
        """Forward chaining loop with support for dynamic prompts."""
        executed = True
        while executed:
            executed = False
            for rule in self.rules:
                if rule.rule_id in self.fired_rules:
                    continue

                is_met, rule_cf = self._eval_rule(rule)

                if is_met:
                    for action in rule.actions:
                        self.set_fact(action.fact, action.value, rule_cf)

                    self.fired_rules.append(rule.rule_id)
                    self._log("RULE_FIRED", f"Rule [{rule.rule_id}] '{rule.name}' fired (CF: {rule_cf})")
                    executed = True
                    break  # Re-evaluate rule priorities

    def _log(self, event_type: str, details: str):
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "details": details
        })

    def explain(self):
        """Prints a structured execution log."""
        print("\n================ SYSTEM EXPLANATION TRAIL ================")
        for log in self.audit_log:
            time_str = log["timestamp"].split("T")[1][:8]
            print(f"[{time_str}] [{log['event']}] {log['details']}")
        print("==========================================================\n")

    def reset(self):
        """Resets working memory for clean reuse."""
        self.facts.clear()
        self.fired_rules.clear()
        self.audit_log.clear()


# =====================================================================
# DEMO EXECUTION
# =====================================================================

RULES_CONFIG = [
    {
        "id": "R1",
        "name": "Identify Local Network Outage",
        "priority": 10,
        "confidence": 1.0,
        "logic": "AND",
        "conditions": [{"fact": "connected_to_wifi", "op": "==", "val": False}],
        "actions": [{"fact": "issue", "val": "Local Network Failure"}]
    },
    {
        "id": "R2",
        "name": "Check Router Power Supply",
        "priority": 20,
        "confidence": 0.95,
        "logic": "AND",
        "conditions": [
            {"fact": "issue", "op": "==", "val": "Local Network Failure"},
            {"fact": "router_powered", "op": "==", "val": False}
        ],
        "actions": [{"fact": "recommendation", "val": "Verify the router power cable is firmly plugged in."}]
    },
    {
        "id": "R3",
        "name": "Check ISP Status",
        "priority": 20,
        "confidence": 0.90,
        "logic": "AND",
        "conditions": [
            {"fact": "issue", "op": "==", "val": "Local Network Failure"},
            {"fact": "router_powered", "op": "==", "val": True}
        ],
        "actions": [{"fact": "recommendation", "val": "Reboot router and check ISP service status."}]
    },
    {
        "id": "R4",
        "name": "Identify DNS Failure",
        "priority": 15,
        "confidence": 0.85,
        "logic": "AND",
        "conditions": [
            {"fact": "connected_to_wifi", "op": "==", "val": True},
            {"fact": "can_access_sites", "op": "==", "val": False}
        ],
        "actions": [{"fact": "recommendation", "val": "DNS Issue. Switch your DNS server to 8.8.8.8."}]
    }
]


def main():
    engine = EnterpriseExpertSystem()
    engine.load_rules_from_json(RULES_CONFIG)

    print("--- Enterprise Expert System Engine ---")

    # Set facts with variable confidences
    engine.set_fact("connected_to_wifi", False, confidence=1.0)
    engine.set_fact("router_powered", True, confidence=0.85)

    # Run inference
    engine.run()

    # Retrieve output
    rec_fact = engine.facts.get("recommendation")
    if rec_fact:
        print(f"\nDIAGNOSIS: {rec_fact.value}")
        print(f"CONFIDENCE SCORE: {rec_fact.confidence * 100:.1f}%")
    else:
        print("\nDIAGNOSIS: No issue identified.")

    # Show explanation trail
    engine.explain()


if __name__ == "__main__":
    main()