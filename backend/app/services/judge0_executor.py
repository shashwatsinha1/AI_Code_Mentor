import asyncio
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.execute import ExecuteRequest, ExecuteResponse

LANGUAGE_IDS = {
    "cpp": 54,
    "java": 62,
    "python": 71,
}

TERMINAL_STATUS_IDS = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}
POLL_INTERVAL_SECONDS = 0.75


class Judge0Executor:
    def __init__(self) -> None:
        self.base_url = settings.judge0_api_url.rstrip("/")
        self.timeout_seconds = settings.judge0_timeout_seconds

    async def execute(self, payload: ExecuteRequest) -> ExecuteResponse:
        language_id = LANGUAGE_IDS[payload.language]
        headers = self._headers()
        submission = {
            "source_code": payload.code,
            "language_id": language_id,
            "stdin": payload.stdin or "",
            "cpu_time_limit": 3,
            "wall_time_limit": 8,
            "memory_limit": 128000,
            "enable_network": False,
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                created = await client.post(
                    f"{self.base_url}/submissions",
                    params={"base64_encoded": "false", "wait": "false"},
                    headers=headers,
                    json=submission,
                )
                created.raise_for_status()
                token = created.json()["token"]
                result = await self._poll_submission(client, token, headers)
        except (httpx.HTTPError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Judge0 execution service is unavailable. Check your Judge0 API settings.",
            ) from exc

        return self._to_execute_response(result)

    async def _poll_submission(
        self,
        client: httpx.AsyncClient,
        token: str,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        deadline = asyncio.get_running_loop().time() + self.timeout_seconds
        fields = "stdout,stderr,compile_output,message,exit_code,status,time,memory"

        while True:
            response = await client.get(
                f"{self.base_url}/submissions/{token}",
                params={"base64_encoded": "false", "fields": fields},
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
            status_id = result.get("status", {}).get("id")
            if status_id in TERMINAL_STATUS_IDS:
                return result
            if asyncio.get_running_loop().time() >= deadline:
                return {
                    "stdout": result.get("stdout") or "",
                    "stderr": result.get("stderr") or "",
                    "compile_output": result.get("compile_output") or "",
                    "message": "Execution timed out while waiting for Judge0.",
                    "exit_code": 124,
                    "status": {"id": 5, "description": "Time Limit Exceeded"},
                }
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.judge0_auth_token:
            headers["X-Auth-Token"] = settings.judge0_auth_token.get_secret_value()
        if settings.judge0_rapidapi_key:
            headers["X-RapidAPI-Key"] = settings.judge0_rapidapi_key.get_secret_value()
        if settings.judge0_rapidapi_host:
            headers["X-RapidAPI-Host"] = settings.judge0_rapidapi_host
        return headers

    def _to_execute_response(self, result: dict[str, Any]) -> ExecuteResponse:
        status_info = result.get("status") or {}
        status_id = status_info.get("id")
        status_description = status_info.get("description") or "Unknown"
        stderr_parts = [
            result.get("stderr") or "",
            result.get("compile_output") or "",
            result.get("message") or "",
        ]
        stderr = "\n".join(part for part in stderr_parts if part).strip()

        if status_id and status_id != 3 and not stderr:
            stderr = status_description

        return ExecuteResponse(
            stdout=result.get("stdout") or "",
            stderr=stderr,
            exit_code=result.get("exit_code") if result.get("exit_code") is not None else 1,
            timed_out=status_id == 5,
        )


judge0_executor = Judge0Executor()
