import configparser
import os

class GetPrompt:
    def __init__(self,base_dir):
        config = configparser.ConfigParser()
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config.read(settings_path, encoding='utf-8')
        self.source_name = config.get('SYSTEM', 'source_name',fallback='Switch画面')

    def get_gameplay_prompt(self,game_title,play_target,play_log,advice,ss_info):
        instruct_info = f"""あなたはゲームプレイAIです。
現在のゲーム画面の情報から操作を判断し、プレイ目標を達成するために必要なプレイの判断とその根拠、コントローラーの操作情報を出力します。
"""
        play_info = f"""
プレイ中またはプレイするゲームのタイトルです：
{game_title}

現在のプレイ目標は以下のとおりです：
{play_target}
"""
        log_info = f"""
AIのこれまでのゲームプレイの情報です：
<play_log>
{play_log}
</play_log>
"""
        advice_info = f"""
ゲームプレイについて以下のような助言を受けています：
<advice>
{advice}
</advice>
"""
        res_info = f"""
現在のゲーム画面から得られる情報は以下の通りです：
<information_game>
{ss_info}
</information_game>

プレイ判断の注意事項は以下の通りです：
1. 前回の操作によりゲームが進行していない場合、判断やコントローラー操作を誤っている可能性があります。別の判断、操作を検討してください
2. ゲームによって基本的な操作方法が異なる場合があります。操作方法を試しに確認することも検討してください
3. 状況が好転しない場合は、あなたのこれまでの判断が誤っている可能性が高いです。あなたが実行できるコントローラー操作を全て試してください。
4. あなたにゲームハード自体の操作など、コントローラー以外の操作を指示する権限はありません。必ずコントローラー操作で状況を解決してください。

出力は以下の形式に従ってください：
<output_format>
<description_reason>
[判断の内容の説明]
</description_reason>
<operation_controller>
[コントローラーの操作の指示]
</operation_controller>
</output_format>

注意事項をよく確認し、これまでのゲームプレイの情報、助言、画面の情報などを加味して判断を行い、所定の形式で出力してください。
"""
        if play_log:
            play_info = play_info + log_info
        if advice:
            prompt = instruct_info+play_info+advice_info+res_info
        else:
            prompt = instruct_info+play_info+res_info
        return prompt
