from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from tests.extra.quizzes import create_short_question_for_quiz, update_quiz_date_times


class TestQuizzes:
    @pytest.mark.asyncio
    async def test_fail_delete_another_user_quiz(
        self, quiz_another_user: dict, user_client: AsyncClient
    ):
        response = await user_client.delete(f'/quiz/delete/{quiz_another_user["id"]}')
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_can_access_user_quizzes(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        # TODO: add ability to create admins
        ...

    @pytest.mark.asyncio
    async def test_delete_quiz(self, user_client: AsyncClient, new_quiz: dict):
        assert new_quiz.get("id") is not None
        response = await user_client.delete(f'/quiz/delete/{new_quiz["id"]}')
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_all_created_quizzes(self, user_client: AsyncClient):
        response = await user_client.get("/quiz/all")
        assert response.status_code == 200
        assert type(response.json()) is list

    @pytest.mark.asyncio
    async def test_fail_delete_quiz_wrong_id(self, user_client: AsyncClient):
        response = await user_client.delete(f"/quiz/delete/{9999999}")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_short_descriptive_question_for_quiz(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        short_descriptive_question_data = {
            "question": "my new descriptive question",
            "answer": "optional answer",
            "score": 1.5,
            "quiz_id": new_quiz["id"],
        }
        response = await user_client.post(
            "/quiz/add/question/descriptive-short", json=short_descriptive_question_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["question_type"] == "descriptive_short_answer"
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_create_long_descriptive_question_for_quiz(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        long_descriptive_question_data = {
            "question": "my new descriptive question",
            "answer": "optional answer",
            "score": 1.5,
            "quiz_id": new_quiz["id"],
        }
        response = await user_client.post(
            "/quiz/add/question/descriptive-long", json=long_descriptive_question_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["question_type"] == "descriptive_long_answer"
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_create_multiple_option_for_quiz(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        multiple_option_question_data = {
            "question": "my multiple option question",
            "quiz_id": new_quiz["id"],
            "score": 1.5,
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
            "/quiz/add/question/multiple-option", json=multiple_option_question_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question_type"] == "multiple_options"
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_fail_create_multiple_option_question_with_empty_answer_list(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        multiple_option_question_data = {
            "question": "my multiple option question",
            "options": [],
            "quiz_id": new_quiz["id"],
            "correct_option_index": 0,
        }
        response = await user_client.post(
            "/quiz/add/question/multiple-option", json=multiple_option_question_data
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_questions_for_one_quiz(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        response = await user_client.get(f'/quiz/{new_quiz["id"]}/questions')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["questions"], list)
        assert data["quiz_id"] == new_quiz["id"]

    @pytest.mark.asyncio
    async def test_create_question_and_delete_id(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        long_descriptive_question_data = {
            "question": "my new descriptive question",
            "answer": "optional answer",
            "score": 1.5,
            "quiz_id": new_quiz["id"],
        }
        response = await user_client.post(
            "/quiz/add/question/descriptive-long", json=long_descriptive_question_data
        )
        assert response.status_code == 200
        data = response.json()
        delete_response = await user_client.delete(
            f'/quiz/delete/question/{data["id"]}/quiz/{new_quiz["id"]}'
        )
        assert delete_response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_quiz_password(self, user_client: AsyncClient, new_quiz: dict):
        data = {"password": "new_password", "quiz_lock": False}
        response = await user_client.post(
            f'/quiz/set/password/{new_quiz["id"]}', json=data
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_all_quiz_settings(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        data = {
            "title": "new title",
            "start_at": str(datetime.now(tz=timezone.utc) + timedelta(minutes=5)),
            "end_at": str(datetime.now(tz=timezone.utc) + timedelta(minutes=30)),
            "quiz_path": "NewQuizPathForParticipants",
            "shuffle_options": True,
        }
        response = await user_client.patch(f'/quiz/{new_quiz["id"]}', json=data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_changing_quiz_activation_status(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        await update_quiz_date_times(user_client=user_client, quiz_id=new_quiz["id"])
        await create_short_question_for_quiz(
            user_client=user_client, quiz_id=new_quiz["id"]
        )
        # activate quiz
        response = await user_client.post(
            f'/quiz/{new_quiz["id"]}/change-activation-status'
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

        # de activate quiz
        response = await user_client.post(
            f'/quiz/{new_quiz["id"]}/change-activation-status'
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    @pytest.mark.skip
    async def test_update_descriptive_question(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        question_json = await create_short_question_for_quiz(
            user_client=user_client, quiz_id=new_quiz["id"]
        )
        update_question_data = {
            "text": "new question text",
            "new_score": 1.5,
            "answer": "new answer",
        }
        response = await user_client.put(
            f'/quiz/{new_quiz["id"]}/edit/question/{question_json["id"]}/descriptive',
            json=update_question_data,
        )
        assert response.status_code == 200
        updated_question_data = response.json()  # should I continue testing

    @pytest.mark.asyncio
    async def test_update_multiple_option_question(
        self, user_client: AsyncClient, new_quiz: dict
    ):
        multiple_option_question_data = {
            "question": "my multiple option question",
            "quiz_id": new_quiz["id"],
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
            "/quiz/add/question/multiple-option", json=multiple_option_question_data
        )
        assert response.status_code == 200
        question_json = response.json()

        update_question_data = {
            "text": "new question test",
            "quiz_id": new_quiz["id"],
            "new_score": 1.75,
            "options": [
                {"text": "updated wrong answer"},
                {"text": "updated correct answer in index 1 of options list"},
                {"text": "new answer added"},
            ],
            "correct_option_index": 1,
        }
        response = await user_client.put(
            f'/quiz/{new_quiz["id"]}/edit/question/{question_json["id"]}/multiple-option',
            json=update_question_data,
        )
        assert response.status_code == 200
        updated_question_data = response.json()  # should I continue testing
