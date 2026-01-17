"""
LangGraph ReAct Agent for Policy Analysis
Implements Think → Act → Observe → Decide loop
"""

import logging
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END

from tools import RAGTools
from schemas import ReasoningStep, PolicyEvidence, StepTypeEnum

logger = logging.getLogger(__name__)


class AgentState:
    """State object for the reasoning agent"""
    
    def __init__(
        self,
        claim_id: str,
        claim_text: str,
        region: str,
        category: str,
    ):
        self.claim_id = claim_id
        self.claim_text = claim_text
        self.region = region
        self.category = category
        
        # Reasoning state
        self.reasoning_trace: List[ReasoningStep] = []
        self.evidence: List[PolicyEvidence] = []
        self.exclusions_found: List[str] = []
        self.limits_found: List[str] = []
        
        # Decision state
        self.decision: Optional[str] = None
        self.summary: Optional[str] = None
        self.confidence: float = 0.0
        
        # Internal state
        self.step_count: int = 0
        self.retrieved_clauses: List[Dict] = []
        self.current_thought: str = ""
        self.should_continue: bool = True
    
    def add_step(
        self,
        step_type: StepTypeEnum,
        content: str,
        tool_used: Optional[str] = None,
        tool_input: Optional[Dict] = None,
        tool_output: Optional[str] = None,
    ):
        """Add a reasoning step to the trace"""
        self.step_count += 1
        step = ReasoningStep(
            step_number=self.step_count,
            step_type=step_type,
            content=content,
            tool_used=tool_used,
            tool_input=tool_input,
            tool_output=tool_output,
            timestamp=datetime.now().isoformat(),
        )
        self.reasoning_trace.append(step)
        return step


