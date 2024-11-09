# %% 
import configparser
import google.generativeai as genai
import os
import json
import base64

class GeminiAdapter:

    def __init__(self,base_dir):
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config = configparser.ConfigParser()
        config.read(settings_path, encoding='utf-8')
        gemini_api_key = config.get('ENVIRONMENT', 'gemini_api_key',fallback='')
        self.gemini_selected_model = config.get('SYSTEM', 'gemini_selected_model',fallback='gemini-1.5-flash')
        self.call_attempt_limit = int(config.get('SYSTEM', 'call_limite', fallback=5))
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(self.gemini_selected_model)

    def b64encode(self,image_path):
        with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_image

    def fetch_gemini_multimodal(self, base64_image, prompt, temperature=0):
        contents = [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
        
        generation_config = {
            "temperature": temperature
        }
        
        for i in range(self.call_attempt_limit):
            try:
                response = self.model.generate_content(
                    contents=contents,
                    generation_config=generation_config
                )
                res_text = response.text
                return res_text
            except Exception as error:
                print(f"Gemini API呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None  # エラー時はNoneを返す
                continue

    def fetch_gemini_multimodal_json(self, base64_image, prompt,temperature=0):
        contents = [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
        
        for i in range(self.call_attempt_limit):
            try:
                response = self.model.generate_content(
                    contents=contents,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=temperature
                    ),
                )
                res_text = response.text
                res_json = json.loads(res_text)
                return res_json
            except Exception as error:
                print(f"Gemini API呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None  # エラー時はNoneを返す
                continue

    def gemini_chat(self, user_text):
        for i in range(self.call_attempt_limit):
            try:
                response = self.model.generate_content(user_text)
                return response.text
            except Exception as error:
                print(f"gemini呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None
                continue
    
    def gemini_streaming(self, user_text):
        for i in range(self.call_attempt_limit):
            try:
                response = self.model.generate_content(user_text, stream=True)
                for chunk in response:
                    if hasattr(chunk, 'parts'):
                        texts = [part.text for part in chunk.parts if hasattr(part, 'text')]
                        yield ''.join(texts)
                break
            except Exception as error:
                print(f"gemini呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None
                continue
    
if __name__ == "__main__":
    base_dir = "C://Users//pirok//ai-auto-gameplay-system"
    ga = GeminiAdapter(base_dir)
    prompt = """
あなたはゲームプレイAIです。
現在のゲーム画面の情報から操作を判断し、プレイ目標を達成するために必要なプレイの判断とその根拠、コントローラーの操作情報 
を出力します。

プレイ中のゲームのタイトルです：
ポケモンスタジアム2

現在のプレイ目標は以下のとおりです：
「とにかくバトルがしたい！」モードで1勝する。

これまでのゲームプレイのログは以下のとおりです：
<play_log>
{
  "timestamp": "2024-11-08T01:05:58.668000",
  "event": {
    "type": "プレイログ更新",
    "ai_reasoning": "現在の画面は「ゲームモード選択画面」で、目標である「とにかくバトルがしたい！」モードでのバトルに進む
ため、選択肢を「とにかくバトルがしたい！」に合わせて選択する必要があります。このオプションを選択することで、素早くバトル 
を行うモードに進むことができます。操作手順としては、十字キーで「左」を押して選択肢を「とにかくバトルがしたい！」に合わせ 
、「Aボタン」を押して確定します。",
    "operation_instruction": "move_LEFT, push_A",
    "button_commands": "push_HAT_LEFT,push_A"
  }
}
{
  "timestamp": "2024-11-09T07:44:43.802000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T07:45:31.947000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T08:06:12.586000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T08:12:41.198000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T08:19:34.607000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T08:32:28.034000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T08:37:30.404000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T08:39:28.186000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
{
  "timestamp": "2024-11-09T08:40:32.807000",
  "event": {
    "type": "目標更新",
    "play_target": "「とにかくバトルがしたい！」モードで1勝する。"
  }
}
</play_log>
プレイ中のゲームの各シーン情報は以下のとおりです：
<scene_information>
{
    "game_title": "ポケモンスタジアム2",
    "general_controls": {
        "basic_navigation": {
            "proceed": "Aボタン",
            "back": "Bボタン",
            "move_selection": "十字キー",
            "command_select": "Cキー",
            "special_functions": [
                "Rボタン",
                "Lボタン"
            ]
        }
    },
    "scenes": [
        {
            "id": 1,
            "name": "オープニングムービー",
            "description": "ゲーム開始時のムービー。サイドンなどの複数のポケモンが順番に表示される",
            "next_scene": "タイトル画面",
            "controls": {
                "proceed": "Aボタン"
            }
        },
        {
            "id": 2,
            "name": "タイトル画面",
            "description": "「ポケモンスタジアム2」のロゴとPUSH START表示がある画面",
            "next_scene": "カートリッジチェック画面",
            "visual_elements": {
                "title": {
                    "position": "正面上",
                    "text": "ポケモンスタジアム2"
                },
                "start_prompt": {
                    "text": "PUSH START",
                    "state": "点滅"
                }
            },
            "controls": {
                "proceed": "Aボタン"
            }
        },
        {
            "id": 3,
            "name": "カートリッジチェック画面",
            "description": "64のセーブ用カートリッジ接続確認画面",
            "previous_scene": "タイトル画面",
            "next_scene": "ゲームモード選択画面",
            "visual_elements": {
                "title": {
                    "position": "左上",
                    "text": "カートリッジチェック"
                },
                "hardware_display": {
                    "position": "正面上",
                    "content": "任天堂64ハードウェアとコントローラ接続図"
                },
                "warning": {
                    "position": "下部",
                    "text": "GBカートリッジ、64GBパック、コントローラのぬきさしは、でんげんをきってからおこなってください
"
                },
                "prompt": {
                    "position": "右上",
                    "text": "OK?"
                }
            },
            "controls": {
                "proceed": "Aボタン",
                "back": "Bボタン"
            },
            "notes": "Switchエミュレータでプレイ時は関係のない画面"
        },
        {
            "id": 4,
            "name": "ゲームモード選択画面",
            "description": "メインのゲームモード選択画面",
            "previous_scene": "カートリッジチェック画面",
            "visual_elements": {
                "title": {
                    "position": "上部",
                    "text": "えらんでください"
                }
            },
            "selectable_options": {
                "center": {
                    "name": "ポケモンスタジアム",
                    "description": "スタジアムは　ここにあります。バトルかいじょう、ポケモンけんきゅうじょ、ミニゲームな 
ど　いろいろ　あります。",
                    "next_scene": "ストーリーモード画面"
                },
                "right": {
                    "name": "イベントバトル",
                    "description": "コントローラ１と２に　セットされた　カートリッジの　手持ちのポケモンどうしのバトルで 
す",
                    "notes": "カートリッジを接続できないため選択不可"
                },
                "left": {
                    "name": "とにかくバトルがしたい！",
                    "description": "とにかく1びょうでも　はやくバトルをやってみたい　というひとは　ここで　あそんでみて　
ください",
                    "next_scene": "バトルモード選択画面"
                },
                "bottom": {
                    "name": "オプション"
                }
            },
            "controls": {
                "move": "十字キー",
                "select": "Aボタン",
                "back": "Bボタン"
            }
        },
        {
            "id": 5,
            "name": "バトルモード選択画面",
            "description": "「とにかくバトルがしたい！」モードでのバトル形式選択画面",
            "previous_scene": "ゲームモード選択画面",
            "next_scene": "アイキャッチ",
            "visual_elements": {
                "base_layout": {
                    "description": "ゲームモード選択画面と同じ背景",
                    "elements": {
                        "left": {
                            "name": "とにかくバトルがしたい！",
                            "state": "アクティブ（選択中）",
                            "description": "とにかく1びょうでも　はやくバトルをやってみたい　というひとは　ここで　あそん
でみて　ください"
                        }
                    }
                },
                "battle_mode_overlay": {
                    "description": "「とにかくバトルがしたい！」の選択肢の上に重なって表示される選択画面",
                    "position": "とにかくバトルがしたい！の選択肢の上",
                    "options": [
                        {
                            "name": "ひとりでバトル",
                            "description": "コンピューターとの対戦",
                            "initial_state": "選択状態"
                        },
                        {
                            "name": "ふたりでバトル",
                            "description": "1Pと2Pでの対戦",
                            "notes": "2Pがいない場合はプレイ不可"
                        }
                    ]
                }
            },
            "controls": {
                "move": "十字キー上下（バトルモードの選択を切り替え）",
                "select": "Aボタン（選択したバトルモードで開始）",
                "back": "Bボタン（ゲームモード選択画面に戻る）"
            }
        },
        {
            "id": 6,
            "name": "アイキャッチ",
            "description": "バトル開始前の「VS」表示画面",
            "previous_scene": "バトルモード選択画面",
            "next_scene": "ポケモン選択画面",
            "visual_elements": {
                "vs_text": {
                    "position": "画面上",
                    "size": "大きく"
                },
                "pokemon_display": "それぞれのトレーナーのポケモン表示"
            },
            "notes": "操作不要の演出画面"
        },
        {
            "id": 7,
            "name": "ポケモン選択画面",
            "description": "バトルに使用するポケモンを選択する画面",
            "previous_scene": "アイキャッチ",
            "next_scene": "バトル画面",
            "visual_elements": {
                "player_info": {
                    "1p_name": "ブルー",
                    "2p_name": "レッド",
                    "pokemon_display": "2行3列で6体ずつ",
                    "selection_slots": "黒い穴3つ（選択後モンスターボールに変化）"
                }
            },
            "controls": {
                "pokemon_selection": {
                    "row1_col1": "Bボタン",
                    "row1_col2": "C左キー",
                    "row1_col3": "C上キー",
                    "row2_col1": "Aボタン",
                    "row2_col2": "C下キー",
                    "row2_col3": "C右キー"
                },
                "reset": "Lボタン",
                "confirm": {
                    "move": "十字キー",
                    "select": "Aボタン"
                }
            }
        },
        {
            "id": 8,
            "name": "バトル画面",
            "description": "ポケモンの技や召喚のアニメーション表示画面",
            "previous_scene": [
                "ポケモン選択画面",
                "バトル選択画面"
            ],
            "next_scene": "バトル選択画面",
            "visual_elements": {
                "animations": [
                    "ポケモン召喚",
                    "技使用"
                ],
                "text_info": [
                    "ポケモン名",
                    "使用技",
                    "効果"
                ]
            },
            "notes": "操作不要のアニメーション画面"
        },
        {
            "id": 9,
            "name": "バトル選択画面",
            "description": "バトル中の行動選択画面",
            "previous_scene": "バトル画面",
            "next_scene": "バトル選択確認画面",
            "visual_elements": {
                "status_display": {
                    "player": {
                        "position": "左上",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    },
                    "opponent": {
                        "position": "右下",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    }
                }
            },
            "selectable_options": {
                "fight": {
                    "name": "たたかう",
                    "control": "Aボタン",
                    "next_scene": {
                        "immediate": "バトル選択確認画面",
                        "type": "技選択モード"
                    }
                },
                "pokemon": {
                    "name": "ポケモン",
                    "control": "Bボタン",
                    "next_scene": {
                        "immediate": "バトル選択確認画面",
                        "type": "ポケモン交代モード"
                    }
                },
                "run": {
                    "name": "にげる",
                    "control": "STARTボタン",
                    "next_scene": "降参選択画面"
                }
            }
        },
        {
            "id": 10,
            "name": "バトル選択確認画面",
            "description": "技選択またはポケモン交代の前の中継確認画面",
            "previous_scene": "バトル選択画面",
            "next_scene": [
                "技選択画面",
                "ポケモン交代画面"
            ],
            "visual_elements": {
                "status_display": {
                    "player": {
                        "position": "左上",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    },
                    "opponent": {
                        "position": "右下",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    }
                },
                "options": {
                    "back": {
                        "text": "もどる",
                        "control": "Lボタン",
                        "action": "バトル選択画面に戻る"
                    },
                    "confirm": {
                        "text": "かくにん",
                        "control": "Rボタンホールド",
                        "action": "選択モードに応じた画面を表示"
                    }
                }
            },
            "mode_transition": {
                "fight_mode": {
                    "condition": "「たたかう」から遷移",
                    "next_scene": "技選択画面",
                    "trigger": "Rボタンホールド"
                },
                "pokemon_mode": {
                    "condition": "「ポケモン」から遷移",
                    "next_scene": "ポケモン交代画面",
                    "trigger": "Rボタンホールド"
                }
            }
        },
        {
            "id": 11,
            "name": "技選択画面",
            "description": "ポケモンの技を選択する画面（Rボタンホールド中のみ表示）",
            "previous_scene": "バトル選択確認画面",
            "next_scene": "バトル画面",
            "visual_elements": {
                "status_display": {
                    "player": {
                        "position": "左上",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    },
                    "opponent": {
                        "position": "右下",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    }
                },
                "move_layout": {
                    "trigger": "Rボタンホールド",
                    "display": "4つの技が上下左右の位置に表示",
                    "info_per_move": [
                        "技名",
                        "タイプ",
                        "PP現在値/最大値"
                    ]
                }
            },
            "button_actions": {
                "Cキー上": "上位置の技を即座に選択・使用してバトル画面へ",
                "Cキー左": "左位置の技を即座に選択・使用してバトル画面へ",
                "Cキー右": "右位置の技を即座に選択・使用してバトル画面へ",
                "Cキー下": "下位置の技を即座に選択・使用してバトル画面へ"
            }
        },
        {
            "id": 12,
            "name": "ポケモン交代画面",
            "description": "バトルに出すポケモンを交代する画面（Rボタンホールド中のみ表示）",
            "previous_scene": "バトル選択確認画面",
            "next_scene": [
                "バトル画面",
                "警告表示"
            ],
            "visual_elements": {
                "status_display": {
                    "player": {
                        "position": "左上",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    },
                    "opponent": {
                        "position": "右下",
                        "info": [
                            "ポケモン名",
                            "状態",
                            "レベル",
                            "HP",
                            "HP現在値/最大値"
                        ]
                    }
                },
                "pokemon_layout": {
                    "trigger": "Rボタンホールド",
                    "display": "3匹のポケモンが縦に配置",
                    "info_per_pokemon": [
                        "レベル",
                        "名前",
                        "状態",
                        "HP現在値/最大値"
                    ]
                }
            },
            "button_actions": {
                "Cキー上": "上位置のポケモンを即座に選択して結果判定へ",
                "Cキー右": "中央位置のポケモンを即座に選択して結果判定へ",
                "Cキー下": "下位置のポケモンを即座に選択して結果判定へ"
            },
            "selection_results": {
                "valid_case": "選択可能なポケモンの場合、即座にバトル画面へ",
                "invalid_cases": [
                    {
                        "case": "既に場に出ているポケモンの場合",
                        "warning": "「もうポケモンは出ています」と表示",
                        "resolution": "Aボタンを押して警告を消すまで他の操作不可"
                    },
                    {
                        "case": "ひんし状態のポケモンの場合",
                        "warning": "「たたかう　きりょくが　ない」と表示",
                        "resolution": "Aボタンを押して警告を消すまで他の操作不可"
                    }
                ]
            }
        }
    ]
}
</scene_information>
ボタン操作の種類は以下のとおりです：
1. push_: ボタンを1回押して離す動作
2. hold_: ボタンを押し続ける動作

各ボタンの実行コマンドは以下のとおりです：
# メインボタン
A: "push_A", "hold_A"
B: "push_B", "hold_B"
X: "push_X", "hold_X"
Y: "push_Y", "hold_Y"

# トリガー/ショルダーボタン
L: "push_L", "hold_L"
R: "push_R", "hold_R"
ZL: "push_ZL", "hold_ZL"
ZR: "push_ZR", "hold_ZR"

# システムボタン
マイナス: "push_MINUS", "hold_MINUS"
プラス: "push_PLUS", "hold_PLUS"
HOME: "push_HOME", "hold_HOME"
キャプチャー: "push_CAPTURE", "hold_CAPTURE"

# スティッククリック
Lスティッククリック: "push_LCLICK", "hold_LCLICK"
Rスティッククリック: "push_RCLICK", "hold_RCLICK"

# 十字キー
十字キー上: "push_HAT_UP", "hold_HAT_UP"
十字キー下: "push_HAT_DOWN", "hold_HAT_DOWN"
十字キー左: "push_HAT_LEFT", "hold_HAT_LEFT"
十字キー右: "push_HAT_RIGHT", "hold_HAT_RIGHT"

# Cスティック
Cスティック上: "push_C_UP", "hold_C_UP"
Cスティック下: "push_C_DOWN", "hold_C_DOWN"
Cスティック左: "push_C_LEFT", "hold_C_LEFT"
Cスティック右: "push_C_RIGHT", "hold_C_RIGHT"

プレイ判断は以下の手順で進めてください：
1. 現在のゲーム画面情報と最も近い、ゲームシーンの情報を見つけてください。それが現在のシーンとなります
2. ゲームプレイログがある場合は、現在のシーンを判断するための参考にしてください
3. 現在のシーンを基にプレイ画面を分析し、ゲームの進行状況、表示されている全ての選択可能な選択肢、その位置関係、それらを実
行可能なコマンドを把握してください
4. プレイ目標を確認し、それを達成するために必要な判断と、それを実行するためのコマンド操作を考えてください

以下の注意事項に従ってください：
1. 前回の操作によりゲームが進行していない場合、判断やコントローラー操作を誤っている可能性があります。別の判断、操作を検討
してください
2. 状況が好転しない場合は、あなたのこれまでの判断が誤っている可能性が高いです。あなたが実行できるコントローラー操作を全て
試してください
3. あなたにゲームハード自体の操作など、コントローラー以外の操作を指示する権限はありません。必ずコントローラー操作で状況を
解決してください

以下のJSONスキーマに従って出力してください:
"current_game_scene"：現在のゲームシーン -> string
"gameplay_decision_explanation"：ゲームプレイの判断の説明 -> string
"selection_item"：選択する項目 -> string
"operation_method"：目的の項目を選択するのに必要な操作手順 -> string
"operation_commands"：実行するコマンドの操作順のリスト -> string in list
例：["push_PLUS","push_A","hold_B"]

schema:
{
  "current_game_scene": string,
  "image_situation": string,
  "gameplay_decision_explanation": string,
  "operation_methods": [
    {
      "selection_item": string,
      "operation_method": string
    }
  ],
  "operation_commands": [string]
}
"""
    base64_data = ga.b64encode("c://Users//pirok//ai-auto-gameplay-system//datas//buttle.png")
    res = ga.fetch_gemini_multimodal_json(base64_data,prompt)
    print(res)
# %%
