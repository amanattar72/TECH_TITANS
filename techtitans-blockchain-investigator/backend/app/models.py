from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime, timezone

class InvestigationRequest(BaseModel):
    address: str = Field(min_length=1, max_length=128)
    network: Literal["ethereum", "polygon", "arbitrum", "base", "bitcoin"] = "ethereum"
    mode: Literal["demo", "etherscan"] = "demo"

class Transaction(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    token: str = "ETH"
    timestamp: str
    direction: Literal["incoming", "outgoing", "related"]
    source: str = "synthetic_demo_data"
    block_number: Optional[int] = None

class RiskFinding(BaseModel):
    severity: Literal["low", "medium", "high"]
    title: str
    explanation: str
    evidence_tx_hashes: list[str] = []

class Attribution(BaseModel):
    candidate_name: str
    address: str
    relationship: str
    confidence: Literal["low", "medium", "high"]
    source: str
    verification_date: str
    explanation: str

class InvestigationResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    investigation_id: str
    address: str
    network: str
    data_mode: str
    generated_at: str
    transaction_count: int
    transactions: list[Transaction]
    nodes: list[dict]
    edges: list[dict]
    paths: list[dict]
    risk_findings: list[RiskFinding]
    attributions: list[Attribution]
    limitations: list[str]

class CaseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    complaint_reference: str = Field(default="", max_length=120)
    investigator: str = Field(default="Unassigned", max_length=120)
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    status: Literal["open", "in_review", "escalated", "closed"] = "open"
    wallet_address: str = ""
    investigation_id: str = ""
    notes: str = ""

class CaseUpdate(BaseModel):
    status: Optional[Literal["open", "in_review", "escalated", "closed"]] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    investigator: Optional[str] = None
    notes: Optional[str] = None
