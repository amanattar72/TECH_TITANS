import httpx, re
from datetime import datetime, timezone

DEMO_HUB="0x1111111111111111111111111111111111111111"
DEMO_MIDDLE="0x2222222222222222222222222222222222222222"
DEMO_VASP="0x3333333333333333333333333333333333333333"

def is_evm_address(value: str) -> bool:
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", value.strip()))

def demo_transactions(address: str) -> list[dict]:
    now=int(datetime.now(timezone.utc).timestamp())
    # All hashes, addresses, amounts and timestamps here are synthetic.
    return [
      {"tx_hash":"0xdemo000000000000000000000000000000000000000000000000000000000001","from_address":address,"to_address":DEMO_MIDDLE,"amount":2.4,"token":"ETH","timestamp":datetime.fromtimestamp(now-7200,timezone.utc).isoformat(),"direction":"outgoing","source":"synthetic_demo_data","block_number":None},
      {"tx_hash":"0xdemo000000000000000000000000000000000000000000000000000000000002","from_address":address,"to_address":DEMO_HUB,"amount":0.35,"token":"ETH","timestamp":datetime.fromtimestamp(now-3600,timezone.utc).isoformat(),"direction":"outgoing","source":"synthetic_demo_data","block_number":None},
      {"tx_hash":"0xdemo000000000000000000000000000000000000000000000000000000000003","from_address":DEMO_MIDDLE,"to_address":DEMO_VASP,"amount":2.1,"token":"ETH","timestamp":datetime.fromtimestamp(now-1800,timezone.utc).isoformat(),"direction":"related","source":"synthetic_demo_data","block_number":None},
      {"tx_hash":"0xdemo000000000000000000000000000000000000000000000000000000000004","from_address":DEMO_HUB,"to_address":DEMO_VASP,"amount":0.3,"token":"ETH","timestamp":datetime.fromtimestamp(now-900,timezone.utc).isoformat(),"direction":"related","source":"synthetic_demo_data","block_number":None},
      {"tx_hash":"0xdemo000000000000000000000000000000000000000000000000000000000005","from_address":DEMO_VASP,"to_address":DEMO_HUB,"amount":0.05,"token":"ETH","timestamp":datetime.fromtimestamp(now-300,timezone.utc).isoformat(),"direction":"incoming","source":"synthetic_demo_data","block_number":None},
    ]

async def etherscan_transactions(address: str, api_key: str) -> list[dict]:
    if not api_key: raise RuntimeError("Etherscan mode selected, but ETHERSCAN_API_KEY is not configured. Choose Demo mode or configure the key.")
    url="https://api.etherscan.io/v2/api"
    params={"chainid":"1","module":"account","action":"txlist","address":address,"startblock":"0","endblock":"99999999","page":"1","offset":"100","sort":"desc","apikey":api_key}
    async with httpx.AsyncClient(timeout=20) as client:
        response=await client.get(url,params=params); response.raise_for_status(); data=response.json()
    if data.get("status") != "1" and data.get("message") != "No transactions found":
        raise RuntimeError(f"Etherscan returned an error: {data.get('message','unknown provider error')} {data.get('result','')}")
    rows=data.get("result",[]) if isinstance(data.get("result"),list) else []
    out=[]
    for tx in rows:
        try: value=int(tx.get("value","0"))/10**18
        except (ValueError,TypeError): value=0.0
        out.append({"tx_hash":tx.get("hash",""),"from_address":tx.get("from",""),"to_address":tx.get("to",""),"amount":value,"token":"ETH","timestamp":datetime.fromtimestamp(int(tx.get("timeStamp","0")),timezone.utc).isoformat(),"direction":"outgoing" if tx.get("from"," ").lower()==address.lower() else "incoming","source":"etherscan_api_v2","block_number":int(tx["blockNumber"]) if tx.get("blockNumber"," ").isdigit() else None})
    return out
