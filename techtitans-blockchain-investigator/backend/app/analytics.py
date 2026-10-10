from datetime import datetime, timezone
import networkx as nx

def analyze(transactions: list[dict], subject: str):
    graph = nx.DiGraph()
    for tx in transactions:
        src, dst = tx["from_address"], tx["to_address"]
        graph.add_node(src, label=short(src), address=src, is_subject=(src.lower()==subject.lower()))
        graph.add_node(dst, label=short(dst), address=dst, is_subject=(dst.lower()==subject.lower()))
        graph.add_edge(src, dst, tx_hash=tx["tx_hash"], amount=tx["amount"], token=tx.get("token", "ETH"), timestamp=tx["timestamp"])
    paths=[]
    if subject in graph:
        for neighbor in graph.successors(subject):
            edge=graph.get_edge_data(subject, neighbor)
            paths.append({"from":subject,"to":neighbor,"hops":1,"tx_hashes":[edge["tx_hash"]],"amount":edge["amount"],"note":"Direct outgoing transfer"})
        # Small bounded paths only; no claim that all funds are traceable.
        for target in graph.nodes:
            if target == subject or target in graph.successors(subject): continue
            try: path=nx.shortest_path(graph, subject, target)
            except (nx.NetworkXNoPath, nx.NodeNotFound): continue
            if 2 <= len(path)-1 <= 3:
                hashes=[]
                for a,b in zip(path,path[1:]): hashes.append(graph.get_edge_data(a,b)["tx_hash"] )
                paths.append({"from":subject,"to":target,"hops":len(path)-1,"tx_hashes":hashes,"amount":None,"note":"Indirect graph path; amounts are not aggregated"})
            if len(paths)>=15: break
    nodes=[{"id":n,"label":graph.nodes[n].get("label",short(n)),"address":n,"is_subject":n.lower()==subject.lower()} for n in graph.nodes]
    edges=[{"id":d["tx_hash"],"source":a,"target":b,"label":f'{d["amount"]} {d["token"]}',"tx_hash":d["tx_hash"],"amount":d["amount"],"timestamp":d["timestamp"]} for a,b,d in graph.edges(data=True)]
    return nodes,edges,paths

def short(address: str):
    return address if len(address)<18 else address[:8]+"…"+address[-6:]

def findings(transactions: list[dict]):
    result=[]
    if len(transactions)>=4:
        result.append({"severity":"medium","title":"Multiple related transfers","explanation":"Four or more transactions were returned in this dataset. Review the timing and counterparties; volume alone does not establish suspicious activity.","evidence_tx_hashes":[x["tx_hash"] for x in transactions[:5]]})
    amounts=[x["amount"] for x in transactions if x.get("amount",0)>0]
    if amounts and max(amounts)>=10:
        result.append({"severity":"low","title":"Large-value transfer in dataset","explanation":"At least one displayed transfer is 10 ETH or more. This is a review cue only; value thresholds are configurable and do not imply wrongdoing.","evidence_tx_hashes":[x["tx_hash"] for x in transactions if x.get("amount",0)>=10]})
    if not result:
        result.append({"severity":"low","title":"No rule-based alert triggered","explanation":"The currently enabled demo rules did not trigger. This is not evidence that the wallet is safe.","evidence_tx_hashes":[]})
    return result
