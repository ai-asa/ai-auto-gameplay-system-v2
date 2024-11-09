#%%
from src.chat.gemini_adapter import GeminiAdapter
from src.obs.obs_websocket_adapter import OBSAdapter
import base64
import hashlib
base_dir = "C://Users//pirok//ai-auto-gameplay-system"
oba = OBSAdapter(base_dir)
ga = GeminiAdapter(base_dir)

def test_obs_image(source_name: str):
    image_data = oba.get_b64_screenshot_non_headder(source_name)
    print(f"OBSで取得したimage_dataの最初の100文字:\n{image_data[:100]}")
    print(f"OBSで取得したimage_dataの長さ: {len(image_data)}")
    obs_hash = hashlib.md5(image_data.encode('utf-8')).hexdigest()
    print(f"OBS画像のハッシュ: {obs_hash}")
    try:
        screenshot_data = base64.b64decode(image_data, validate=True)
        with open('test_obs_image.png', 'wb') as f:
            f.write(screenshot_data)
        print("画像を正常にデコードして保存しました。")
    except base64.binascii.Error as e:
        print(f"デコードエラー: {e}")

if __name__ == "__main__":
    source_name = "Switch画面"
    # local_image_path = "C://Users//pirok//ai-auto-gameplay-system//datas//buttle.png"
    # image_data = ga.b64encode(local_image_path)
    # # ローカルPNGのハッシュ
    # with open(local_image_path, "rb") as f:
    #     local_hash = hashlib.md5(f.read()).hexdigest()
    # print(f"ローカルPNGのハッシュ: {local_hash}")
    # print(f"ローカル画像をエンコードしたimage_dataの最初の100文字:\n{image_data[:100]}")
    # print(f"ローカル画像をエンコードしたimage_dataの長さ: {len(image_data)}")
    # test_obs_image(source_name)

    b64_image = oba.get_b64_screenshot_non_headder(source_name)
    prompt = "画像からわかることをJSONスキームで出力してください"
    res = ga.fetch_gemini_multimodal_json(b64_image,prompt)
    print(res)
# %%
