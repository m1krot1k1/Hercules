"""
Self-Evaluation and Auto-Correction System for Hercules Agent.

Implements self-evaluation loops, cross-verification via delegate_task,
and automated error correction.
"""

import json
import logging
from typing import Dict, List, Optional, Any

from hermes_constants import get_hermes_home
from hermes_logging import setup_logging

logger = logging.getLogger(__name__)

# Threshold for passing self-evaluation
PASS_THRESHOLD = 0.8


class SelfEvaluation:
    """
    System for self-evaluation and auto-correction of agent results.
    Uses delegate_task to spawn reviewer agents for cross-verification.
    """

    def __init__(
        self,
        agent_id: str,
        max_iterations: int = 3,
        delegate_func: Optional[Any] = None
    ):
        """
        Initialize the SelfEvaluation system.

        Args:
            agent_id: Identifier of the agent performing evaluation.
            max_iterations: Maximum number of correction loops (default: 3).
            delegate_func: Function to call delegate_task (e.g., tools/delegate_tool.py logic).
                          If None, evaluation runs in standalone mode (mocked).
        """
        self.agent_id = agent_id
        self.max_iterations = max_iterations
        self.iteration = 0
        self.evaluation_history = []
        self._delegate = delegate_func

    def evaluate_result(self, result: str, goal: str, context: str) -> Dict:
        """
        Evaluate the result based on the goal and context using an internal review prompt.
        In a real scenario, this would call an LLM or a specialized reviewer agent.

        Returns:
            dict: {
                "score": float (0.0 to 1.0),
                "issues": list of str,
                "suggestions": list of str,
                "passed": bool (score >= 0.8)
            }
        """
        # In a full implementation, this would use delegate_task to ask a reviewer agent.
        # For now, we simulate a basic evaluation structure.
        # TODO: Implement actual LLM-based evaluation or delegate to 'code-reviewer'.
        
        # Mock evaluation logic (replace with actual agent call)
        score = 0.9  # Assume high score for now
        issues = []
        suggestions = []

        if not result or len(result.strip()) < 10:
            score = 0.3
            issues.append("Result is too short or empty.")
            suggestions.append("Provide a more detailed response.")

        if goal.lower() not in result.lower() and "error" not in result.lower():
            # Simple heuristic: check if goal keywords appear in result
            pass  # Complex goals might not need direct keyword match

        evaluation = {
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "passed": score >= PASS_THRESHOLD
        }
        
        self.evaluation_history.append({
            "iteration": self.iteration,
            "type": "self-eval",
            "result": evaluation
        })
        
        logger.info(
            f"[SelfEval] Agent {self.agent_id}: Score={score:.2f}, "
            f"Passed={evaluation['passed']}, Issues={len(issues)}"
        )
        return evaluation

    def cross_verify(self, result: str, verifier_agent: str = "code-reviewer") -> Dict:
        """
        Cross-verification: Another agent checks the result using delegate_task.
        
        Args:
            result: The result string to verify.
            verifier_agent: The agent to use for verification (default: code-reviewer).
            
        Returns:
            dict: {
                "verified": bool,
                "issues": list of str,
                "verifier_notes": str
            }
        """
        logger.info(f"[SelfEval] Starting cross-verification with {verifier_agent}")
        
        if self._delegate:
            try:
                # Construct a verification task
                verify_task = (
                    f"Please verify the following result for correctness, completeness, "
                    f"and quality:\n\n{result}\n\n"
                    f"List any issues found. If none, state 'Verified: OK'."
                )
                
                # Call delegate_task
                verification_response = self._delegate(
                    goal=verify_task,
                    role="leaf",
                    toolsets=["code-reviewer"] # Simplified
                )
                
                # Parse response
                # Expecting JSON like {"status": "success", "output": "..."}
                if isinstance(verification_response, str):
                    try:
                        resp_data = json.loads(verification_response)
                    except json.JSONDecodeError:
                        resp_data = {"status": "error", "output": verification_response}
                else:
                    resp_data = verification_response if isinstance(verification_response, dict) else {}
                
                notes = resp_data.get("output", str(verification_response))
                verified = "verified" in notes.lower() or "ok" in notes.lower()
                issues = []
                if not verified:
                    issues.append(notes)
                
            except Exception as e:
                logger.error(f"Cross-verification failed: {e}")
                verified = False
                issues = [f"Verification error: {str(e)}"]
                notes = f"Error during verification: {str(e)}"
        else:
            # Standalone mode (no delegate function provided)
            logger.warning("No delegate function provided. Skipping cross-verification.")
            verified = True
            issues = []
            notes = "Cross-verification skipped (no delegate func)."

        result_dict = {
            "verified": verified,
            "issues": issues,
            "verifier_notes": notes
        }
        
        self.evaluation_history.append({
            "iteration": self.iteration,
            "type": "cross-verify",
            "result": result_dict
        })
        
        return result_dict

    def auto_correct(self, result: str, issues: List[str], suggestions: List[str]) -> str:
        """
        Automatically correct errors found in the result.
        In a full implementation, this would use an LLM to refine the result
        based on the provided issues and suggestions.

        Returns:
            str: Corrected result.
        """
        logger.info(f"[SelfEval] Auto-correcting result. Issues: {len(issues)}")
        
        if not issues:
            return result
            
        # Mock correction: append a note about corrections
        # In reality, this would re-run the agent with feedback or use a patch tool.
        corrected = (
            f"{result}\n\n"
            f"[Auto-Correction Applied]\n"
            f"Issues addressed: {', '.join(issues)}\n"
            f"Suggestions applied: {', '.join(suggestions)}"
        )
        
        self.evaluation_history.append({
            "iteration": self.iteration,
            "type": "auto-correct",
            "original_length": len(result),
            "corrected_length": len(corrected)
        })
        
        return corrected

    def run_evaluation_loop(self, initial_result: str, goal: str, context: str) -> Dict:
        """
        Full self-evaluation cycle with up to max_iterations iterations.
        
        Returns:
            dict: {
                "final_result": str,
                "iterations": int,
                "passed": bool,
                "evaluation_history": list
            }
        """
        current_result = initial_result
        self.iteration = 0
        passed = False

        logger.info(f"[SelfEval] Starting evaluation loop for agent {self.agent_id}")

        for i in range(self.max_iterations):
            self.iteration = i + 1
            logger.info(f"[SelfEval] Iteration {self.iteration}/{self.max_iterations}")

            # 1. Evaluate
            eval_result = self.evaluate_result(current_result, goal, context)
            
            if eval_result["passed"]:
                logger.info(f"[SelfEval] Passed on iteration {self.iteration}")
                passed = True
                break
            
            # 2. Correct if failed
            if eval_result["issues"]:
                current_result = self.auto_correct(
                    current_result,
                    eval_result["issues"],
                    eval_result["suggestions"]
                )
            else:
                # No issues listed but score low? Break to avoid loop.
                break

        # 3. Cross-Verification (after loop)
        if passed:
            verify_result = self.cross_verify(current_result)
            if not verify_result["verified"]:
                # If verification fails, we might want to log it but still return the result
                logger.warning(f"[SelfEval] Cross-verification failed: {verify_result['verifier_notes']}")

        return {
            "final_result": current_result,
            "iterations": self.iteration,
            "passed": passed,
            "evaluation_history": self.evaluation_history
        }
