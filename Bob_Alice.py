import networkx as nx
import plotly.graph_objects as go

class DemoBlockchain:
    def _init_(self):
        self.transactions = {
            "Alice": ["tx1"],
            "Bob": ["tx2"],
            "Charlie": [],  # True end user
            "Alice_Change": [],  # Change address
            "Bob_Change": []     # Change address
        }
        
        self.tx_details = {
            "tx1": {
                "inputs": [{"recipient": "Alice", "value": 1.0}],
                "outputs": [
                    {"recipient": "Bob", "value": 0.3},
                    {"recipient": "Alice_Change", "value": 0.7}  # Change (largest output)
                ]
            },
            "tx2": {
                "inputs": [{"recipient": "Bob", "value": 0.3}],
                "outputs": [
                    {"recipient": "Charlie", "value": 0.1},   # Regular recipient
                    {"recipient": "Bob_Change", "value": 0.2}  # Change (largest output)
                ]
            }
        }

    def get_transactions(self, address):
        return self.transactions.get(address, [])

    def get_transaction_details(self, tx_hash):
        return self.tx_details.get(tx_hash)

class TransactionTracer:
    def _init_(self):
        self.blockchain = DemoBlockchain()
        self.graph = nx.DiGraph()
        self.end_users = set()
        self.visited = set()  # Track which addresses have been processed

    def _get_change_address(self, outputs):
        if not outputs:
            return None
        # Return the recipient of the output with the largest value
        return max(outputs, key=lambda x: x['value'])['recipient']

    def trace(self, start_address, depth=2):
        if depth < 0 or start_address in self.visited:
            return

        self.visited.add(start_address)
        tx_hashes = self.blockchain.get_transactions(start_address)

        for tx_hash in tx_hashes:
            tx = self.blockchain.get_transaction_details(tx_hash)
            if not tx:
                continue

            change_addr = self._get_change_address(tx['outputs'])

            for output in tx['outputs']:
                recipient = output['recipient']

                if recipient == change_addr:
                    print(f"  [Change Address] Skipped: {recipient}")
                    continue  # Skip change addresses

                # Add an edge from the current address to the recipient
                self.graph.add_edge(start_address, recipient, amount=output['value'])

                # Check if the recipient has any outgoing transactions
                if not self.blockchain.get_transactions(recipient):
                    self.end_users.add(recipient)
                    print(f"[End User] Identified: {recipient}")
                else:
                    self.trace(recipient, depth - 1)

def visualize(graph, end_users):
    pos = nx.spring_layout(graph, seed=42)
    
    # Prepare edge data
    edge_x = []
    edge_y = []
    edge_text = []
    for u, v, data in graph.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.append(f"{data['amount']:.2f} BTC")
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines'
    )
    
    # Prepare node data
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_color.append('#FF851B' if node not in end_users else '#2ECC40')
        
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        marker=dict(
            size=25,
            color=node_color,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        hoverinfo='text'
    )
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            title="Bitcoin Transaction Flow Analysis"
        )
    )
    fig.show()

if __name__ == "_main_":
    print("Starting Bitcoin Transaction Tracer (Demo Mode)")
    print("--------------------------------------------")
    
    tracer = TransactionTracer()
    tracer.trace("Alice", depth=2)
    
    print("\nResults:")
    print(f"- End users identified: {tracer.end_users or 'None'}")
    print(f"- Transaction graph: {len(tracer.graph.nodes())} nodes, "
          f"{len(tracer.graph.edges())} edges")
    
    print("\nGenerating visualization...")
    visualize(tracer.graph, tracer.end_users)