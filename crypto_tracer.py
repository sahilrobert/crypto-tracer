import requests
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import time

# ======================
# Blockchain Data Fetcher (Blockchair API)
# ======================
class BlockchainAnalyzer:
    def _init_(self):   # Correct init syntax
        self.base_url = "https://api.blockchair.com/bitcoin"

    def fetch_with_retry(self, url, max_retries=3, delay=5):
        """API fetch with retries to handle rate limits and errors"""
        for i in range(max_retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Attempt {i + 1} failed: {e}")
                time.sleep(delay)
        return None

    def get_transactions(self, address):
        """Fetch transactions using Blockchair API"""
        print(f"Fetching transactions for {address}...")
        
        url = f"{self.base_url}/dashboards/address/{address}?limit=50"
        data = self.fetch_with_retry(url)
        
        if not data or 'data' not in data or address not in data['data']:
            print(f"Error: No data found for address {address}")
            return []

        tx_hashes = data['data'].get(address, {}).get('transactions', [])
        
        transactions = []
        for tx_hash in tx_hashes[:5]:  # Process first 5 transactions
            tx_data = self.get_transaction_details(tx_hash)
            if tx_data:
                transactions.append(tx_data)
        return transactions

    def get_transaction_details(self, tx_hash):
        """Fetch detailed data for a single transaction"""
        print(f"Fetching details for transaction {tx_hash}...")
        
        url = f"{self.base_url}/dashboards/transaction/{tx_hash}"
        data = self.fetch_with_retry(url)
        
        if not data or 'data' not in data or tx_hash not in data['data']:
            print(f"Error: No data found for transaction {tx_hash}")
            return None

        tx_info = data['data'][tx_hash]

        # Extract inputs and outputs safely
        inputs = tx_info.get('inputs', [])
        outputs = tx_info.get('outputs', [])

        return {
            'hash': tx_hash,
            'inputs': inputs,
            'outputs': outputs
        }

# ======================
# Transaction Tracer
# ======================
class TransactionTracer:
    def _init_(self):
        self.analyzer = BlockchainAnalyzer()
        self.graph = nx.DiGraph()
        self.clusters = defaultdict(set)
        self.visited = set()

    def _get_change_address(self, outputs):
        """Identify change address (smallest output)"""
        if not outputs:
            return None
        
        valid_outputs = [out for out in outputs if out.get('recipient')]
        if not valid_outputs:
            return None
        
        # Identify change address as the smallest value output
        return min(valid_outputs, key=lambda x: x['value']).get('recipient', 'unknown')

    def _cluster_addresses(self, tx):
        """Group addresses owned by the same entity"""
        input_addresses = {inp.get('recipient') for inp in tx.get('inputs', []) if inp.get('recipient')}
        
        if len(input_addresses) > 1:
            main_cluster = min(input_addresses)  # Use the smallest address as the cluster ID
            for addr in input_addresses:
                self.clusters[main_cluster].add(addr)

    def trace_transactions(self, start_address, depth=2, max_transactions=50):
        """Recursive transaction tracing"""
        if depth <= 0 or start_address in self.visited or len(self.visited) >= max_transactions:
            return
        
        self.visited.add(start_address)
        
        transactions = self.analyzer.get_transactions(start_address)
        print(f"Fetched {len(transactions)} transactions for {start_address}")

        for tx in transactions:
            self._cluster_addresses(tx)

            # Identify change address
            change_address = self._get_change_address(tx.get('outputs', []))
            print(f"Change Address: {change_address}")

            sender_cluster = next(
                (k for k, v in self.clusters.items() if start_address in v),
                start_address
            )

            for output in tx.get('outputs', []):
                receiver = output.get('recipient', 'unknown')
                value = output.get('value', 0) / 10**8  # Convert satoshi to BTC

                print(f"Receiver: {receiver}, Value: {value:.4f} BTC")

                # Add edges to the graph
                if receiver != change_address and receiver not in self.visited:
                    self.graph.add_edge(sender_cluster, receiver, weight=value, tx_hash=tx['hash'])
                    
                    # Recursively trace transactions
                    if len(self.visited) < max_transactions:
                        self.trace_transactions(receiver, depth - 1, max_transactions)

# ======================
# Visualization
# ======================
def visualize_graph(graph):
    """Visualize the transaction graph"""
    plt.figure(figsize=(20, 15))

    # Layout configuration
    pos = nx.spring_layout(graph, seed=42)

    # Normalize node sizes based on degree
    node_sizes = [1000 + 500 * graph.degree(node) for node in graph.nodes()]
    
    nx.draw_networkx_nodes(graph, pos, node_size=node_sizes, node_color='skyblue')
    nx.draw_networkx_labels(graph, pos, font_size=8)

    # Visualize edges with weights
    edge_weights = [graph[u][v]['weight'] * 0.1 for u, v in graph.edges()]
    nx.draw_networkx_edges(graph, pos, width=edge_weights, edge_color='gray')

    # Display edge labels with BTC value
    edge_labels = {(u, v): f"{graph[u][v]['weight']:.4f} BTC" for u, v in graph.edges()}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=6)

    plt.title("Bitcoin Transaction Flow", size=18)
    plt.axis('off')
    plt.show()

# ======================
# Main Execution
# ======================
if _name_ == "_main_":
    start_address = "1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v"  # Wikipedia Donations

    tracer = TransactionTracer()
    
    print("\n Starting Bitcoin Transaction Trace...")
    
    tracer.trace_transactions(start_address, depth=2, max_transactions=50)

    print("\n Results:")
    print(f"Clusters: {len(tracer.clusters)}")
    print(f"Nodes: {len(tracer.graph.nodes())}")
    print(f"Edges: {len(tracer.graph.edges())}")
    
    visualize_graph(tracer.graph)
