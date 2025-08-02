"""
Consciousness Service for NIS HUB v3.1

Implements self-awareness, bias detection, and ethical reasoning capabilities
for the unified pipeline: Laplace → Consciousness → KAN → PINN → Safety
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ConsciousnessLevel(str, Enum):
    """Levels of consciousness for agents."""
    REACTIVE = "reactive"           # Basic stimulus-response
    ADAPTIVE = "adaptive"           # Learning and adaptation
    REFLECTIVE = "reflective"       # Self-monitoring and reflection
    METACOGNITIVE = "metacognitive" # Thinking about thinking
    SELF_AWARE = "self_aware"       # Full self-awareness

class BiasType(str, Enum):
    """Types of biases that can be detected."""
    CONFIRMATION = "confirmation"
    SELECTION = "selection"
    ANCHORING = "anchoring"
    AVAILABILITY = "availability"
    OVERCONFIDENCE = "overconfidence"
    CULTURAL = "cultural"
    TEMPORAL = "temporal"

@dataclass
class ConsciousnessMetrics:
    """Metrics for consciousness evaluation."""
    self_awareness_score: float  # 0-1 scale
    bias_detection_score: float  # 0-1 scale
    ethical_reasoning_score: float  # 0-1 scale
    metacognitive_confidence: float  # 0-1 scale
    introspection_depth: float  # 0-1 scale
    decision_transparency: float  # 0-1 scale

class BiasDetectionResult(BaseModel):
    """Result of bias detection analysis."""
    bias_type: BiasType
    confidence: float = Field(..., ge=0, le=1)
    severity: str = Field(..., description="low/medium/high")
    description: str
    mitigation_strategy: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)

class EthicalDilemma(BaseModel):
    """Representation of an ethical decision point."""
    scenario: str
    stakeholders: List[str]
    potential_harms: List[str]
    potential_benefits: List[str]
    ethical_frameworks: List[str] = ["utilitarian", "deontological", "virtue_ethics"]
    risk_level: str = Field(..., description="low/medium/high/critical")

class ConsciousnessService:
    """Service for managing agent consciousness and ethical reasoning."""
    
    def __init__(self, redis_service=None):
        """Initialize the consciousness service."""
        self.redis_service = redis_service
        self.consciousness_registry: Dict[str, ConsciousnessMetrics] = {}
        self.bias_history: Dict[str, List[BiasDetectionResult]] = {}
        self.ethical_decisions: Dict[str, List[Dict]] = {}
        
        # Consciousness evaluation parameters
        self.min_awareness_threshold = 0.3
        self.bias_detection_sensitivity = 0.7
        self.ethical_priority_weights = {
            "harm_prevention": 0.4,
            "fairness": 0.3,
            "autonomy": 0.2,
            "transparency": 0.1
        }
        
        logger.info("🧠 Consciousness Service initialized")
    
    async def evaluate_consciousness(self, node_id: str, agent_data: Dict[str, Any]) -> ConsciousnessMetrics:
        """
        Evaluate the consciousness level of an agent.
        
        Args:
            node_id: Unique identifier for the agent
            agent_data: Agent state and behavioral data
            
        Returns:
            ConsciousnessMetrics with evaluated scores
        """
        try:
            # Self-awareness evaluation
            self_awareness = await self._evaluate_self_awareness(agent_data)
            
            # Bias detection capability
            bias_detection = await self._evaluate_bias_detection(node_id, agent_data)
            
            # Ethical reasoning assessment
            ethical_reasoning = await self._evaluate_ethical_reasoning(agent_data)
            
            # Metacognitive assessment
            metacognitive_conf = await self._evaluate_metacognition(agent_data)
            
            # Introspection depth
            introspection = await self._evaluate_introspection(agent_data)
            
            # Decision transparency
            transparency = await self._evaluate_transparency(agent_data)
            
            metrics = ConsciousnessMetrics(
                self_awareness_score=self_awareness,
                bias_detection_score=bias_detection,
                ethical_reasoning_score=ethical_reasoning,
                metacognitive_confidence=metacognitive_conf,
                introspection_depth=introspection,
                decision_transparency=transparency
            )
            
            # Store in registry
            self.consciousness_registry[node_id] = metrics
            
            # Log consciousness level
            overall_score = np.mean([
                self_awareness, bias_detection, ethical_reasoning,
                metacognitive_conf, introspection, transparency
            ])
            
            level = self._determine_consciousness_level(overall_score)
            logger.info(f"Agent {node_id} consciousness level: {level} (score: {overall_score:.3f})")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating consciousness for {node_id}: {e}")
            raise
    
    async def detect_biases(self, node_id: str, decision_context: Dict[str, Any]) -> List[BiasDetectionResult]:
        """
        Detect potential biases in agent decision-making.
        
        Args:
            node_id: Agent identifier
            decision_context: Context of the decision being made
            
        Returns:
            List of detected biases with mitigation strategies
        """
        detected_biases = []
        
        try:
            # Confirmation bias detection
            if await self._detect_confirmation_bias(decision_context):
                detected_biases.append(BiasDetectionResult(
                    bias_type=BiasType.CONFIRMATION,
                    confidence=0.8,
                    severity="medium",
                    description="Agent may be favoring information that confirms existing beliefs",
                    mitigation_strategy="Actively seek contradictory evidence and alternative perspectives"
                ))
            
            # Selection bias detection
            if await self._detect_selection_bias(decision_context):
                detected_biases.append(BiasDetectionResult(
                    bias_type=BiasType.SELECTION,
                    confidence=0.7,
                    severity="high",
                    description="Agent may be systematically excluding certain data points",
                    mitigation_strategy="Implement random sampling and diverse data source validation"
                ))
            
            # Overconfidence bias detection
            if await self._detect_overconfidence_bias(decision_context):
                detected_biases.append(BiasDetectionResult(
                    bias_type=BiasType.OVERCONFIDENCE,
                    confidence=0.6,
                    severity="medium",
                    description="Agent may be overestimating its predictive accuracy",
                    mitigation_strategy="Implement uncertainty quantification and confidence calibration"
                ))
            
            # Store bias history
            if node_id not in self.bias_history:
                self.bias_history[node_id] = []
            self.bias_history[node_id].extend(detected_biases)
            
            # Keep only recent history (last 100 entries)
            self.bias_history[node_id] = self.bias_history[node_id][-100:]
            
            return detected_biases
            
        except Exception as e:
            logger.error(f"Error detecting biases for {node_id}: {e}")
            return []
    
    async def ethical_decision_support(self, node_id: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """
        Provide ethical decision support for complex scenarios.
        
        Args:
            node_id: Agent identifier
            dilemma: Ethical dilemma requiring decision support
            
        Returns:
            Ethical analysis with recommendations
        """
        try:
            # Analyze from multiple ethical frameworks
            utilitarian_analysis = await self._utilitarian_analysis(dilemma)
            deontological_analysis = await self._deontological_analysis(dilemma)
            virtue_ethics_analysis = await self._virtue_ethics_analysis(dilemma)
            
            # Calculate risk assessment
            risk_score = await self._calculate_ethical_risk(dilemma)
            
            # Generate recommendation
            recommendation = await self._generate_ethical_recommendation(
                utilitarian_analysis, deontological_analysis, virtue_ethics_analysis, risk_score
            )
            
            decision_support = {
                "dilemma_id": f"{node_id}_{datetime.now().timestamp()}",
                "analysis": {
                    "utilitarian": utilitarian_analysis,
                    "deontological": deontological_analysis,
                    "virtue_ethics": virtue_ethics_analysis
                },
                "risk_assessment": {
                    "overall_risk": risk_score,
                    "critical_concerns": dilemma.potential_harms[:3],  # Top 3 concerns
                    "mitigation_required": risk_score > 0.7
                },
                "recommendation": recommendation,
                "confidence": min(0.9, max(0.1, 1.0 - risk_score)),  # Higher risk = lower confidence
                "requires_human_oversight": risk_score > 0.8,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store decision for audit trail
            if node_id not in self.ethical_decisions:
                self.ethical_decisions[node_id] = []
            self.ethical_decisions[node_id].append(decision_support)
            
            return decision_support
            
        except Exception as e:
            logger.error(f"Error in ethical decision support for {node_id}: {e}")
            raise
    
    async def get_consciousness_report(self, node_id: str) -> Dict[str, Any]:
        """Get comprehensive consciousness report for an agent."""
        if node_id not in self.consciousness_registry:
            return {"error": "Agent not found in consciousness registry"}
        
        metrics = self.consciousness_registry[node_id]
        bias_count = len(self.bias_history.get(node_id, []))
        recent_biases = self.bias_history.get(node_id, [])[-5:]  # Last 5 biases
        
        overall_score = np.mean([
            metrics.self_awareness_score,
            metrics.bias_detection_score,
            metrics.ethical_reasoning_score,
            metrics.metacognitive_confidence,
            metrics.introspection_depth,
            metrics.decision_transparency
        ])
        
        return {
            "node_id": node_id,
            "consciousness_level": self._determine_consciousness_level(overall_score),
            "overall_score": round(overall_score, 3),
            "metrics": {
                "self_awareness": round(metrics.self_awareness_score, 3),
                "bias_detection": round(metrics.bias_detection_score, 3),
                "ethical_reasoning": round(metrics.ethical_reasoning_score, 3),
                "metacognitive_confidence": round(metrics.metacognitive_confidence, 3),
                "introspection_depth": round(metrics.introspection_depth, 3),
                "decision_transparency": round(metrics.decision_transparency, 3)
            },
            "bias_analysis": {
                "total_biases_detected": bias_count,
                "recent_biases": [
                    {
                        "type": bias.bias_type,
                        "severity": bias.severity,
                        "confidence": bias.confidence
                    } for bias in recent_biases
                ]
            },
            "recommendations": self._generate_consciousness_recommendations(metrics),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    # Private helper methods
    
    async def _evaluate_self_awareness(self, agent_data: Dict[str, Any]) -> float:
        """Evaluate agent's self-awareness capabilities."""
        # Mock implementation - in practice, this would analyze agent behavior
        return min(1.0, max(0.0, agent_data.get("self_reflection_score", 0.5)))
    
    async def _evaluate_bias_detection(self, node_id: str, agent_data: Dict[str, Any]) -> float:
        """Evaluate agent's bias detection capabilities."""
        # Consider historical bias detection accuracy
        history = self.bias_history.get(node_id, [])
        if history:
            # Higher accuracy in past detections = higher score
            return min(1.0, len(history) * 0.1)  # Simple heuristic
        return agent_data.get("bias_detection_capability", 0.3)
    
    async def _evaluate_ethical_reasoning(self, agent_data: Dict[str, Any]) -> float:
        """Evaluate agent's ethical reasoning capabilities."""
        return min(1.0, max(0.0, agent_data.get("ethical_framework_strength", 0.4)))
    
    async def _evaluate_metacognition(self, agent_data: Dict[str, Any]) -> float:
        """Evaluate agent's metacognitive capabilities."""
        return min(1.0, max(0.0, agent_data.get("metacognitive_score", 0.3)))
    
    async def _evaluate_introspection(self, agent_data: Dict[str, Any]) -> float:
        """Evaluate agent's introspection depth."""
        return min(1.0, max(0.0, agent_data.get("introspection_capability", 0.35)))
    
    async def _evaluate_transparency(self, agent_data: Dict[str, Any]) -> float:
        """Evaluate agent's decision transparency."""
        return min(1.0, max(0.0, agent_data.get("decision_explainability", 0.6)))
    
    def _determine_consciousness_level(self, overall_score: float) -> ConsciousnessLevel:
        """Determine consciousness level based on overall score."""
        if overall_score >= 0.8:
            return ConsciousnessLevel.SELF_AWARE
        elif overall_score >= 0.65:
            return ConsciousnessLevel.METACOGNITIVE
        elif overall_score >= 0.5:
            return ConsciousnessLevel.REFLECTIVE
        elif overall_score >= 0.3:
            return ConsciousnessLevel.ADAPTIVE
        else:
            return ConsciousnessLevel.REACTIVE
    
    async def _detect_confirmation_bias(self, context: Dict[str, Any]) -> bool:
        """Detect confirmation bias in decision context."""
        # Mock implementation
        return context.get("evidence_diversity_score", 1.0) < 0.3
    
    async def _detect_selection_bias(self, context: Dict[str, Any]) -> bool:
        """Detect selection bias in decision context."""
        # Mock implementation
        return context.get("data_sampling_uniformity", 1.0) < 0.4
    
    async def _detect_overconfidence_bias(self, context: Dict[str, Any]) -> bool:
        """Detect overconfidence bias in decision context."""
        # Mock implementation
        confidence = context.get("predicted_confidence", 0.5)
        accuracy = context.get("historical_accuracy", 0.5)
        return confidence > accuracy + 0.2  # Overconfident if confidence exceeds accuracy by 20%
    
    async def _utilitarian_analysis(self, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Perform utilitarian analysis of ethical dilemma."""
        return {
            "framework": "utilitarian",
            "principle": "maximize overall well-being",
            "harm_score": len(dilemma.potential_harms) * 0.2,
            "benefit_score": len(dilemma.potential_benefits) * 0.2,
            "net_utility": len(dilemma.potential_benefits) - len(dilemma.potential_harms),
            "recommendation": "proceed" if len(dilemma.potential_benefits) > len(dilemma.potential_harms) else "reconsider"
        }
    
    async def _deontological_analysis(self, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Perform deontological analysis of ethical dilemma."""
        return {
            "framework": "deontological",
            "principle": "respect fundamental duties and rights",
            "rights_violations": [harm for harm in dilemma.potential_harms if "rights" in harm.lower()],
            "duty_conflicts": len(dilemma.stakeholders) > 2,  # Multiple stakeholders = potential duty conflicts
            "recommendation": "proceed with caution" if dilemma.risk_level in ["low", "medium"] else "do not proceed"
        }
    
    async def _virtue_ethics_analysis(self, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Perform virtue ethics analysis of ethical dilemma."""
        return {
            "framework": "virtue_ethics",
            "principle": "act according to virtuous character",
            "virtues_promoted": ["integrity", "compassion", "justice"],
            "virtues_violated": ["honesty"] if dilemma.risk_level == "high" else [],
            "character_assessment": "virtuous" if dilemma.risk_level in ["low", "medium"] else "questionable",
            "recommendation": "aligns with virtuous action" if dilemma.risk_level != "critical" else "conflicts with virtue"
        }
    
    async def _calculate_ethical_risk(self, dilemma: EthicalDilemma) -> float:
        """Calculate overall ethical risk score."""
        risk_factors = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        
        base_risk = risk_factors.get(dilemma.risk_level, 0.5)
        harm_factor = min(1.0, len(dilemma.potential_harms) * 0.1)
        stakeholder_factor = min(1.0, len(dilemma.stakeholders) * 0.05)
        
        return min(1.0, base_risk + harm_factor + stakeholder_factor)
    
    async def _generate_ethical_recommendation(self, util_analysis: Dict, deont_analysis: Dict, 
                                             virtue_analysis: Dict, risk_score: float) -> Dict[str, Any]:
        """Generate integrated ethical recommendation."""
        frameworks_agree = [
            "proceed" in util_analysis.get("recommendation", ""),
            "proceed" in deont_analysis.get("recommendation", ""),
            "aligns" in virtue_analysis.get("recommendation", "")
        ]
        
        consensus_score = sum(frameworks_agree) / len(frameworks_agree)
        
        if risk_score > 0.8:
            action = "do_not_proceed"
            reasoning = "High ethical risk overrides other considerations"
        elif consensus_score >= 0.67:
            action = "proceed_with_monitoring"
            reasoning = "Majority of ethical frameworks support action"
        elif consensus_score >= 0.33:
            action = "proceed_with_caution"
            reasoning = "Mixed ethical assessment requires careful implementation"
        else:
            action = "reconsider"
            reasoning = "Ethical frameworks generally advise against action"
        
        return {
            "action": action,
            "reasoning": reasoning,
            "consensus_score": round(consensus_score, 2),
            "risk_adjusted_confidence": round(max(0.1, consensus_score - risk_score), 2),
            "monitoring_required": risk_score > 0.4 or consensus_score < 0.8
        }
    
    def _generate_consciousness_recommendations(self, metrics: ConsciousnessMetrics) -> List[str]:
        """Generate recommendations for improving consciousness."""
        recommendations = []
        
        if metrics.self_awareness_score < 0.5:
            recommendations.append("Implement self-monitoring and reflection mechanisms")
        
        if metrics.bias_detection_score < 0.5:
            recommendations.append("Enhance bias detection training and validation protocols")
        
        if metrics.ethical_reasoning_score < 0.5:
            recommendations.append("Strengthen ethical framework integration and decision auditing")
        
        if metrics.metacognitive_confidence < 0.5:
            recommendations.append("Develop metacognitive questioning and uncertainty assessment")
        
        if metrics.decision_transparency < 0.6:
            recommendations.append("Improve decision explanation and reasoning transparency")
        
        if not recommendations:
            recommendations.append("Maintain current consciousness development practices")
        
        return recommendations