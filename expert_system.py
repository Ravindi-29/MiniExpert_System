import json
from datetime import datetime


class Rule:
    """Represents a structured IF-THEN production rule with priority and certainty."""

    def __init__(self, rule_id, name, conditions, actions, priority=1, confidence=1.0):
        self.rule_id = rule_id
        self.name = name
        self.conditions = conditions  # List of dicts: [{"fact": k, "op": "==", "val": v}]
        self.actions = actions        # List of dicts: [{"fact": k, "val": v}]
        self.priority = priority      # Conflict resolution priority
        self.confidence = confidence  # Certainty Factor multiplier


class AdvancedExpertSystem:
    def __init__(self):
        self.facts = {}
        self.fact_confidences = {}
        self.rules = []
        self.fired_rules = []
        self.audit_log = []

    def set_fact(self, key, value, confidence=1.0):
        """Add or update a fact with a certainty factor (0.0 to 1.0)."""
        self.facts[key] = value
        self.fact_confidences[key] = confidence
        self.audit_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FACT SET: {key} = {value} (cf={confidence})")

    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        # Higher priority rules run first
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def load_rules_from_json(self, json_data):
        """Load externalized JSON rule definitions."""
        rules_list = json.loads(json_data) if isinstance(json_data, str) else json_data
        for r in rules_list:
            self.add_rule(
                Rule(
                    rule_id=r["id"],
                    name=r["name"],
                    conditions=r["conditions"],
                    actions=r["actions"],
                    priority=r.get("priority", 1),
                    confidence=r.get("confidence", 1.0),
                )
            )

    def _eval_condition(self, cond):
        fact_key = cond["fact"]
        op = cond["op"]
        target_val = cond["val"]

        if fact_key not in self.facts:
            return False

        fact_val = self.facts[fact_key]
        if op == "==": return fact_val == target_val
        if op == "!=": return fact_val != target_val
        if op == ">": return fact_val > target_val
        if op == "<": return fact_val < target_val
        if op == "in": return fact_val in target_val
        return False

    def run(self):
        """Forward Chaining Engine with Agenda Conflict Resolution."""
        executed = True
        while executed:
            executed = False
            for rule in self.rules:
                if rule.rule_id in self.fired_rules:
                    continue  # Refractory period: Prevent infinite loops

                # Evaluate all IF conditions
                all_met = all(self._eval_condition(cond) for cond in rule.conditions)

                if all_met:
                    # Calculate cumulative certainty factor
                    cond_cfs = [self.fact_confidences.get(c["fact"], 1.0) for c in rule.conditions]
                    rule_cf = min(cond_cfs) * rule.confidence

                    # Apply actions
                    for act in rule.actions:
                        self.set_fact(act["fact"], act["val"], round(rule_cf, 2))

                    self.fired_rules.append(rule.rule_id)
                    self.audit_log.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] RULE FIRED: [{rule.rule_id}] {rule.name} (CF: {rule_cf})"
                    )
                    executed = True
                    break  # Restart loop to respect rule priority ordering

    def explain(self):
        """Explanation Facility: Prints the step-by-step reasoning trail."""
        print("\n================ EXPLANATION TRAIL ================")
        for entry in self.audit_log:
            print(entry)
        print("===================================================\n")


# =====================================================================
# DEMO EXECUTION
# =====================================================================

RULES_JSON = [
    {
        "id": "R1",
        "name": "Identify Local Network Outage",
        "priority": 10,
        "confidence": 1.0,
        "conditions": [{"fact": "connected_to_wifi", "op": "==", "val": False}],
        "actions": [{"fact": "issue", "val": "Local Network Failure"}],
    },
    {
        "id": "R2",
        "name": "Check Router Power Supply",
        "priority": 20,
        "confidence": 0.95,
        "conditions": [
            {"fact": "issue", "op": "==", "val": "Local Network Failure"},
            {"fact": "router_powered", "op": "==", "val": False},
        ],
        "actions": [{"fact": "recommendation", "val": "Verify the router power cable is firmly plugged in."}],
    },
    {
        "id": "R3",
        "name": "Check ISP Status",
        "priority": 20,
        "confidence": 0.90,
        "conditions": [
            {"fact": "issue", "op": "==", "val": "Local Network Failure"},
            {"fact": "router_powered", "op": "==", "val": True},
        ],
        "actions": [{"fact": "recommendation", "val": "Reboot router and check ISP service status."}],
    },
    {
        "id": "R4",
        "name": "Identify DNS Failure",
        "priority": 15,
        "confidence": 0.85,
        "conditions": [
            {"fact": "connected_to_wifi", "op": "==", "val": True},
            {"fact": "can_access_sites", "op": "==", "val": False},
        ],
        "actions": [{"fact": "recommendation", "val": "DNS Issue. Switch your DNS server to 8.8.8.8."}],
    },
]


def main():
    engine = AdvancedExpertSystem()
    engine.load_rules_from_json(RULES_JSON)

    print("--- Advanced Expert Engine ---")
    
    # 1. User inputs facts with confidence rating
    wifi_res = input("Is device connected to Wi-Fi? (yes/no): ").strip().lower() == "yes"
    engine.set_fact("connected_to_wifi", wifi_res, confidence=1.0)

    if not wifi_res:
        router_res = input("Are the router lights on? (yes/no): ").strip().lower() == "yes"
        # User is unsure, so we set confidence to 0.8
        engine.set_fact("router_powered", router_res, confidence=0.8)
    else:
        site_res = input("Can you access websites? (yes/no): ").strip().lower() == "yes"
        engine.set_fact("can_access_sites", site_res, confidence=1.0)

    # 2. Run Forward Chaining
    engine.run()

    # 3. Present Results & Confidence
    diag = engine.facts.get("recommendation", "No action needed.")
    diag_cf = engine.fact_confidences.get("recommendation", 1.0)
    print(f"\nDIAGNOSIS: {diag}")
    print(f"CONFIDENCE SCORE: {diag_cf * 100:.1f}%")

    # 4. Display Rule Execution Reasoning
    engine.explain()


if __name__ == "__main__":
    main()