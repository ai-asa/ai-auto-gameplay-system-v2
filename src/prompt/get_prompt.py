import configparser
import os

class GetPrompt:
    def __init__(self,base_dir):
        config = configparser.ConfigParser()
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config.read(settings_path, encoding='utf-8')
        self.source_name = config.get('SYSTEM', 'source_name',fallback='Switch画面')

    def get_gameplay_prompt(self,game_title,play_target,play_log,advice,ss_info,last_operate):
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
        operate_info = f"""
AIが最後に実行した操作コマンドです：
<last_operate>
{last_operate}
</last_operate>
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
        if last_operate:
            log_info = log_info + operate_info
        if play_log:
            play_info = play_info + log_info
        if advice:
            prompt = instruct_info+play_info+advice_info+res_info
        else:
            prompt = instruct_info+play_info+res_info
        return prompt

    def ss_prompt(self,play_log,game_info):
        instruct_info = f"""あなたはゲームのプレイ画面を分析し、ゲームの進行状況や可能な操作など、得られる全ての情報をJSON形式で整理して出力するAIです。
"""
        scene_info = f"""プレイ中のゲームのシーンの情報は以下のとおりです：
<scene_information>
{game_info}
</scene_information>
"""
        log_info = f"""
これまでのゲームプレイのログは以下のとおりです：
<play_log>
{play_log}
</play_log>
"""
        res_info = f"""
分析の注意事項は以下のとおりです：
1. 現在のゲーム画面情報と最も近い、ゲームシーンの情報を見つけてください。それが現在のシーンとなります
2. ゲームプレイログがある場合は、現在のシーンを判断するための参考にしてください
3. 現在のシーンを基にプレイ画面を分析し、ゲームの進行状況、表示されている全ての選択可能な選択肢、操作コマンド等の情報をJSON形式で出力してください
"""
        if play_log:
            prompt = instruct_info+scene_info+log_info+res_info
        else:
            prompt = instruct_info+scene_info+res_info
        return prompt

    def scene_prompt(self,play_log,game_info,ss_info):
        instruct_info = f"""あなたは現在のシーンを分析し、ゲーム画面情報に修正・追加をおこなうAIです。
ゲーム画面情報、これまでのゲームプレイログ、ゲームのシーン情報をもとに分析し、推定される現在のゲームシーン、修正・追加をおこなったゲーム画面情報を出力します。
"""
        scene_info = f"""プレイ中のゲームのシーン情報は以下のとおりです：
<scene_information>
{game_info}
</scene_information>
"""
        log_info = f"""
これまでのゲームプレイのログは以下のとおりです：
<play_log>
{play_log}
</play_log>
"""
        dis_info = f"""
現在のゲーム画面情報は以下の通りです：
<display_information>
{ss_info}
</display_information>
"""
        res_info = f"""
分析の注意事項は以下のとおりです：
1. 現在のゲーム画面情報と最も近い、ゲームシーンの情報を見つけてください。それが現在のシーンとなります
2. ゲームプレイログがある場合は、現在のシーンを判断するための参考にしてください
3. 現在のゲーム画面情報は画像からAIが分析したものであり、ゲームシーンの情報を基に操作コマンドや注意事項の追加・修正が必要です

出力は以下の形式に従ってください：
<output_format>
<current_scnene>
[現在のシーン]
</current_scene>
<fixed_information>
[修正・追加したゲームの画面情報]
</fixed_information>
</output_format>

注意事項をよく確認し、与えられた全ての情報を加味して分析し、所定の形式で出力してください
"""
        if play_log:
            prompt = instruct_info+scene_info+log_info+dis_info+res_info
        else:
            prompt = instruct_info+scene_info+dis_info+res_info
        return prompt
    

