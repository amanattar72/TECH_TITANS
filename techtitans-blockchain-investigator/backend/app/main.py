from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from uuid import uuid4
import csv, io, json
from fastapi.responses import StreamingResponse
from .config import settings
from .models import InvestigationRequest, CaseCreate, CaseUpdate
from .providers import is_evm_address, demo_transactions, etherscan_transactions, DEMO_VASP
from .analytics import analyze, findings, short

app=FastAPI(title="Tech Titans Blockchain Investigation API", version="0.1.0", description="MVP API for wallet analysis, transaction graph review, case management and evidence exports. Demo records are synthetic.")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
INVESTIGATIONS: dict[str,dict]={}
CASES: dict[str,dict]={}

@app.get("/health")
def health(): return {"status":"ok","environment":settings.app_env,"database":"in-memory demo repository","live_integrations":{"etherscan":bool(settings.etherscan_api_key),"ncrp":False,"sahyog":False}}

@app.post("/api/investigations")
async def investigate(req: InvestigationRequest):
    address=req.address.strip()
    if req.network != "bitcoin" and not is_evm_address(address): raise HTTPException(422,"Invalid EVM wallet address. Expected 0x followed by 40 hexadecimal characters.")
    if req.network == "bitcoin": raise HTTPException(501,"Bitcoin analysis is not implemented yet. Use Ethereum or another listed EVM network in demo mode.")
    if req.mode == "etherscan":
        if req.network != "ethereum": raise HTTPException(400,"Live provider adapter currently supports Ethereum mainnet only.")
        try: txs=await etherscan_transactions(address,settings.etherscan_api_key)
        except Exception as exc: raise HTTPException(502,str(exc))
        data_mode="live_provider_data"
    else:
        txs=demo_transactions(address); data_mode="synthetic_demo_data"
    # Live txs may contain no subject edges if there is no history; this is reported, not hidden.
    nodes,edges,paths=analyze(txs,address)
    attributions=[]
    if data_mode=="synthetic_demo_data" and any(t["to_address"].lower()==DEMO_VASP.lower() for t in txs):
        attributions.append({"candidate_name":"Example VASP (synthetic label)","address":DEMO_VASP,"relationship":"indirect_demo_path","confidence":"low","source":"synthetic_demo_label_registry","verification_date":datetime.now(timezone.utc).date().isoformat(),"explanation":"This is a fictional demo label used to demonstrate provenance display. It is not a real exchange attribution."})
    result={"investigation_id":"INV-"+uuid4().hex[:10].upper(),"address":address,"network":req.network,"data_mode":data_mode,"generated_at":datetime.now(timezone.utc).isoformat(),"transaction_count":len(txs),"transactions":txs,"nodes":nodes,"edges":edges,"paths":paths,"risk_findings":findings(txs),"attributions":attributions,"limitations":["Transaction history is limited to the configured provider and requested page/offset.","Graph paths show connectivity, not proof that the same funds moved end-to-end.","Candidate attribution is not proof of wallet ownership, criminal intent, or fraud.","No cross-chain tracing, exchange account identification, or law-enforcement integration is enabled."] if data_mode=="live_provider_data" else ["All displayed transactions, addresses and labels are synthetic demonstration data.","Candidate VASP is fictional and is not a real exchange attribution.","Graph paths show connectivity, not proof that the same funds moved end-to-end.","No cross-chain tracing or law-enforcement integration is enabled."]}
    INVESTIGATIONS[result["investigation_id"]]=result
    return result

@app.get("/api/cases")
def list_cases(): return sorted(CASES.values(),key=lambda c:c["created_at"],reverse=True)

@app.post("/api/cases")
def create_case(req: CaseCreate):
    cid="CASE-"+uuid4().hex[:8].upper(); now=datetime.now(timezone.utc).isoformat()
    case={"case_id":cid,**req.model_dump(),"created_at":now,"updated_at":now,"audit_log":[{"at":now,"action":"case_created","actor":"local_demo_user"}]}
    if req.investigation_id and req.investigation_id not in INVESTIGATIONS: raise HTTPException(404,"Investigation not found")
    CASES[cid]=case; return case

@app.patch("/api/cases/{case_id}")
def update_case(case_id: str, req: CaseUpdate):
    if case_id not in CASES: raise HTTPException(404,"Case not found")
    case=CASES[case_id]; changes={k:v for k,v in req.model_dump().items() if v is not None}
    case.update(changes); now=datetime.now(timezone.utc).isoformat(); case["updated_at"]=now
    case["audit_log"].append({"at":now,"action":"case_updated","fields":list(changes.keys()),"actor":"local_demo_user"})
    return case

@app.get("/api/reports/{investigation_id}.json")
def report_json(investigation_id: str):
    if investigation_id not in INVESTIGATIONS: raise HTTPException(404,"Investigation not found")
    return INVESTIGATIONS[investigation_id]

@app.get("/api/reports/{investigation_id}.csv")
def report_csv(investigation_id: str):
    if investigation_id not in INVESTIGATIONS: raise HTTPException(404,"Investigation not found")
    out=io.StringIO(); writer=csv.DictWriter(out,fieldnames=["tx_hash","from_address","to_address","amount","token","timestamp","direction","source","block_number"]); writer.writeheader(); writer.writerows(INVESTIGATIONS[investigation_id]["transactions"]); out.seek(0)
    return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",headers={"Content-Disposition":f"attachment; filename={investigation_id}-transactions.csv"})
