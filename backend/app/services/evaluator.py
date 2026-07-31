import time
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.schemas.execute import ExecuteRequest
from app.schemas.submission import (
    DifficultyBreakdown,
    RecentSubmissionItem,
    SubmitCodeRequest,
    SubmitCodeResponse,
    TestCaseResultItem,
    TopicStat,
    UserAnalyticsResponse,
)
from app.services.judge0_executor import judge0_executor


def normalize_output(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


class ProblemEvaluatorService:
    async def evaluate_and_submit(
        self,
        db: AsyncSession,
        user: User,
        problem: Problem,
        payload: SubmitCodeRequest,
    ) -> SubmitCodeResponse:
        test_cases = sorted(problem.test_cases, key=lambda tc: tc.position)
        results: list[TestCaseResultItem] = []
        passed_count = 0
        has_time_limit = False
        has_compile_error = False
        has_runtime_error = False

        start_time = time.perf_counter()

        for tc in test_cases:
            exec_payload = ExecuteRequest(
                language=payload.language,
                code=payload.code,
                stdin=tc.stdin,
            )
            exec_res = await judge0_executor.execute(exec_payload)

            actual_norm = normalize_output(exec_res.stdout)
            expected_norm = normalize_output(tc.expected_stdout)
            is_match = (
                exec_res.exit_code == 0
                and not exec_res.timed_out
                and actual_norm == expected_norm
            )

            if is_match:
                passed_count += 1
                status_desc = "Passed"
            elif exec_res.timed_out:
                has_time_limit = True
                status_desc = "Time Limit Exceeded"
            elif exec_res.exit_code != 0:
                if "error" in exec_res.stderr.lower() or "compil" in exec_res.stderr.lower():
                    has_compile_error = True
                else:
                    has_runtime_error = True
                status_desc = f"Execution Error (code {exec_res.exit_code})"
            else:
                status_desc = "Wrong Answer"

            results.append(
                TestCaseResultItem(
                    position=tc.position,
                    passed=is_match,
                    is_sample=tc.is_sample,
                    stdin=tc.stdin,
                    expected_stdout=tc.expected_stdout,
                    actual_stdout=exec_res.stdout,
                    stderr=exec_res.stderr,
                    status_description=status_desc,
                )
            )

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        total_tc = len(test_cases)

        if passed_count == total_tc and total_tc > 0:
            final_status = "ACCEPTED"
        elif has_time_limit:
            final_status = "TIME_LIMIT_EXCEEDED"
        elif has_compile_error:
            final_status = "COMPILE_ERROR"
        elif has_runtime_error:
            final_status = "RUNTIME_ERROR"
        else:
            final_status = "WRONG_ANSWER"

        submission = Submission(
            user_id=user.id,
            problem_id=problem.id,
            language=payload.language,
            code=payload.code,
            status=final_status,
            passed_test_cases=passed_count,
            total_test_cases=total_tc,
            runtime_ms=elapsed_ms,
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)

        return SubmitCodeResponse(
            submission_id=submission.id,
            problem_slug=problem.slug,
            status=final_status,  # type: ignore
            passed_test_cases=passed_count,
            total_test_cases=total_tc,
            runtime_ms=elapsed_ms,
            test_results=results,
        )

    async def get_user_analytics(
        self,
        db: AsyncSession,
        user: User,
    ) -> UserAnalyticsResponse:
        # Fetch all submissions by user
        stmt = (
            select(Submission, Problem)
            .join(Problem, Submission.problem_id == Problem.id)
            .where(Submission.user_id == user.id)
            .order_by(Submission.created_at.desc())
        )
        res = await db.execute(stmt)
        rows = res.all()

        total_submissions = len(rows)
        if total_submissions == 0:
            return UserAnalyticsResponse(
                total_solved=0,
                solved_by_difficulty=DifficultyBreakdown(easy=0, medium=0, hard=0),
                total_submissions=0,
                accuracy_rate=0.0,
                topic_stats=[],
                weak_topics=[],
                recent_submissions=[],
            )

        # Count distinct solved problems
        solved_stmt = (
            select(distinct(Problem.id), Problem.difficulty)
            .join(Submission, Submission.problem_id == Problem.id)
            .where(Submission.user_id == user.id, Submission.status == "ACCEPTED")
        )
        solved_res = await db.execute(solved_stmt)
        solved_rows = solved_res.all()

        total_solved = len(solved_rows)
        easy_count = sum(1 for _, diff in solved_rows if diff == "easy")
        medium_count = sum(1 for _, diff in solved_rows if diff == "medium")
        hard_count = sum(1 for _, diff in solved_rows if diff == "hard")

        accepted_submissions = sum(1 for sub, _ in rows if sub.status == "ACCEPTED")
        accuracy_rate = round((accepted_submissions / total_submissions) * 100, 1)

        # Topic breakdown
        topic_map: dict[str, dict[str, int]] = {}
        for sub, prob in rows:
            for tag in prob.tags or []:
                if tag not in topic_map:
                    topic_map[tag] = {"attempted": 0, "solved": 0}
                topic_map[tag]["attempted"] += 1

        for _, prob in rows:
            pass  # populate topic stats based on unique solved problem tags
        
        # Calculate topic solved count per tag
        solved_prob_ids = {p_id for p_id, _ in solved_rows}
        for sub, prob in rows:
            if prob.id in solved_prob_ids and sub.status == "ACCEPTED":
                for tag in prob.tags or []:
                    if tag in topic_map:
                        topic_map[tag]["solved"] += 1

        topic_stats: list[TopicStat] = []
        weak_topics: list[str] = []

        for tag, stats in topic_map.items():
            att = stats["attempted"]
            sol = stats["solved"]
            rate = round((sol / att) * 100, 1) if att > 0 else 0.0
            topic_stats.append(
                TopicStat(tag=tag, attempted=att, solved=sol, pass_rate=rate)
            )
            if rate < 60.0 or sol == 0:
                weak_topics.append(tag)

        topic_stats.sort(key=lambda x: x.pass_rate)

        # Recent 10 submissions
        recent_items: list[RecentSubmissionItem] = []
        for sub, prob in rows[:10]:
            recent_items.append(
                RecentSubmissionItem(
                    id=sub.id,
                    problem_slug=prob.slug,
                    problem_title=prob.title,
                    difficulty=prob.difficulty,
                    language=sub.language,
                    status=sub.status,
                    passed_test_cases=sub.passed_test_cases,
                    total_test_cases=sub.total_test_cases,
                    created_at=sub.created_at,
                )
            )

        return UserAnalyticsResponse(
            total_solved=total_solved,
            solved_by_difficulty=DifficultyBreakdown(
                easy=easy_count, medium=medium_count, hard=hard_count
            ),
            total_submissions=total_submissions,
            accuracy_rate=accuracy_rate,
            topic_stats=topic_stats,
            weak_topics=weak_topics,
            recent_submissions=recent_items,
        )


problem_evaluator_service = ProblemEvaluatorService()
