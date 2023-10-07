from channels.generic.websocket import AsyncWebsocketConsumer
import json


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        username = self.scope['user'].username
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat',
                'msg': f'你好,{username}, 欢迎进入{self.room_name}房间' ,
                'from': '系统',
                'to': username
            }
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        sender_user = self.scope["user"]
        if text_data:
            content = json.loads(text_data)
            if content['type'] == 'chat':
                content['from'] = sender_user.username
                await self.channel_layer.group_send(
                    self.room_group_name,
                    content
                )

    async def chat(self, content):
        await self.send(json.dumps(content, ensure_ascii=False))


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['user'].id
        self.room_group_name = f'user_{user_id}'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'remind',
                'msg': '你好,' + self.scope['user'].username,
                'from': '系统'
            }
        )
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            content = json.loads(text_data)
            if content['type'] == 'event':
                await self.channel_layer.group_add(
                    'event',
                    self.channel_name
                )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            'event',
            self.channel_name
        )

    async def event(self, content):
        await self.send(json.dumps(content, ensure_ascii=False))

    async def ticket(self, content):
        await self.send(json.dumps(content, ensure_ascii=False))

    async def remind(self, content):
        await self.send(json.dumps(content, ensure_ascii=False))
