# %% 
import configparser
import google.generativeai as genai
import os

class GeminiAdapter:

    def __init__(self,base_dir):
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config = configparser.ConfigParser()
        config.read(settings_path, encoding='utf-8')
        gemini_api_key = config.get('Environment', 'gemini_api_key',fallback='')
        self.gemini_model = config.get('CONFIG', 'gemini_model',fallback='gemini-1.5-flash')
        gemini_selected_model = config.get('SYSTEM', 'gemini_selected_model',fallback='gemini-1.5-flash')
        self.call_attempt_limit = int(config.get('SYSTEM', 'call_limite', fallback=5))
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(gemini_selected_model)


    def gemini_chat(self, user_text):
        for i in range(self.call_attempt_limit):
            try:
                response = self.model.generate_content(user_text)
                return response.text
            except Exception as error:
                print(f"gemini呼び出し時にエラーが発生しました:{error}")
                if i == self.call_attempt_limit - 1:
                    return None  # エラー時はNoneを返す
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
                    return None  # エラー時はNoneを返す
                continue
    