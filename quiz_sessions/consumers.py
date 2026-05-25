import json

from channels.generic.websocket import AsyncWebsocketConsumer


class LobbyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.lobby_group_name = "lobby"

        await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name,
        )

        await self.accept()

        await self.send(
            json.dumps(
                {
                    "type": "lobby_update",
                    "users": [],
                },
            ),
        )

    async def disconnect(self, close_code):
        if hasattr(self, "lobby_group_name"):
            await self.channel_layer.group_discard(
                self.lobby_group_name,
                self.channel_name,
            )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data.get("type") == "join_lobby":
            await self.send(
                json.dumps(
                    {
                        "type": "lobby_update",
                        "users": [],
                    },
                ),
            )

    async def lobby_update(self, event):
        await self.send(
            text_data=json.dumps(
                event,
            ),
        )


class QuizSessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.quiz_id = self.scope["url_route"]["kwargs"]["quiz_id"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.quiz_group_name = f"quiz_{self.quiz_id}"

        await self.channel_layer.group_add(
            self.quiz_group_name,
            self.channel_name,
        )

        await self.accept()

        await self.send(
            json.dumps(
                {
                    "type": "session_started",
                    "quiz_id": self.quiz_id,
                },
            ),
        )

    async def disconnect(self, close_code):
        if hasattr(self, "quiz_group_name"):
            await self.channel_layer.group_discard(
                self.quiz_group_name,
                self.channel_name,
            )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data.get("type") == "submit_answer":
            question_id = data.get("question_id")
            answer_id = data.get("answer_id")

            await self.send(
                json.dumps(
                    {
                        "type": "answer_submitted",
                        "question_id": question_id,
                        "answer_id": answer_id,
                    },
                ),
            )

    async def quiz_progress(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "progress_update",
                    "current_question": event.get("current_question"),
                },
            ),
        )
