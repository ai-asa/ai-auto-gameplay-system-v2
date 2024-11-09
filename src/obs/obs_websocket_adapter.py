# %%
import obsws_python as obs
import configparser
import os
import base64
import re

class OBSAdapter:
    
    def __init__(self, base_dir) -> None:
        config = configparser.ConfigParser()
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config.read(settings_path, encoding='utf-8')
        self.host = config.get('OBS', 'obs_ws_host', fallback="")
        self.port = config.get('OBS', 'obs_ws_port', fallback="")
        self.password = config.get('OBS', 'obs_ws_password', fallback="")
        # 設定されていない場合はエラー
        if not all([self.host, self.port, self.password]):
            raise Exception("OBSの設定がされていません")
        self.ws = obs.ReqClient(host=self.host, port=int(self.port), password=self.password)

    def save_source_screenshot(self, source_name: str, save_path: str):
        response = self.ws.get_source_screenshot(
            name=source_name,
            img_format='png',
            width=1920,
            height=1080,
            quality=100
        )
        # "data:image/png;base64," ヘッダーを削除
        image_data = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', response.image_data)
        # base64デコード処理
        try:
            screenshot_data = base64.b64decode(image_data, validate=True)
        except base64.binascii.Error as e:
            print(f"base64デコードエラー: {e}")
            return
        with open(save_path + '.png', 'wb') as file:
            file.write(screenshot_data)

    def get_b64_screenshot_non_headder(self, source_name: str):
        response = self.ws.get_source_screenshot(
            name=source_name,
            img_format='png',
            width=1920,
            height=1080,
            quality=100
        )
        # "data:image/png;base64," ヘッダーを削除
        image_data = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', response.image_data)
        return image_data
    
    def get_b64_screenshot(self, source_name: str):
        response = self.ws.get_source_screenshot(
            name=source_name,
            img_format='png',
            width=1920,
            height=1080,
            quality=100
        )
        image_data = response.image_data
        return image_data

if __name__ == "__main__":
    base_dir = "C://Users//pirok//ai-auto-gameplay-system"
    oba = OBSAdapter(base_dir)
    oba.save_source_screenshot('Switch画面','test')


# %%