class PolicyReasoningAgent:
    """
    LangGraph-based ReAct agent for insurance policy analysis.
    
    The agent follows this pattern:
    1. THINK: Reason about what information is needed
    2. ACT: Use tools to retrieve policy information
    3. OBSERVE: Analyze the retrieved information
    4. DECIDE: Make a coverage decision based on evidence
    """
    
    SYSTEM_PROMPT = """You are an expert insurance claims analyst. Your job is to analyze insurance claims 
and determine coverage based on policy documents.

For each claim, you must:
1. Identify the type of damage or loss
2. Search for relevant policy clauses that cover this type of claim
3. Check for any exclusions that might apply
4. Check for coverage limits
5. Make a final decision: COVERED, NOT_COVERED, PARTIAL, or NEEDS_REVIEW

Always explain your reasoning clearly. Be thorough but concise.

Region: {region}
Category: {category}
Policy Focus: {policy_focus}

When analyzing, pay special attention to:
- Specific coverage clauses that apply to this claim type
- Exclusions that might void coverage
- Coverage limits and deductibles
- Any conditions or requirements for coverage
"""

    POLICY_FOCUS = {
        ("SG", "Home"): "MSIG Enhanced HomePlus Policy - Focus on home damage, water damage, bursting of pipes",
        ("AU", "Business"): "Zurich Business Insurance - Focus on property damage, liability, business interruption",
        ("SG", "Business"): "Singapore business insurance policies",
        ("AU", "Home"): "Australian home insurance policies",
    }
    
    def __init__(
        self,
        rag_service_url: str,
        google_api_key: str,
        model_name: str = "gemini-2.0-flash",
    ):
        self.rag_tools = RAGTools(rag_service_url)
        self.model_name = model_name
        
        if google_api_key:
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=google_api_key,
                temperature=0.1,
                convert_system_message_to_human=True,
            )
        else:
            self.llm = None
            logger.warning("No Google API key provided - using mock responses")
    
    def _get_system_prompt(self, region: str, category: str) -> str:
        """Get the system prompt for the specific region/category"""
        policy_focus = self.POLICY_FOCUS.get(
            (region, category),
            "General insurance policy"
        )
        return self.SYSTEM_PROMPT.format(
            region=region,
            category=category,
            policy_focus=policy_focus,
        )
    
    async def _think(self, state: AgentState) -> str:
        """Generate a thought about what to do next"""
        if self.llm is None:
            # Mock response for testing without API key
            if state.step_count == 0:
                return f"I need to analyze this {state.category} insurance claim from {state.region}. First, I should search for relevant policy clauses about: {state.claim_text[:100]}"
            elif state.step_count < 3:
                return "I should check for any exclusions that might apply to this claim."
            else:
                return "I have gathered enough information. I should now make a coverage decision."
        
        messages = [
            SystemMessage(content=self._get_system_prompt(state.region, state.category)),
            HumanMessage(content=f"""
Claim: {state.claim_text}

Current reasoning steps taken:
{self._format_trace(state.reasoning_trace)}

What should I think about or do next to analyze this claim?
If I have enough information, I should make a decision.
Respond with your thought process.
"""),
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def _decide(self, state: AgentState) -> Dict[str, Any]:
        """Make a final coverage decision"""
        if self.llm is None:
            # Mock decision for testing
            return {
                "decision": "NEEDS_REVIEW",
                "summary": f"This {state.category} claim from {state.region} requires manual review. Based on initial analysis of the claim regarding: {state.claim_text[:100]}...",
                "confidence": 0.6,
            }
        
        messages = [
            SystemMessage(content=self._get_system_prompt(state.region, state.category)),
            HumanMessage(content=f"""
Claim: {state.claim_text}

Evidence gathered:
{self._format_evidence(state.evidence)}

Exclusions found:
{chr(10).join(state.exclusions_found) if state.exclusions_found else 'None found'}

Limits found:
{chr(10).join(state.limits_found) if state.limits_found else 'None found'}

Based on all the evidence, make a FINAL DECISION about this claim.
Respond in this exact format:
DECISION: [COVERED/NOT_COVERED/PARTIAL/NEEDS_REVIEW]
CONFIDENCE: [0.0-1.0]
SUMMARY: [2-3 sentence explanation]
"""),
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Parse the response
        lines = response.content.strip().split("\n")
        decision = "NEEDS_REVIEW"
        confidence = 0.5
        summary = response.content
        
        for line in lines:
            if line.startswith("DECISION:"):
                decision = line.replace("DECISION:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
        
        return {
            "decision": decision,
            "summary": summary,
            "confidence": confidence,
        }
    
    def _format_trace(self, trace: List[ReasoningStep]) -> str:
        """Format reasoning trace for prompt"""
        if not trace:
            return "No steps taken yet."
        
        lines = []
        for step in trace:
            lines.append(f"{step.step_number}. [{step.step_type}] {step.content[:200]}")
        return "\n".join(lines)
    
    def _format_evidence(self, evidence: List[PolicyEvidence]) -> str:
        """Format evidence for prompt"""
        if not evidence:
            return "No evidence gathered yet."
        
        lines = []
        for e in evidence:
            lines.append(f"- [{e.policy_name}] {e.content[:200]}...")
        return "\n".join(lines)
    
    async def analyze(
        self,
        claim_id: str,
        claim_text: str,
        region: str,
        category: str,
    ) -> Dict[str, Any]:
        """
        Run the full analysis pipeline for a claim.
        Returns the complete reasoning trace and decision.
        """
        state = AgentState(
            claim_id=claim_id,
            claim_text=claim_text,
            region=region,
            category=category,
        )
        
        max_steps = 8
        
        # Step 1: Initial thinking
        thought = await self._think(state)
        state.add_step(StepTypeEnum.THINK, thought)
        
        # Step 2: Search for relevant policy clauses
        state.add_step(
            StepTypeEnum.ACT,
            f"Searching for policy clauses related to: {claim_text[:100]}",
            tool_used="search_policy_clauses",
            tool_input={"query": claim_text, "region": region, "category": category},
        )
        
        clauses = await self.rag_tools.search_clauses(claim_text, region, category)
        
        state.add_step(
            StepTypeEnum.OBSERVE,
            f"Found {len(clauses)} relevant policy clauses",
            tool_output=str([c["content"][:100] for c in clauses]),
        )
        
        # Add clauses as evidence
        for clause in clauses:
            state.evidence.append(PolicyEvidence(
                content=clause["content"],
                policy_name=clause.get("policy_name", "Unknown"),
                section=clause.get("section"),
                relevance_score=clause.get("similarity_score", 0.0),
            ))
        
        # Step 3: Check for exclusions
        state.add_step(
            StepTypeEnum.ACT,
            "Checking for exclusions that might apply",
            tool_used="check_exclusions",
            tool_input={"query": claim_text, "region": region},
        )
        
        exclusions = await self.rag_tools.search_exclusions(claim_text, region, category)
        
        if exclusions:
            state.exclusions_found = [e["content"][:200] for e in exclusions]
            state.add_step(
                StepTypeEnum.OBSERVE,
                f"Found {len(exclusions)} potential exclusions",
                tool_output=str(state.exclusions_found),
            )
        else:
            state.add_step(
                StepTypeEnum.OBSERVE,
                "No specific exclusions found for this claim type",
            )
        
        # Step 4: Check for limits
        state.add_step(
            StepTypeEnum.ACT,
            "Checking coverage limits",
            tool_used="check_limits",
            tool_input={"query": claim_text, "region": region},
        )
        
        limits = await self.rag_tools.search_limits(claim_text, region, category)
        
        if limits:
            state.limits_found = [l["content"][:200] for l in limits]
            state.add_step(
                StepTypeEnum.OBSERVE,
                f"Found {len(limits)} relevant coverage limits",
                tool_output=str(state.limits_found),
            )
        else:
            state.add_step(
                StepTypeEnum.OBSERVE,
                "No specific limits found",
            )
        
        # Step 5: Make decision
        decision_result = await self._decide(state)
        
        state.add_step(
            StepTypeEnum.DECIDE,
            f"Decision: {decision_result['decision']} - {decision_result['summary']}",
        )
        
        state.decision = decision_result["decision"]
        state.summary = decision_result["summary"]
        state.confidence = decision_result["confidence"]
        
        return {
            "claim_id": claim_id,
            "decision": state.decision,
            "reasoning_trace": state.reasoning_trace,
            "evidence": state.evidence,
            "summary": state.summary,
            "exclusions_found": state.exclusions_found,
            "limits_found": state.limits_found,
            "confidence": state.confidence,
        }
    
    async def analyze_stream(
        self,
        claim_id: str,
        claim_text: str,
        region: str,
        category: str,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream the analysis process step by step.
        Yields each reasoning step as it occurs.
        """
        state = AgentState(
            claim_id=claim_id,
            claim_text=claim_text,
            region=region,
            category=category,
        )
        
        # Yield initial status
        yield {"type": "start", "claim_id": claim_id, "status": "Starting analysis..."}
        
        # Think
        thought = await self._think(state)
        step = state.add_step(StepTypeEnum.THINK, thought)
        yield {"type": "step", "step": step.model_dump()}
        
        # Search clauses
        step = state.add_step(
            StepTypeEnum.ACT,
            f"Searching for policy clauses",
            tool_used="search_policy_clauses",
        )
        yield {"type": "step", "step": step.model_dump()}
        
        clauses = await self.rag_tools.search_clauses(claim_text, region, category)
        step = state.add_step(
            StepTypeEnum.OBSERVE,
            f"Found {len(clauses)} relevant clauses",
        )
        yield {"type": "step", "step": step.model_dump()}
        
        # Search exclusions
        step = state.add_step(
            StepTypeEnum.ACT,
            "Checking for exclusions",
            tool_used="check_exclusions",
        )
        yield {"type": "step", "step": step.model_dump()}
        
        exclusions = await self.rag_tools.search_exclusions(claim_text, region, category)
        step = state.add_step(
            StepTypeEnum.OBSERVE,
            f"Found {len(exclusions)} potential exclusions",
        )
        yield {"type": "step", "step": step.model_dump()}
        
        # Make decision
        decision_result = await self._decide(state)
        step = state.add_step(
            StepTypeEnum.DECIDE,
            f"Decision: {decision_result['decision']}",
        )
        yield {"type": "step", "step": step.model_dump()}
        
        # Final result
        yield {
            "type": "complete",
            "claim_id": claim_id,
            "decision": decision_result["decision"],
            "summary": decision_result["summary"],
            "confidence": decision_result["confidence"],
        }
