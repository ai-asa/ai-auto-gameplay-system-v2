#%%
import os
import time
import serial
import configparser
from logger.logger_config import setup_logger
from typing import Union, Tuple

class SwitchControllerAdapter:
    
    def __init__(self, base_dir):
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config = configparser.ConfigParser()
        config.read(settings_path, encoding='utf-8')
        self.serial_port = config.get('SYSTEM', 'serial_port_com', fallback="")
        self.serial_baud_rate = int(config.get('SYSTEM', 'serial_baud_rate', fallback=115200))
        self.logger = setup_logger()
        self.ser = None
        self.set_button()
        self.set_command()
        self.connect()
    
    def set_button(self):
        # 通常のボタンコード
        self._SIMPLE_CODES = {
            'A': 0x01,
            'B': 0x00,
            'X': 0x03,
            'Y': 0x02,
            'L': 0x04,
            'R': 0x05,
            'ZL': 0x06,
            'ZR': 0x07,
            'MINUS': 0x08,
            'PLUS': 0x09,
            'LCLICK': 0x0A,
            'RCLICK': 0x0B,
            'HAT_UP': 0x0C,
            'HAT_DOWN': 0x0D,
            'HAT_LEFT': 0x0E,
            'HAT_RIGHT': 0x0F,
            'HOME': 0x10,
            'CAPTURE': 0x11
        }

        # 複合ボタンの定義（タプルで複数のボタンコードを指定）
        self._COMBO_CODES = {
            'C_UP': (0x07, 0x03),    # ZR + X
            'C_DOWN': (0x07, 0x00),  # ZR + B
            'C_LEFT': (0x07, 0x02),  # ZR + Y
            'C_RIGHT': (0x07, 0x01)  # ZR + A
        }

        # BUTTON_CODESを両方のマッピングを含む辞書として設定
        self.BUTTON_CODES = {**self._SIMPLE_CODES, **self._COMBO_CODES}

    def set_command(self):
        self._COMMAND = {
            'push_A': {'type': 'push', 'button': 'A'},
            'push_B': {'type': 'push', 'button': 'B'},
            'push_X': {'type': 'push', 'button': 'X'},
            'push_Y': {'type': 'push', 'button': 'Y'},
            'push_L': {'type': 'push', 'button': 'L'},
            'push_R': {'type': 'push', 'button': 'R'},
            'push_ZL': {'type': 'push', 'button': 'ZL'},
            'push_ZR': {'type': 'push', 'button': 'ZR'},
            'hold_A': {'type': 'hold', 'button': 'A'},
            'hold_B': {'type': 'hold', 'button': 'B'},
            'hold_X': {'type': 'hold', 'button': 'X'},
            'hold_Y': {'type': 'hold', 'button': 'Y'},
            'hold_L': {'type': 'hold', 'button': 'L'},
            'hold_R': {'type': 'hold', 'button': 'R'},
            'hold_ZL': {'type': 'hold', 'button': 'ZL'},
            'hold_ZR': {'type': 'hold', 'button': 'ZR'},
            'push_MINUS': {'type': 'push', 'button': 'MINUS'},
            'push_PLUS': {'type': 'push', 'button': 'PLUS'},
            'push_LCLICK': {'type': 'push', 'button': 'LCLICK'},
            'push_RCLICK': {'type': 'push', 'button': 'RCLICK'},
            'push_HOME': {'type': 'push', 'button': 'HOME'},
            'push_CAPTURE': {'type': 'push', 'button': 'CAPTURE'},
            'hold_MINUS': {'type': 'hold', 'button': 'MINUS'},
            'hold_PLUS': {'type': 'hold', 'button': 'PLUS'},
            'hold_LCLICK': {'type': 'hold', 'button': 'LCLICK'},
            'hold_RCLICK': {'type': 'hold', 'button': 'RCLICK'},
            'hold_HOME': {'type': 'hold', 'button': 'HOME'},
            'hold_CAPTURE': {'type': 'hold', 'button': 'CAPTURE'},
            'push_HAT_UP': {'type': 'push', 'button': 'HAT_UP'},
            'push_HAT_DOWN': {'type': 'push', 'button': 'HAT_DOWN'},
            'push_HAT_LEFT': {'type': 'push', 'button': 'HAT_LEFT'},
            'push_HAT_RIGHT': {'type': 'push', 'button': 'HAT_RIGHT'},
            'hold_HAT_UP': {'type': 'hold', 'button': 'HAT_UP'},
            'hold_HAT_DOWN': {'type': 'hold', 'button': 'HAT_DOWN'},
            'hold_HAT_LEFT': {'type': 'hold', 'button': 'HAT_LEFT'},
            'hold_HAT_RIGHT': {'type': 'hold', 'button': 'HAT_RIGHT'},
            'push_C_UP': {'type': 'push', 'button': 'C_UP'},
            'push_C_DOWN': {'type': 'push', 'button': 'C_DOWN'},
            'push_C_LEFT': {'type': 'push', 'button': 'C_LEFT'},
            'push_C_RIGHT': {'type': 'push', 'button': 'C_RIGHT'},
            'hold_C_UP': {'type': 'hold', 'button': 'C_UP'},
            'hold_C_DOWN': {'type': 'hold', 'button': 'C_DOWN'},
            'hold_C_LEFT': {'type': 'hold', 'button': 'C_LEFT'},
            'hold_C_RIGHT': {'type': 'hold', 'button': 'C_RIGHT'},
            'push_UP_RIGHT': {'type': 'push', 'button': 'UP_RIGHT'},
            'push_UP_LEFT': {'type': 'push', 'button': 'UP_LEFT'},
            'push_DOWN_RIGHT': {'type': 'push', 'button': 'DOWN_RIGHT'},
            'push_DOWN_LEFT': {'type': 'push', 'button': 'DOWN_LEFT'},
            'hold_UP_RIGHT': {'type': 'hold', 'button': 'UP_RIGHT'},
            'hold_UP_LEFT': {'type': 'hold', 'button': 'UP_LEFT'},
            'hold_DOWN_RIGHT': {'type': 'hold', 'button': 'DOWN_RIGHT'},
            'hold_DOWN_LEFT': {'type': 'hold', 'button': 'DOWN_LEFT'}
        }

    def connect(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.serial_baud_rate, timeout=2)
            self.logger.info("Serial port opened.")
        except Exception as e:
            self.logger.error(f"Failed to open serial port: {e}")
            raise

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.logger.info("Serial port closed.")

    def _send_button_command(self, button_code: int, is_press: bool):
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial port is not open")
        command = bytes([ord('S'), button_code, 0x01 if is_press else 0x00, ord('E')])
        self.ser.write(command)

    def _handle_button_press(self, button_code: Union[int, Tuple[int, ...]], is_hold: bool = False):
        if isinstance(button_code, tuple):
            # 複合ボタンの場合
            for code in button_code:
                self._send_button_command(code, True)
            if not is_hold:
                for code in reversed(button_code):  # 逆順でリリース
                    self._send_button_command(code, False)
        else:
            # 単一ボタンの場合
            self._send_button_command(button_code, True)
            if not is_hold:
                self._send_button_command(button_code, False)

    def push_button(self, button: str):
        button_code = self.BUTTON_CODES.get(button.upper())
        if button_code is None:
            raise ValueError(f"Invalid button: {button}")
        self._handle_button_press(button_code, is_hold=False)

    def hold_button(self, button: str):
        button_code = self.BUTTON_CODES.get(button.upper())
        if button_code is None:
            raise ValueError(f"Invalid button: {button}")
        self._handle_button_press(button_code, is_hold=True)

    def release_all_buttons(self):
        for button_code in self._SIMPLE_CODES.values():
            self._send_button_command(button_code, False)

    def excute_button(self,select_commands:list):
        for command in select_commands:
            button = self._COMMAND[command]
            if button['type'] == 'push':
                self.push_button(button['button'])
            else:
                self.hold_button(button['button'])
            time.sleep(3)

if __name__ == "__main__":
    with SwitchControllerAdapter() as controller:
        # Simple button press
        controller.push_button('A')
        # Keep pushing a button
        controller.hold_button('B')
        # Release all buttons
        controller.release_all_buttons()
        # C-button combination
        controller.push_button('C_UP')    # ZR + X の組み合わせ
        controller.hold_button('C_LEFT')  # ZR + Y の組み合わせを維持
# %%
