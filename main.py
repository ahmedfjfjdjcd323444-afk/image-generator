import wx
import requests
import json
import os
import pyperclip

SERVER_URL = "http://127.0.0.1:5000"
KEYS_FILE = os.path.join(os.path.dirname(__file__), "api_keys.json")

class ApiKeyApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="مولد API Keys", size=(500, 400))
        self.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.keys = []

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 30, 30))

        font_title = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        font_normal = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        title = wx.StaticText(panel, label="🔑 مولد API Keys")
        title.SetFont(font_title)
        title.SetForegroundColour(wx.Colour(0, 200, 0))

        self.generate_btn = wx.Button(panel, label="إنشاء API Key", size=(200, 50))
        self.generate_btn.SetBackgroundColour(wx.Colour(0, 100, 200))
        self.generate_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.generate_btn.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.generate_btn.Bind(wx.EVT_BUTTON, self.generate_key)

        self.keys_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_EDIT_LABELS)
        self.keys_list.SetBackgroundColour(wx.Colour(20, 20, 20))
        self.keys_list.SetForegroundColour(wx.Colour(255, 255, 255))
        self.keys_list.AppendColumn("API Key", width=300)
        self.keys_list.AppendColumn("نسخ", width=100)
        self.keys_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.copy_key)

        self.status_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.status_box.SetBackgroundColour(wx.Colour(20, 20, 20))
        self.status_box.SetForegroundColour(wx.Colour(0, 255, 0))
        self.status_box.SetMinSize((450, 60))

        self.info_label = wx.StaticText(panel, label="طريقة الاستخدام:\nضع API Key في كودك وأرسل request إلى /generate-image مع api_key و prompt")
        self.info_label.SetForegroundColour(wx.Colour(200, 200, 200))
        self.info_label.SetFont(font_normal)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        sizer.Add(self.generate_btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        sizer.Add(self.keys_list, 1, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.status_box, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.info_label, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        panel.SetSizer(sizer)
        self.Centre()
        self.Show()
        self.load_keys()

    def load_keys(self):
        if os.path.exists(KEYS_FILE):
            with open(KEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.keys = list(data.keys())
                self.refresh_list()

    def refresh_list(self):
        self.keys_list.DeleteAllItems()
        for key in self.keys:
            idx = self.keys_list.InsertItem(self.keys_list.GetItemCount(), key)
            self.keys_list.SetItem(idx, 1, "📋 نسخ")

    def generate_key(self, event=None):
        try:
            resp = requests.post(f"{SERVER_URL}/generate-key", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                new_key = data["api_key"]
                self.keys.append(new_key)
                self.refresh_list()
                self.status_box.SetValue(f"✅ تم إنشاء مفتاح جديد:\n{new_key}")
            else:
                self.status_box.SetValue("❌ فشل في إنشاء المفتاح")
        except requests.ConnectionError:
            self.status_box.SetValue("⚠️ السيرفر شغال؟ تأكد من تشغيل server.py")
        except Exception as e:
            self.status_box.SetValue(f"❌ خطأ: {e}")

    def copy_key(self, event):
        idx = event.GetIndex()
        key = self.keys_list.GetItemText(idx)
        pyperclip.copy(key)
        self.status_box.SetValue(f"📋 تم نسخ المفتاح:\n{key}")


if __name__ == "__main__":
    app = wx.App(False)
    ApiKeyApp()
    app.MainLoop()
