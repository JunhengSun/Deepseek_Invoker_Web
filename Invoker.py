import os
from sys import float_repr_style
import openai
import copy
from typing import Optional

class Invoker:

    model = "deepseek-chat"
    base_url = "https://api.deepseek.com"

    def __init__(self, api_key: Optional[str] = None, role: Optional[str] = None):
        # get API key
        self.api_key = api_key if api_key else os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("ERROR: API key not found")
        
        # create client
        self.client = openai.OpenAI(
            api_key = self.api_key,
            base_url = self.base_url
        )


        self.role = role
        self.consistency_messages = []
        if self.role:
            self.consistency_messages.append({"role": "system", "content": self.role})

    def test_api_key_validity(self) -> bool:
        '''
            Test the API key validity
        '''
        try:
            self.client.chat.completions.create(
                model = self.model,
                messages = [{"role": "user", "content": "Hello"}],
                max_tokens = 1
            )
            return True
        except openai.AuthenticationError:
            return False
        except Exception as e:
            raise RuntimeError(f"ERROR: Failed to test API key validity: {str(e)}")


    def get_current_role(self) -> str:
        '''
            Get the current role
        '''
        return self.role

    def resume_consistency_messages(self, consistency_messages: list[dict]) -> bool:
        '''
            Resume the given consistency messages
        '''
        self.consistency_messages = consistency_messages
        if len(self.consistency_messages > 0 and self.consistency_messages[0]["role"] == "system"):
            self.role = self.consistency_messages[0]["content"]
        else:
            self.role = None
        return True
    
    def get_current_consistency_messages(self) -> list[dict]:
        '''
            Get the current consistency messages - return a deep copy
        '''
        return copy.deepcopy(self.consistency_messages)

    def clear_history(self) -> bool:
        '''
            Clear the history of consistency messages
        '''
        self.consistency_messages = []
        if self.role:
            self.consistency_messages.append({"role": "system", "content": self.role})
        return True

    def reset_role(self, role: Optional[str] = None) -> bool:
        '''
            Reset the system role and clear the history
        '''
        self.role = role
        self.clear_history()
        return True

    def adjust_role(self, role_adjustment: str, strength: Optional[str] = "medium") -> bool:
        '''
            Adjust the system role during a conversation
        '''
        if strength == "weak":
            prompt = f"""
            please slightly adjust the output according to the following requirements: {role_adjustment}
            """
        elif strength == "medium":
            prompt = f"""
            Please adjust the output according to the following requirements: {role_adjustment}
            """
        elif strength == "strong":
            prompt = f"""
            Please strictly adjust the output according to the following requirements: {role_adjustment}
            """
        else:
            return False

        # add the prompt to the consistency messages
        prompt = "In the following conversation, " + prompt
        self.consistency_messages.append({"role": "user", "content": prompt})
        # simulate the assistant's response
        self.consistency_messages.append({"role": "assistant", "content": "I understand the requirements, and will adjust the output accordingly."})
        return True

    def consistent_invoke(self, prompt: str, temp: Optional[float] = 1.0, max: Optional[int] = 1000) -> str:
        '''
            Invoke the API with the consistency messages
        '''
        '''
            备注：
            1. messages传递的参数为一个列表，列表中每个元素为一个字典，字典中包含role和content两个键值对
            可以模仿AI的对话过程，添加到messages中，以获得更精确的回答（可参考adjust role实现）

            2. temperature参数用于控制生成内容的随机性，范围为0到2，值越大，生成内容越随机

            3. max_tokens参数用于控制生成内容的最大长度，达到限制自动停止，可能导致不完整
        '''
        # check if prompt is empty
        if not prompt.strip():
            return "ERROR: Empty prompt"

        # check if temp is between 0 and 2
        if temp < 0 or temp > 2:
            return "ERROR: Temperature must be between 0 and 2"

        # add the prompt to the consistency messages
        self.consistency_messages.append({"role": "user", "content": prompt})

        # invoke API
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = self.consistency_messages,
                temperature = temp,
                max_tokens = max
            )
            result = response.choices[0].message.content
            self.consistency_messages.append({"role": "assistant", "content": result})
            return result
        except Exception as e:
            self.consistency_messages.pop()
            return f"ERROR: {str(e)}"

    def message_invoke(self, messages: list[dict], temp: Optional[float] = 1.0, max: Optional[int] = 1000) -> str:
        '''
            Invoke the API with the given messages
        '''
        # check if messages is empty
        if not messages:
            return "ERROR: Empty messages"
        
        # check if temp is between 0 and 2
        if temp < 0 or temp > 2:
            return "ERROR: Temperature must be between 0 and 2"

        # invoke API
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature = temp,
                max_tokens = max
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR: {str(e)}"
        

    def invoke(self, prompt: str, temp: Optional[float] = 1.0, max: Optional[int] = 1000) -> str:
        '''
            Invoke the API independently
        '''
        # checl if prompt is empty
        if not prompt.strip():
            return "ERROR: Empty prompt"

        # check if temp is between 0 and 2
        if temp < 0 or temp > 2:
            return "ERROR: Temperature must be between 0 and 2"

        invoke_messages = []
        if self.role:
            invoke_messages.append({"role": "system", "content": self.role})
        invoke_messages.append({"role": "user", "content": prompt})

        # invoke API
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = invoke_messages,
                temperature = temp,
                max_tokens = max
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR: {str(e)}"



if __name__ == "__main__":
    # invoker = Invoker("YOUR_API_KEY", "你是一个乐于助人的助手，请根据用户的问题，给出详细的回答")
    # # invoker.consistent_invoke("你好，我叫小鹏")
    # # invoker.consistent_invoke("我叫什么名字？")
    # # print(invoker.get_current_consistency_messages())
    # # print("--------------------------------------------------")
    # # invoker.clear_history()
    # # print(invoker.invoke("你好，我叫小鹏"))
    # # print(invoker.invoke("我叫什么名字？"))

    # invoker.reset_role("你是一个温柔的老师，请根据用户的问题，给出简短的回答")
    # print(invoker.consistent_invoke("在一次考试中，你是老师，一位平时不错的学生考差了，你会怎么说"))
    # invoker.adjust_role("在考试问题上，你是严厉的老师，请给出更加严厉的批评", strength = "strong")
    # print(invoker.consistent_invoke("在一次考试中，你是老师，一位平时不错的学生考差了，你会怎么说"))
    pass
    
