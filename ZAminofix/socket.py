import time
import json
import websocket
from threading import Thread
from .lib.util import helpers
from .lib.util import objects, helpers

# ======================
# Callbacks
# ======================
class Callbacks:
    def __init__(self, client, debug=False):
        self.client = client
        self.debug = debug
        self.handlers = {}
        self.methods = {
            304: self._resolve_chat_action_start,
            306: self._resolve_chat_action_end,
            1000: self._resolve_chat_message
        }
        self.chat_methods = {
    "0:0": "on_text_message",
    "0:100": "on_image_message",
    "0:103": "on_youtube_message",
    "1:0": "on_strike_message",
    "2:110": "on_voice_message",
    "3:113": "on_sticker_message",
    "52:0": "on_voice_chat_not_answered",
    "53:0": "on_voice_chat_not_cancelled",
    "54:0": "on_voice_chat_not_declined",
    "55:0": "on_video_chat_not_answered",
    "56:0": "on_video_chat_not_cancelled",
    "57:0": "on_video_chat_not_declined",
    "58:0": "on_avatar_chat_not_answered",
    "59:0": "on_avatar_chat_not_cancelled",
    "60:0": "on_avatar_chat_not_declined",
    "100:0": "on_delete_message",
    "101:0": "on_group_member_join",
    "102:0": "on_group_member_leave",
    "103:0": "on_chat_invite",
    "104:0": "on_chat_background_changed",
    "105:0": "on_chat_title_changed",
    "106:0": "on_chat_icon_changed",
    "107:0": "on_voice_chat_start",
    "108:0": "on_video_chat_start",
    "109:0": "on_avatar_chat_start",
    "110:0": "on_voice_chat_end",
    "111:0": "on_video_chat_end",
    "112:0": "on_avatar_chat_end",
    "113:0": "on_chat_content_changed",
    "114:0": "on_screen_room_start",
    "115:0": "on_screen_room_end",
    "116:0": "on_chat_host_transfered",
    "117:0": "on_text_message_force_removed",
    "118:0": "on_chat_removed_message",
    "119:0": "on_text_message_removed_by_admin",
    "120:0": "on_chat_tip",
    "121:0": "on_chat_pin_announcement",
    "122:0": "on_voice_chat_permission_open_to_everyone",
    "123:0": "on_voice_chat_permission_invited_and_requested",
    "124:0": "on_voice_chat_permission_invite_only",
    "125:0": "on_chat_view_only_enabled",
    "126:0": "on_chat_view_only_disabled",
    "127:0": "on_chat_unpin_announcement",
    "128:0": "on_chat_tipping_enabled",
    "129:0": "on_chat_tipping_disabled",
    "65281:0": "on_timestamp_message",
    "65282:0": "on_welcome_message",
    "65283:0": "on_invite_message",
}


        self.client.handle_socket_message = self.resolve

    def _log(self, msg):
        if self.debug:
            print(f"[callbacks] {msg}")

    def auto_register(self, scope, prefix="on_"):

        for name, func in scope.items():
            if callable(func) and name.startswith(prefix):
                self.handlers[name] = [func]
                self._log(f"Registered event: {name}")

    def _dispatch(self, event_name, payload):
        event_data = objects.Event(payload).Event
        for handler in self.handlers.get(event_name, []):
            try:
                handler(event_data)
            except Exception as e:
                self._log(f"Handler {event_name} failed: {e}")

    def _resolve_chat_message(self, data):
        key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType',0)}"
        event_name = self.chat_methods.get(key, "default")
        self._dispatch(event_name, data["o"])

    def _resolve_chat_action_start(self, data):
        self._dispatch("on_user_typing_start", data["o"])

    def _resolve_chat_action_end(self, data):
        self._dispatch("on_user_typing_end", data["o"])

    def resolve(self, raw_data):
        try:
            data = json.loads(raw_data)
            resolver = self.methods.get(data["t"], self.default)
            resolver(data)
        except Exception as e:
            self._log(f"Error parsing data: {e}")

    def default(self, data):
        self._dispatch("default", data)


# ======================
# SocketHandler
# ======================
class SocketHandler:
    def __init__(self, client, socket_trace=False, debug=False, auto_run=False):
        self.socket_url = "wss://ws1.aminoapps.com"
        self.client = client
        self.debug = debug
        self.active = False
        self.headers = None
        self.socket = None
        self.socket_thread = None
        self.reconnectTime = 180
        self.reconnect_thread = None

        websocket.enableTrace(socket_trace)

        if auto_run and self.client.sid:
            self.run_amino_socket()

    def reconnect_handler(self):
        while True:
            time.sleep(self.reconnectTime)
            if self.active:
                if self.debug:
                    print(f"[socket][reconnect_handler] Reconnecting Socket")
                self.close()
                self.run_amino_socket()

    def handle_message(self, ws, data):
        self.client.handle_socket_message(data)

    def send(self, data):
        if self.debug:
            print(f"[socket][send] Sending Data : {data}")
        if not self.socket_thread:
            self.run_amino_socket()
            time.sleep(5)
        self.socket.send(data)

    def run_amino_socket(self):
        try:
            if self.debug:
                print(f"[socket][start] Starting Socket")

            if self.client.sid is None:
                return

            final = f"{self.client.device_id}|{int(time.time() * 1000)}"

            self.headers = {
                "NDCDEVICEID": self.client.device_id,
                "NDCAUTH": f"sid={self.client.sid}",
                "NDC-MSG-SIG": helpers.signature(final)
            }

            self.socket = websocket.WebSocketApp(
                f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
                on_message=self.handle_message,
                header=self.headers
            )

            self.active = True
            self.socket_thread = Thread(target=self.socket.run_forever)
            self.socket_thread.start()

            if self.reconnect_thread is None:
                self.reconnect_thread = Thread(target=self.reconnect_handler)
                self.reconnect_thread.start()

            if self.debug:
                print(f"[socket][start] Socket Started")
        except Exception as e:
            print(e)

    def close(self):
        if self.debug:
            print(f"[socket][close] Closing Socket")
        self.active = False
        try:
            self.socket.close()
        except Exception as closeError:
            if self.debug:
                print(f"[socket][close] Error while closing Socket : {closeError}")
