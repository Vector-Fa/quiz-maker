from httpx import AsyncClient


async def create_questions(quiz_id: int, user_client: AsyncClient):
    descriptive_question = {
        "question": "my new descriptive question for shared quiz",
        "score": 1.5,
        "quiz_id": quiz_id,
    }
    response = await user_client.post(
        "/quiz/add/question/descriptive-short", json=descriptive_question
    )
    assert response.status_code == 200

    multiple_option_question = {
        "question": "my multiple option question for shared quiz",
        "quiz_id": quiz_id,
        "score": 2.75,
        "options": [
            {
                "text": "wrong answer",
            },
            {
                "text": "correct answer in index 1 of options list",
            },
        ],
        "correct_option_index": 1,
    }
    response = await user_client.post(
        "/quiz/add/question/multiple-option", json=multiple_option_question
    )
    assert response.status_code == 200
