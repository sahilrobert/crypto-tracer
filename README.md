# 🔍 Crypto Tracer – Find the End User of a Cryptocurrency Transaction

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A Python-based software solution that analyzes and traces cryptocurrency transactions on the blockchain to identify the **end user** in a transaction chain. Built for cybersecurity researchers, law enforcement, and investigative use cases.

---

## 🧠 What It Does

`Crypto Tracer` starts with a known **cryptocurrency transaction hash** or **wallet address** and follows the transaction trail through the blockchain. Using data from the **Blockchair API**, it explores outgoing transactions recursively to trace where the cryptocurrency eventually ends up.

The software aims to **identify the last active wallet** in the chain — likely controlled by the final user — by analyzing:
- Address activity
- Transaction depth
- Reuse of addresses
- Patterns indicating mixers or exchanges

---

## 💡 How It Works

Here's an overview of the tracing logic:

1. **Input**: A user provides a wallet address or transaction hash.
2. **API Query**: The tool uses the [Blockchair API](https://blockchair.com/api/docs) to fetch transaction history and outputs.
3. **Recursive Tracing**: It follows each transaction’s outputs to identify the next recipient addresses.
4. **Exit Conditions**:
   - The address has no further outgoing transactions.
   - The address is flagged as belonging to an exchange or mixer (optional extension).
5. **Result**: The program displays a report of all traced addresses and highlights the most likely end user(s).

---

## 📁 Project Structure

```bash
crypto-tracer/
├── main.py              # Main tracing logic
├── bob_and_alice.py     # Example scenario simulation
├── utils.py             # Helper functions (API, parsing, etc.)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
