# Mini Expert System (Network Troubleshooter)

A lightweight, rule-based expert system written in Python that diagnoses common internet connection issues using **forward chaining**, **certainty factors**, and an **explanation facility**.

---

## 🚀 Features

- **Forward Chaining Inference Engine**: Infers new facts and diagnoses step-by-step from known facts and conditions.
- **Uncertainty Handling (Certainty Factors)**: Calculates confidence scores for diagnoses based on input reliability and rule confidence.
- **Priority-Based Conflict Resolution**: Rules with higher priority execute first to ensure proper diagnostic flow.
- **Explanation Facility**: Provides an audit trail that explains why specific conclusions were reached.
- **JSON Rule Definitions**: Easily extend or add new diagnostic rules without modifying core engine logic.
- **Zero Dependencies**: Built entirely using Python's standard library (`json`, `datetime`).

---

## 📋 Requirements

- Python 3.7 or higher

---

## 🛠️ How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ravindi-29/MiniExpert_System.git
   cd MiniExpert_System
   ```

2. **Run the script**:
   ```bash
   python expert_system.py
   ```

---

## 💡 Example Usage

```text
--- Advanced Expert Engine ---
Is device connected to Wi-Fi? (yes/no): no
Are the router lights on? (yes/no): yes

DIAGNOSIS: Reboot router and check ISP service status.
CONFIDENCE SCORE: 72.0%

================ EXPLANATION TRAIL ================
[18:00:01] FACT SET: connected_to_wifi = False (cf=1.0)
[18:00:04] FACT SET: router_powered = True (cf=0.8)
[18:00:04] FACT SET: issue = Local Network Failure (cf=1.0)
[18:00:04] RULE FIRED: [R1] Identify Local Network Outage (CF: 1.0)
[18:00:04] FACT SET: recommendation = Reboot router and check ISP service status. (cf=0.72)
[18:00:04] RULE FIRED: [R3] Check ISP Status (CF: 0.72)
===================================================
```

---

## 📁 Project Structure

```text
MiniExpert_System/
├── expert_system.py   # Core inference engine, rule structures, and interactive CLI
└── README.md          # Project documentation
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
