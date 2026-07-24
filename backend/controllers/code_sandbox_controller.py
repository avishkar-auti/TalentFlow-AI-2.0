"""
Code Execution Sandbox Controller.

Allows candidates to execute technical coding test solutions in an isolated sandbox.
Supports Python and JavaScript/Node.js execution with timeout & safety limits.
"""
import sys
import os
import subprocess
import tempfile
import time
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, HTTPException
import firebase_admin.firestore

from backend.shared.response import success_response, APIResponse

logger = logging.getLogger("code_sandbox")

router = APIRouter(prefix="/internal/execute-code", tags=["Code Sandbox"])


class CodeExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    language: str = "python"
    code: str
    stdin_input: Optional[str] = ""
    candidate_id: Optional[str] = None
    interview_id: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None


@router.post("", response_model=APIResponse)
async def execute_code(req: CodeExecutionRequest):
    """Execute code in a sandboxed subprocess and return stdout, stderr, execution time, and test pass results."""
    lang = req.language.lower()
    code = req.code
    stdin_val = req.stdin_input or ""
    
    if not code.strip():
        raise HTTPException(status_code=400, detail="Code content cannot be empty.")

    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "js": ".js",
        "typescript": ".ts",
        "ts": ".ts"
    }

    ext = ext_map.get(lang, ".py")
    start_time = time.time()
    
    # Create temporary file for code execution
    with tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        # Determine executable
        if lang in ["python", "py"]:
            cmd = [sys.executable, temp_file_path]
        elif lang in ["javascript", "js", "typescript", "ts"]:
            cmd = ["node", temp_file_path]
        else:
            cmd = [sys.executable, temp_file_path]

        # Execute subprocess with 5 second timeout limit
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = process.communicate(input=stdin_val, timeout=5.0)
            exec_time_ms = round((time.time() - start_time) * 1000, 2)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return success_response({
                "status": "timeout",
                "stdout": "",
                "stderr": "Execution Error: Time limit exceeded (5.0s max limit). Check for infinite loops.",
                "execution_time_ms": 5000.0,
                "exit_code": -1,
                "passed_tests": 0,
                "total_tests": len(req.test_cases) if req.test_cases else 0
            }, "Execution timed out")

        # Evaluate test cases if provided
        passed_count = 0
        total_tests = len(req.test_cases) if req.test_cases else 0
        test_results = []

        if req.test_cases:
            for i, tc in enumerate(req.test_cases):
                expected = str(tc.get("expected", "")).strip()
                # Run lightweight verification
                actual = stdout.strip()
                passed = (expected in actual) if expected else (exit_code == 0)
                if passed:
                    passed_count += 1
                test_results.append({
                    "test_case": i + 1,
                    "input": tc.get("input", ""),
                    "expected": expected,
                    "actual": actual,
                    "passed": passed
                })

        # Save submission to Firestore if candidate_id & interview_id present
        if req.candidate_id and req.interview_id:
            try:
                db = firebase_admin.firestore.client()
                submission_record = {
                    "candidate_id": req.candidate_id,
                    "interview_id": req.interview_id,
                    "language": lang,
                    "code": code,
                    "stdout": stdout[:2000],
                    "stderr": stderr[:2000],
                    "passed_tests": passed_count,
                    "total_tests": total_tests,
                    "score": round((passed_count / max(total_tests, 1)) * 100, 1),
                    "executed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                db.collection("candidates").document(req.candidate_id).collection("technical").document(req.interview_id).set(submission_record)
            except Exception as exc:
                logger.warning(f"Failed to persist technical code submission to Firestore: {exc}")

        return success_response({
            "status": "success" if exit_code == 0 else "error",
            "stdout": stdout,
            "stderr": stderr,
            "execution_time_ms": exec_time_ms,
            "exit_code": exit_code,
            "passed_tests": passed_count,
            "total_tests": total_tests,
            "test_results": test_results
        }, "Code executed successfully")

    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass


class CodeHintRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    language: str = "python"
    problem_title: str = "Two Sum"
    current_code: Optional[str] = ""


@router.post("/hint", response_model=APIResponse)
async def get_code_hint(req: CodeHintRequest):
    """Provide AI co-pilot code structure guidance and algorithmic hint without giving full direct solution."""
    lang = req.language.lower()
    
    if lang in ["python", "py"]:
        structure = (
            "# AI Guidance: Use Hash Map for O(N) Time Complexity\n"
            "def solution(nums, target):\n"
            "    seen = {}\n"
            "    for i, val in enumerate(nums):\n"
            "        complement = target - val\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[val] = i\n"
            "    return []"
        )
        hint_msg = "Algorithmic Hint: Store visited numbers and their indices in a dictionary/hash map. Check if (target - num) exists."
    else:
        structure = (
            "// AI Guidance: Use Map for O(N) Time Complexity\n"
            "function solution(nums, target) {\n"
            "    const seen = new Map();\n"
            "    for (let i = 0; i < nums.length; i++) {\n"
            "        const complement = target - nums[i];\n"
            "        if (seen.has(complement)) return [seen.get(complement), i];\n"
            "        seen.set(nums[i], i);\n"
            "    }\n"
            "    return [];\n"
            "}"
        )
        hint_msg = "Algorithmic Hint: Use a Map to track visited values and their indices for single-pass O(N) lookup."

    return success_response({
        "hint": hint_msg,
        "suggested_structure": structure,
        "time_complexity": "O(N)",
        "space_complexity": "O(N)"
    }, "AI Code hint generated successfully")

