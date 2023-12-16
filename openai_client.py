import os # If api key as en environment variable
import json
import time
from typing import List

import openai
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from logos_app import search_logos_library


class OpenAIClient:
    def __init__(self, model: str|None = None):
        # For simplicity, we assume the api key is stored as an environment variable
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.openai = openai
        self.openai.api_key = self.api_key
        self.last_response_obj = None
        self.messages = list()
        self.model = model

    def list_models(self) -> List[dict]:
        client = openai.OpenAI()
        models_list = client.models.list()
        return models_list.model_dump()

    def request_completion(self, temp: float = 1.0, max_tokens: int = 16, num_completions: int = 1, tools: list|None = None, tool_choice: str|None = None, print_response=True) -> None:
        """
        Since this is just an example, we don't worry about a function that can handle all possible parameters of the OpenAI API.
        Note that we only run one follow-up completion.
        """
        if self.model is None:
            print("[ERROR] No model specified. Please specify a model. E.g., client.model = 'gpt-4' OR during instantiation: client = OpenAIClient(model='gpt-4')")
            return
        # Attempting to use tool_choice arg without tools arg will result in an error
        if tools is not None and tool_choice is None:
            tool_choice = "auto"
        elif tools is None and tool_choice is not None:
            print("[ERROR] Cannot use tool_choice without tools. Please provide tools or remove tool_choice argument.")
            return
        
        client = openai.OpenAI()
        response_object = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=temp,
            max_tokens=max_tokens,
            n=num_completions,
            tools=tools,
            tool_choice=tool_choice,
        )

        self.messages.append(response_object.choices[0].message)
        tool_calls = response_object.choices[0].message.tool_calls
        if tool_calls:
            run_follow_up = self._handle_tool_calls(tool_calls)
            if run_follow_up:
                self.request_completion(
                    temp=temp,
                    max_tokens=max_tokens,
                    num_completions=num_completions,
                    print_response=print_response
                )

        self._handle_response(response_object, print_response=print_response)
    
    def _handle_tool_calls(self, tool_calls: dict) -> bool:
        """
        Basic method of handling tool calls taken from example here: https://platform.openai.com/docs/guides/function-calling
        """
        run_follow_up = False
        available_functions = {
            "search_logos_library": search_logos_library,
        }
        for tool_call in tool_calls:
            function_name  = tool_call.function.name
            function_to_call  = available_functions.get(function_name)
            if function_to_call:
                run_follow_up = True
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        return run_follow_up
    
    def _handle_response(self, response_obj: ChatCompletion, print_response: bool = True) -> None:
        """
        Truncated example. Here we might want to auto-save the response or the messages as a chat log.
        """
        res_dict = response_obj.model_dump()
        # If n > 1, there will be other response content, we ignore that for this example
        res_content = res_dict["choices"][0]["message"]["content"]
        if print_response:
            print(res_content)
        
        self.last_response_obj = response_obj

    def set_sys_msg(self, msg) -> None:
        """
        The example `set_sys_msg` fn makes two assumptsion that should be kept in mind:
            1. If `messages` already has content, that the pre-existing 
            system message is the first item in the list.
            2. You want the system message to be the first message in 
            the list. (And this may not always be the case!)

        The final `messages` list will contain the new system message as the first 
        item in the list, along with whatever other contents followed came after the 
        first message in the old `messages` list.

        We mutate the `messages` list, instead of returning a new list obj.
        """
        sys_msg = {
            "role": "system",
            "content": msg,
        }
        if len(self.messages) == 0:
            self.messages.append(sys_msg)
            return
        prev_msgs = self.messages[1:]
        new_msgs = [sys_msg] + prev_msgs
        self.messages.clear()
        self.messages.extend(new_msgs)

    def add_user_msg(self, msg) -> None:
        user_msg = {
            "role": "user",
            "content": msg,
        }
        self.messages.append(user_msg)

    def display_messages(self) -> None:
        """
        Since the purpose here is to show what messages are being sent to the OpenAI API, 
        we don't filter out stuff that we would want to filter out if this were being
        used to provide a chat interface to a user.

        Filtering out the less relevant information might look like this:
        if isinstance(msg, ChatCompletionMessage):
            if msg.content:
                print(f"{msg.role.upper()}: {msg.content}")
        elif msg["role"] == "user" or msg["role"] == "system":
            print(f"{msg['role'].upper()}: {msg['content']}")
        """
        for msg in self.messages:
            if isinstance(msg, ChatCompletionMessage):
                print(f"{msg.role.upper()}: {msg.content}")
            else:
                print(f"{msg['role'].upper()}: {msg['content']}")

    def clear_messages(self) -> None:
        self.messages.clear()