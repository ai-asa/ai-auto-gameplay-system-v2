# %%
import configparser
from openai import OpenAI
import os
import base64
import re
from typing import List
import json

class OpenaiAdapter:

    def __init__(self,base_dir):
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config = configparser.ConfigParser()
        config.read(settings_path, encoding='utf-8')
        self.openai_api_key = config.get('ENVIRONMENT', 'openai_api_key', fallback="")
        self.call_attempt_limit = int(config.get('SYSTEM', 'call_limite', fallback=5))
        self.openai_selected_model = config.get('SYSTEM', 'openai_selected_model', fallback="gpt-4o")
        self.client = OpenAI(
            api_key = self.openai_api_key
        )
        self.set_tools()
    
    def set_tools(self):
        enum = [
            "push_A", "push_B", "push_X", "push_Y",
            "push_L", "push_R", "push_ZL", "push_ZR",
            "push_MINUS", "push_PLUS", "push_LCLICK", "push_RCLICK",
            "push_HOME", "push_CAPTURE",
            "push_HAT_UP", "push_HAT_DOWN", "push_HAT_LEFT", "push_HAT_RIGHT",
            "push_C_UP", "push_C_DOWN", "push_C_LEFT", "push_C_RIGHT",
            "push_UP_RIGHT", "push_UP_LEFT", "push_DOWN_RIGHT", "push_DOWN_LEFT",
            "hold_A", "hold_B", "hold_X", "hold_Y",
            "hold_L", "hold_R", "hold_ZL", "hold_ZR",
            "hold_MINUS", "hold_PLUS", "hold_LCLICK", "hold_RCLICK",
            "hold_HOME", "hold_CAPTURE",
            "hold_HAT_UP", "hold_HAT_DOWN", "hold_HAT_LEFT", "hold_HAT_RIGHT",
            "hold_C_UP", "hold_C_DOWN", "hold_C_LEFT", "hold_C_RIGHT",
            "hold_UP_RIGHT", "hold_UP_LEFT", "hold_DOWN_RIGHT", "hold_DOWN_LEFT"
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "select_buttons",
                    "description": """
ゲームプレイの判断とコントローラー操作の指示から、適切なボタン操作を選択します。

ボタン操作の種類：
1. push_: ボタンを1回押して離す動作
2. hold_: ボタンを押し続ける動作

複数のボタンを順番に押す必要がある場合：
- 各ボタンに対して個別のコマンドを配列に含めてください
- 例：Aボタンのみを押す場合 → ["push_A"]
- 例：AボタンとBボタンを順番に押す場合 → ["push_X", "push_Y"]

ボタンの対応関係：
- X, Y, A, B: それぞれ "push_X", "push_Y", "push_A", "push_B"
- 十字キー: Up="push_HAT_UP", Down="push_HAT_DOWN", Left="push_HAT_LEFT", Right="push_HAT_RIGHT"
- Cスティック: C上="push_C_UP", C下="push_C_DOWN", C左="push_C_LEFT", C右="push_C_RIGHT"

注意事項：
- 複数のボタンの指示がある場合は、必ず複数のボタンコマンドを返してください
- テキスト内でボタンが列挙されている場合（「と」「、」で区切られている場合）は、それらを順番に押すとして扱います
""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "buttons": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": enum
                                },
                                "description": "選択されたボタン操作のリスト"
                            }
                        },
                        "required": ["buttons"]
                    }
                }
            }
        ]

    def select_game_buttons(self,ds_reason_text,op_cont_text) -> List[str]:
        tools = self.tools
        prompt = f"""以下のゲームプレイの判断とコントローラー操作の指示から、必要なボタン操作をすべて選択してください。
複数のボタンが指示されている場合（「と」や「、」で区切られている場合）は、それらを順番に押す必要があります。
各ボタンに対して個別のコマンドを返してください。

ゲームプレイの判断：
<decision_gameplay>
{ds_reason_text}
</decision_gameplay>

コントローラー操作の指示：
<instruct_operation>
{op_cont_text}
</instruct_operation>"""
        messages = [
            {"role": "system", "content": prompt}
        ]

        for _ in range(self.call_attempt_limit):
            try:
                response = self.client.chat.completions.create(
                    model=self.openai_selected_model,
                    messages=messages,
                    tools=tools
                )

                if response.choices[0].message.tool_calls:
                    tool_call = response.choices[0].message.tool_calls[0]
                    if tool_call.function.name == "select_buttons":
                        buttons = json.loads(tool_call.function.arguments)["buttons"]
                        return buttons
                else:
                    return []

            except Exception as e:
                print(f"Error occurred: {e}")
                continue

        return []  # Return an empty list if all attempts fail

    def fetch_openai(self, prompt, temperature=1):
        system_prompt = [{"role": "system", "content": prompt}]
        for i in range(self.call_attempt_limit):
            try:
                response = self.client.chat.completions.create(
                    messages=system_prompt,
                    model=self.openai_selected_model,
                    temperature=temperature
                )
                text = response.choices[0].message.content
                return text
            except Exception as error:
                print(f"GPT呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None  # エラー時はNoneを返す
                continue
    
    def fetch_openai_streaming(self, prompt, temperature=1):
        system_prompt = [{"role": "system", "content": prompt}]
        for i in range(self.call_attempt_limit):
            try:
                stream = self.client.chat.completions.create(
                    model=self.openai_selected_model,
                    messages=system_prompt,
                    temperature=temperature,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                break
            except Exception as error:
                print(f"GPT呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None  # エラー時はNoneを返す
                continue
    
    def b64encode(self,image_path):
        with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_image

    def fetch_openai_multimodal(self,base64_image,prompt,instruct_text="画像からわかることはなんですか？",temperature=0):
        system_prompt = {"role": "system", "content": prompt}
        instruct_text = {"type": "text", "text": instruct_text}
        image_url = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        for i in range(self.call_attempt_limit):
            try:
                response = self.client.chat.completions.create(
                    model=self.openai_selected_model,
                    messages=[
                        system_prompt,
                        {"role": "user", "content": [
                            instruct_text,
                            image_url
                        ]}
                    ],
                    temperature=temperature,
                )
                res_text = response.choices[0].message.content
                return res_text
            except Exception as error:
                print(f"GPT呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None  # エラー時はNoneを返す
                continue

    def fetch_openai_multimodal_json(self,base64_image,prompt,instruct_text="画像からわかることはなんですか？",temperature=0):
        system_prompt = {"role": "system", "content": prompt}
        instruct_text = {"type": "text", "text": instruct_text}
        image_url = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        for i in range(self.call_attempt_limit):
            try:
                response = self.client.chat.completions.create(
                    model=self.openai_selected_model,
                    messages=[
                        system_prompt,
                        {"role": "user", "content": [
                            instruct_text,
                            image_url
                        ]}
                    ],
                    response_format={"type": "json_object"},
                    temperature=temperature,
                )
                res_text = response.choices[0].message.content
                return res_text
            except Exception as error:
                print(f"GPT呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None  # エラー時はNoneを返す
                continue

    def parse_response(self,text):
        description_reason = re.search(r'<description_reason>(.*?)</description_reason>', text, re.DOTALL)
        operation_controller = re.search(r'<operation_controller>(.*?)</operation_controller>', text, re.DOTALL)
        ds_reason_text = description_reason.group(1).strip() if description_reason else None
        op_cont_text = operation_controller.group(1).strip() if operation_controller else None
        # コントローラ操作情報の構造化
        select_buttons = self.select_game_buttons(ds_reason_text,op_cont_text)
        return ds_reason_text,op_cont_text,select_buttons

if __name__ == "__main__":
    image_path = "C://Users//pirok//ai-auto-gameplay-system//datas//buttle.png"
    base_dir = "C://Users//pirok//ai-auto-gameplay-system"
    oa = OpenaiAdapter(base_dir)
    # # prompt = "ゲームのプレイ画像を渡します。画面の情報を分析してください。"
    # # text = "画像からわかる全ての情報を教えて下さい。"
    # prompt = "ゲームのプレイ画像を渡します。画面の情報を分析し、その結果をJSON形式で出力してください。"
    # text = "画像からわかる全ての情報をJSON形式で教えて下さい。"
    # start_time = time.time()
    # b64_image = oa.b64encode(image_path)
    # result = oa.fetch_openai_multimodal(b64_image, prompt, text)
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(result)
    # print(f"実行時間: {execution_time} 秒")
    # prompt = "ジャンプと攻撃を同時にしたいです。"
    # print(oa.select_buttons(prompt))
    ds_reason_text = "相手のポケモンはフシギソウでこちらはヒトカゲがいます。タイプ相性がいいので、このまま「たたかう」を選択しましょう。たたかうはcボタン上とYボタンとXボタンを押します。"
    op_cont_text = "c上ボタンとYボタンとXボタンを押す"
    response = oa.select_game_buttons(ds_reason_text,op_cont_text)
    print(",".join(response))
    

# %%
