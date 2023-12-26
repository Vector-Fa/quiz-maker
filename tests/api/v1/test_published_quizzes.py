import pytest
from httpx import AsyncClient


class TestPublishedQuizzes:
    @pytest.mark.asyncio
    async def test_check_quiz_password_status(
            self, http_client: AsyncClient, shared_quiz: dict
    ):
        response = await http_client.get(f'/quiz/pub/{shared_quiz["quiz_path"]}/password-status')
        assert response.status_code == 200

        data = response.json()
        assert data['need_password'] is False

    @pytest.mark.asyncio
    async def test_get_published_quiz_questions_without_password(
            self, http_client: AsyncClient, shared_quiz: dict
    ):
        response = await http_client.post(f'/quiz/pub/{shared_quiz["quiz_id"]}/get-questions', json={'password': None})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data['questions'], list)
        assert len(data['questions']) >= 1

        await self._answer_quiz_questions(http_client, data['questions'],
                                          shared_quiz['quiz_id'])

    async def _answer_quiz_questions(self, http_client: AsyncClient,
                                     questions: list, quiz_id: int):
        print(questions)
        assert isinstance(questions, list)
        answer_data = {
            "participant_info": {
                "username": "alireza felani"
            },
            "descriptive": [],
            "multiple_options": [],
        }

        for q in questions:
            if q['question_type'] == 'descriptive_short_answer':
                answer_data['descriptive'].append(
                    {
                        'question_id': q['id'],
                        'answer': 'my answer'
                    }
                )
            elif q['question_type'] == 'multiple_options':
                answer_data['multiple_options'].append(
                    {
                        'question_id': q['id'],
                        'option_id': q['choices'][1]['id']
                    }
                )
        response = await http_client.post(f'/quiz/pub/{quiz_id}', json=answer_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_participant_answers(self):
        ...

    @pytest.mark.asyncio
    async def test_get_all_quiz_participants_answers_with_score(
            self,
            user_client: AsyncClient,
            shared_quiz: dict
    ):
        response = await user_client.get(
            f'/quiz/pub/{shared_quiz["quiz_id"]}/all/answers'
        )
        data = response.json()
        assert response.status_code == 200
        assert isinstance(data['total_quiz_score'], float)
        assert isinstance(data['participant_answers'], list)

    @pytest.mark.asyncio
    async def test_get_one_participant_answers(self):
        ...