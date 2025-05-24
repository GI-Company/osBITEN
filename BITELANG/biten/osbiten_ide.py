import webview
import threading
import tkinter as tk
from tkinter.filedialog import askopenfilename
import requests

BITEN_API_URL = "http://localhost:5005/run_biten"

class IDEApp:
    def __init__(self, master):
        self.master = master
        self.master.title("osBITEN CloudCode IDE")
        self.text = tk.Text(master, height=20, width=70)
        self.text.pack()
        self.output = tk.Text(master, height=10, width=70, bg="#222", fg="#fff")
        self.output.pack()
        self.run_button = tk.Button(master, text="Run", command=self.run_code)
        self.run_button.pack()
        self.open_button = tk.Button(master, text="Open", command=self.open_file)
        self.open_button.pack()

    def run_code(self):
        code = self.text.get("1.0", tk.END)
        try:
            r = requests.post(BITEN_API_URL, json={"code": code})
            res = r.json()
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, res["output"])
        except Exception as e:
            self.output.insert(tk.END, f"Error: {e}")

    def open_file(self):
        fname = askopenfilename(filetypes=[("BITE CloudCode", "*.b")])
        if fname:
            with open(fname) as f:
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, f.read())

def start_tk():
    root = tk.Tk()
    app = IDEApp(root)
    root.mainloop()

def main():
    threading.Thread(target=start_tk).start()
    webview.create_window("osBITEN WebView", "http://localhost:5005")  # optional: show API docs or dashboard

if __name__ == "__main__":
    main()