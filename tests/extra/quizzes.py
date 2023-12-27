from datetime import datetime, timedelta, timezone

from httpx import AsyncClient


async def update_quiz_date_times(user_client: AsyncClient, quiz_id: int) -> None:
    data = {
        "start_at": str(datetime.now(tz=timezone.utc) + timedelta(milliseconds=5)),
        "end_at": str(datetime.now(tz=timezone.utc) + timedelta(minutes=30)),
    }
    response = await user_client.patch(f"/quiz/{quiz_id}", json=data)
    assert response.status_code == 200


async def create_short_question_for_quiz(
    user_client: AsyncClient, quiz_id: int
) -> dict:
    short_descriptive_question_data = {
        "question": "my new descriptive question",
        "answer": "optional answer",
        "score": 1.5,
        "quiz_id": quiz_id,
    }
    response = await user_client.post(
        "/quiz/add/question/descriptive-short", json=short_descriptive_question_data
    )
    question_json = response.json()
    assert response.status_code == 200
    return question_json
