import pytest
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import path

from quiz_sessions.consumers import LobbyConsumer, QuizSessionConsumer
from tests.factories.quiz_factory import QuizFactory
from tests.factories.user_factory import CustomUserFactory


@pytest.fixture
def authenticated_user(db):
    return CustomUserFactory()


@pytest.fixture
def quiz(db):
    return QuizFactory()


class TestLobbyConsumer:

    @pytest.mark.asyncio
    async def test_connect_successful(self, authenticated_user):
        application = URLRouter(
            [
                path("ws/lobby/", AuthMiddlewareStack(LobbyConsumer.as_asgi())),
            ],
        )
        communicator = WebsocketCommunicator(application, "/ws/lobby/")
        communicator.scope["user"] = authenticated_user

        connected, subprotocol = await communicator.connect()
        assert connected is True
        assert subprotocol is None
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_receive_lobby_updates(self, authenticated_user, quiz):
        application = URLRouter(
            [
                path("ws/lobby/", AuthMiddlewareStack(LobbyConsumer.as_asgi())),
            ],
        )

        communicator = WebsocketCommunicator(application, "/ws/lobby/")
        communicator.scope["user"] = authenticated_user

        await communicator.connect()
        await communicator.send_json_to(
            {
                "type": "join_lobby",
                "quiz_id": quiz.id,
            },
        )
        response = await communicator.receive_json_from(timeout=1)

        assert response["type"] == "lobby_update"
        assert "users" in response

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_unauthorized_connection(self):
        application = URLRouter(
            [
                path("ws/lobby/", AuthMiddlewareStack(LobbyConsumer.as_asgi())),
            ],
        )

        communicator = WebsocketCommunicator(application, "/ws/lobby/")

        connected, close_code = await communicator.connect()

        assert connected is False
        assert close_code == 1000

        await communicator.disconnect()


class TestQuizSessionConsumer:

    @pytest.mark.asyncio
    async def test_join_quiz_session(self, authenticated_user, quiz):
        application = URLRouter(
            [
                path(
                    "ws/quiz/<int:quiz_id>/",
                    AuthMiddlewareStack(QuizSessionConsumer.as_asgi()),
                ),
            ],
        )

        communicator = WebsocketCommunicator(application, f"/ws/quiz/{quiz.id}/")
        communicator.scope["user"] = authenticated_user

        connected, subprotocol = await communicator.connect()
        assert connected is True

        response = await communicator.receive_json_from(timeout=1)
        assert response["type"] == "session_started"
        assert "quiz_id" in response

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_submit_answer(self, authenticated_user, quiz):
        application = URLRouter(
            [
                path(
                    "ws/quiz/<int:quiz_id>/",
                    AuthMiddlewareStack(QuizSessionConsumer.as_asgi()),
                ),
            ],
        )

        communicator = WebsocketCommunicator(application, f"/ws/quiz/{quiz.id}/")
        communicator.scope["user"] = authenticated_user

        await communicator.connect()

        await communicator.receive_json_from(timeout=1)

        await communicator.send_json_to(
            {
                "type": "submit_answer",
                "question_id": 1,
                "answer_id": 42,
            },
        )

        response = await communicator.receive_json_from(timeout=1)
        assert response["type"] == "answer_submitted"

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_quiz_progress_updates(self, authenticated_user, quiz):
        application = URLRouter(
            [
                path(
                    "ws/quiz/<int:quiz_id>/",
                    AuthMiddlewareStack(QuizSessionConsumer.as_asgi()),
                ),
            ],
        )

        communicator = WebsocketCommunicator(application, f"/ws/quiz/{quiz.id}/")
        communicator.scope["user"] = authenticated_user

        await communicator.connect()

        response = await communicator.receive_json_from(timeout=1)
        assert response["type"] == "session_started"

        await communicator.disconnect()
