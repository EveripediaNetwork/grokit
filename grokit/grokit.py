#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from typing import Optional, Generator, Dict, Any, Union
from enum import Enum
from os import environ as env


class GrokModels(Enum):
    GROK_2 = 'grok-2'
    GROK_2_MINI = 'grok-2-mini'


class Grokit:
    BEARER_TOKEN = (
        'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs'
        '%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
    )

    def __init__(
        self,
        auth_token: Optional[str] = None,
        csrf_token: Optional[str] = None,
    ):
        self.auth_token = auth_token or env.get('X_AUTH_TOKEN')
        self.csrf_token = csrf_token or env.get('X_CSRF_TOKEN')
        self._validate_tokens()
        self.cookie = self._create_cookie()
        self.headers = self._create_headers()

    def _validate_tokens(self) -> None:
        if not self.auth_token or not self.csrf_token:
            raise ValueError('X_AUTH_TOKEN and X_CSRF_TOKEN must be provided')

    def _create_cookie(self) -> str:
        return 'auth_token={0}; ct0={1};'.format(
            self.auth_token,
            self.csrf_token,
        )

    def _create_headers(self) -> Dict[str, str]:
        return {
            'X-Csrf-Token': self.csrf_token,
            'authorization': 'Bearer {}'.format(self.BEARER_TOKEN),
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
        }

    def create_conversation(self) -> Optional[str]:
        url = ('https://x.com/i/api/graphql/UBIjqHqsA5aixuibXTBheQ/'
               'CreateGrokConversation')
        payload = {
            'variables': {},
            'queryId': 'UBIjqHqsA5aixuibXTBheQ',
        }

        response = self._make_request(url, payload)
        if response and 'data' in response:
            return (
                response['data']['create_grok_conversation']['conversation_id']
            )
        return None

    def generate(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt_name: str = '',
        model_id: Union[GrokModels, str] = GrokModels.GROK_2_MINI,
    ) -> str:
        conversation_id = self._ensure_conversation_id(conversation_id)
        response = ''.join(self._stream_response(
            conversation_id,
            message,
            system_prompt_name,
            model_id,
        ))
        return response

    def stream(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt_name: str = '',
        model_id: Union[GrokModels, str] = GrokModels.GROK_2_MINI,
    ) -> Generator[str, None, None]:
        conversation_id = self._ensure_conversation_id(conversation_id)
        yield from self._stream_response(
            conversation_id,
            message,
            system_prompt_name,
            model_id,
        )

    def image(self, prompt: str) -> bytes:
        image_url = self._get_image_url(prompt)
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            return image_response.content
        raise ValueError('Failed to download the image')

    def image_url(self, prompt: str) -> str:
        return self._get_image_url(prompt)

    def _get_image_url(self, prompt: str) -> str:
        conversation_id = self.create_conversation()
        if not conversation_id:
            raise ValueError('Failed to create conversation')
        image_prompt = 'Generate an image of "{}"'.format(prompt)
        response = self._stream_response(
            conversation_id,
            image_prompt,
            '',
            GrokModels.GROK_2_MINI,
        )

        for chunk in response:
            try:
                data = json.loads(chunk)
                if 'result' in data and 'imageAttachment' in data['result']:
                    return data['result']['imageAttachment']['imageUrl']
            except json.JSONDecodeError:
                continue

        raise ValueError('Failed to generate the image')

    def _ensure_conversation_id(self, conversation_id: Optional[str]) -> str:
        if not conversation_id:
            conversation_id = self.create_conversation()
            if not conversation_id:
                raise ValueError('Failed to create conversation')
        return conversation_id

    def _stream_response(
        self,
        conversation_id: str,
        message: str,
        system_prompt_name: str,
        model_id: Union[GrokModels, str],
    ) -> Generator[str, None, None]:
        url = 'https://api.x.com/2/grok/add_response.json'
        payload = self._create_add_response_payload(
            conversation_id,
            message,
            system_prompt_name,
            model_id,
        )

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            stream=True,
        )

        if response.status_code == 200:
            yield from self._process_response_stream(response)
        else:
            print('Error adding response: {}'.format(response.text))

    def _make_request(
        self,
        url: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print('Error making request: {}'.format(response.text))
            return None

    def _create_add_response_payload(
        self,
        conversation_id: str,
        message: str,
        system_prompt_name: str,
        model_id: Union[GrokModels, str],
    ) -> Dict[str, Any]:
        return {
            'responses': [
                {
                    'message': message,
                    'sender': 1,
                },
            ],
            'systemPromptName': system_prompt_name,
            'grokModelOptionId': (
                model_id.value if isinstance(model_id, GrokModels)
                else model_id
            ),
            'conversationId': conversation_id,
        }

    def _process_response_stream(
        self,
        response: requests.Response,
    ) -> Generator[str, None, None]:
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'result' in chunk:
                    if 'message' in chunk['result']:
                        yield chunk['result']['message']
                    elif 'imageAttachment' in chunk['result']:
                        yield json.dumps(chunk)
