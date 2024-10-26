import configparser
import os
import time

class GamePlaySystem:
    def __init__(self,base_dir,game_title,save_name,play_target):
        from src.chat.openai_adapter import OpenaiAdapter
        from src.prompt.get_prompt import GetPrompt
        from src.obs.obs_websocket_adapter import OBSAdapter
        from src.controller.switch_controller_adapter import SwitchControllerAdapter
        from src.db.mongo_adapter import MongoAdapter
        from src.webhook.webhook_adapter import WebhookAdapter
        self.oba = OBSAdapter(base_dir)
        self.gp = GetPrompt(base_dir)
        self.oa = OpenaiAdapter(base_dir)
        self.sc = SwitchControllerAdapter(base_dir)
        self.db = MongoAdapter(base_dir,game_title,save_name,play_target)
        self.wa = WebhookAdapter(base_dir)
        self.load_settings(base_dir)
        self.set_var()
        self.game_title = game_title
        self.play_target = play_target

    def load_settings(self,base_dir):
        config = configparser.ConfigParser()
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config.read(settings_path, encoding='utf-8')
        self.source_name = config.get('SYSTEM', 'source_name',fallback='Switch画面')
        self.wait_time = int(config.get('SYSTEM', 'wait_time',fallback=0))
        self.log_limit = int(config.get('SYSTEM', 'log_limit',fallback=10))

    def set_var(self):
        self.play_log_list = []
        self.play_log_text = self.db.fetch_logs()
        if not self.play_log_text:
            self.play_log_text = ""

    # 指示・アドバイスの取得
    def get_advice(self, ad_queue):
        advice = None
        if not ad_queue.empty():
            if self.wait_time == 0:
                advice = ad_queue.get_nowait()
            else:
                advice = ad_queue.get(timeout=self.wait_time)
        return advice

    # ScreenShot画像からシーン情報を取得する
    def fetch_ss_text(self):
        b64_image = self.oba.get_b64_screenshot(self.source_name)
        system_prompt = "ゲームのプレイ画像を渡します。画面の情報を分析し、その結果を出力してください。"
        instruct_text = "画像の全ての要素を詳細に説明し、選択可能と推定される要素、表示されているボタンの情報について出力してください。"
        response = self.oa.fetch_openai_multimodal(b64_image,system_prompt,instruct_text)
        return response
    
    # 操作判断用プロンプトの作成
    def assemble_prompt(self,ss_response,advice):
        prompt = self.gp.get_gameplay_prompt(self.game_title,self.play_target,self.play_log_text,advice,ss_response)
        return prompt
    
    # コントローラー操作判断の取得
    def get_operate(self,prompt):
        response = self.oa.fetch_openai(prompt)
        print("ai response:\n",response)
        # 結果のパース&操作コマンドの判断
        rs,op,bu = self.oa.parse_response(response)
        # プレイログ
        self._logging_gameplay(rs,op,bu)
        return bu
    
    # コントローラー操作の実行
    def exec_operate(self,button_data):
        self.sc.excute_button(button_data)

    # イベントのwebhook送信
    def _send_webhook(self):
        self.wa.post_http_event()

    # ゲームプレイのログ情報更新
    def _logging_gameplay(self,rs,op,bu):
        # logのDB保存
        log_text = self.db.update_log(rs,op,bu)
        # イベント送信
        self._send_webhook()
        # logの更新
        self.play_log_list.append(log_text)
        self.play_log_list = self.play_log_list[-self.log_limit:]
        if len(self.play_log_list) > 1:
            self.play_log_text = "¥n".join(self.play_log_list)

    def loop_gameplay(self,exit_event,ad_queue):
        while not exit_event.is_set():
            # try:
            # アドバイスを取得
            advice = self.get_advice(ad_queue)
            print("advice: ",advice)
            # SSとシーン情報の取得
            ss_response = self.fetch_ss_text()
            print("scene:\n",ss_response)
            # プロンプトの作成
            prompt = self.assemble_prompt(ss_response,advice)
            # 操作判断の取得
            button_data = self.get_operate(prompt)
            print("select button: ",button_data)
            # 操作の反映
            self.exec_operate(button_data)
            # except Exception as e:
            #     print("loop_gameplay実行中に例外が発生しました: %s", e)
            time.sleep(5)

    def agent_gameplay(self):
        pass