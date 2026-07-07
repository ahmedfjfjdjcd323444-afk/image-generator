import wx
import requests
import io
from PIL import Image
import os

SERVER_URL = "http://127.0.0.1:5000"
API_KEY = "4879bb8a-7f3a-4e2a-9eba-787990510fdd"

class ImageGenApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="توليد الصور - تجربة", size=(700, 700))
        self.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.current_image_data = None
        self.current_prompt = ""

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 30, 30))

        font_title = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        font_normal = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        title = wx.StaticText(panel, label="🖼️ توليد الصور بالذكاء الإصطناعي")
        title.SetFont(font_title)
        title.SetForegroundColour(wx.Colour(0, 200, 255))

        lbl_prompt = wx.StaticText(panel, label="أكتب وصف الصورة:")
        lbl_prompt.SetForegroundColour(wx.Colour(200, 200, 200))

        self.prompt_input = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(600, 60))
        self.prompt_input.SetBackgroundColour(wx.Colour(50, 50, 50))
        self.prompt_input.SetForegroundColour(wx.Colour(255, 255, 255))
        self.prompt_input.SetFont(font_normal)
        self.prompt_input.Bind(wx.EVT_TEXT_ENTER, self.generate_image)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_btn = wx.Button(panel, label="🪄 توليد الصورة", size=(150, 45))
        self.generate_btn.SetBackgroundColour(wx.Colour(0, 120, 200))
        self.generate_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.generate_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.generate_btn.Bind(wx.EVT_BUTTON, self.generate_image)

        self.save_btn = wx.Button(panel, label="💾 حفظ الصورة", size=(150, 45))
        self.save_btn.SetBackgroundColour(wx.Colour(0, 150, 0))
        self.save_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.save_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.save_btn.Enable(False)
        self.save_btn.Bind(wx.EVT_BUTTON, self.save_image)

        btn_sizer.Add(self.generate_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self.save_btn, 0, wx.ALL, 5)

        self.image_display = wx.StaticBitmap(panel, size=(600, 400))
        self.image_display.SetBackgroundColour(wx.Colour(20, 20, 20))

        self.status_label = wx.StaticText(panel, label="اكتب وصف واضغط توليد")
        self.status_label.SetForegroundColour(wx.Colour(0, 255, 0))
        self.status_label.SetFont(font_normal)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        sizer.Add(lbl_prompt, 0, wx.LEFT | wx.TOP, 10)
        sizer.Add(self.prompt_input, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.image_display, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        sizer.Add(self.status_label, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        panel.SetSizer(sizer)
        self.Centre()
        self.Show()

    def generate_image(self, event=None):
        prompt = self.prompt_input.GetValue().strip()
        if not prompt:
            self.status_label.SetLabel("الرجاء كتابة وصف!")
            return

        self.current_prompt = prompt
        self.status_label.SetLabel("جاري توليد الصورة...")
        self.generate_btn.Enable(False)
        self.save_btn.Enable(False)
        self.Layout()
        self.Update()

        try:
            resp = requests.post(f"{SERVER_URL}/generate-image", json={
                "api_key": API_KEY,
                "prompt": prompt
            }, timeout=30)

            if resp.status_code == 200:
                self.current_image_data = resp.content
                img = Image.open(io.BytesIO(self.current_image_data))
                img = img.resize((600, 400), Image.LANCZOS)

                wx_img = self.pil_to_wx(img)
                self.image_display.SetBitmap(wx_img)
                self.save_btn.Enable(True)
                self.status_label.SetLabel(f"✅ تم توليد الصورة بنجاح: {prompt}")
            else:
                err = resp.json().get("error", "فشل التوليد")
                self.status_label.SetLabel(f"❌ {err}")

        except requests.ConnectionError:
            self.status_label.SetLabel("⚠️ السيرفر مو شغال! شغّل server.py أولاً")
        except Exception as e:
            self.status_label.SetLabel(f"❌ خطأ: {e}")
        finally:
            self.generate_btn.Enable(True)

    def pil_to_wx(self, pil_img):
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        width, height = pil_img.size
        data = pil_img.tobytes()
        wx_img = wx.Image(width, height)
        wx_img.SetData(data)
        return wx_img.ConvertToBitmap()

    def save_image(self, event=None):
        if not self.current_image_data:
            return

        with wx.FileDialog(self, "حفظ الصورة", wildcard="PNG files (*.png)|*.png",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                if not path.endswith(".png"):
                    path += ".png"
                with open(path, "wb") as f:
                    f.write(self.current_image_data)
                self.status_label.SetLabel(f"✅ تم حفظ الصورة في:\n{path}")


if __name__ == "__main__":
    app = wx.App(False)
    ImageGenApp()
    app.MainLoop()
