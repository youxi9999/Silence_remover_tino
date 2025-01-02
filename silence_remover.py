# 导入必要的库
import tkinter as tk  # 用于创建图形界面
from tkinter import ttk, filedialog, messagebox  # 用于文件选择对话框和消息提示框
import os  # 用于文件路径操作
import threading
import subprocess  # 添加这行
from pydub import AudioSegment  # 用于音频处理
from pydub.silence import split_on_silence  # 用于检测和分割静音部分

def convert_png_to_ico(png_path):
    try:
        from PIL import Image
        ico_path = png_path[:-4] + '.ico'
        if not os.path.exists(ico_path):
            img = Image.open(png_path)
            img.save(ico_path, format='ICO')
        return ico_path
    except ImportError:
        print("未安装 pillow 库，无法转换图标格式")
        return png_path
    except Exception as e:
        print(f"转换图标格式时出错: {str(e)}")
        return png_path

def set_app_icon(root):
    try:
        icon_path = "icon.png"
        if os.path.exists(icon_path):
            if os.name == 'nt':  # Windows系统
                ico_path = convert_png_to_ico(icon_path)
                root.iconbitmap(ico_path)
            else:  # Linux/Mac系统
                img = tk.PhotoImage(file=icon_path)
                root.tk.call('wm', 'iconphoto', root._w, img)
    except Exception as e:
        print(f"无法加载图标: {str(e)}")

def remove_silence(input_file, silence_thresh=-40, min_silence_len=50, keep_silence=100):
    """
    移除音频文件中的静音部分
    input_file: 输入音频文件路径
    silence_thresh: 静音阈值（dB），低于此值视为静音
    min_silence_len: 最小静音长度（毫秒）
    keep_silence: 保留的静音长度（毫秒）
    """
    try:
        # 读取音频文件
        print(f"Reading audio file: {input_file}")
        audio = AudioSegment.from_file(input_file)  # 加载音频文件
        print(f"Audio duration: {len(audio)} ms")  # 打印音频总长度

        # 打印处理参数
        print(f"Splitting audio with parameters: silence_thresh={silence_thresh}, min_silence_len={min_silence_len}, keep_silence={keep_silence}")
        
        # 分割音频，去除静音部分
        audio_parts = split_on_silence(
            audio,
            min_silence_len=min_silence_len,  # 最小静音长度
            silence_thresh=silence_thresh,     # 静音阈值
            keep_silence=keep_silence          # 保留的静音长度
        )
        print(f"Number of audio parts after splitting: {len(audio_parts)}")  # 打印分割后的片段数量

        # 合并所有非静音片段
        combined = AudioSegment.empty()  # 创建空的音频段
        for i, part in enumerate(audio_parts):
            combined += part  # 添加每个非静音片段
            print(f"Added part {i+1}, current duration: {len(combined)} ms")

        # 生成输出文件路径（在原文件同目录下，添加"_no_silence"后缀）
        output_file = os.path.join(os.path.dirname(input_file), 
                                 os.path.splitext(os.path.basename(input_file))[0] + "_no_silence.mp3")
        
        # 导出处理后的音频
        print(f"Exporting processed audio to: {output_file}")
        combined.export(output_file, format="mp3", bitrate="192k")
        
        # 打印处理结果
        print(f"Export completed. Final duration: {len(combined)} ms")
        print(f"Silence removed: {len(audio) - len(combined)} ms")

        return output_file

    except Exception as e:
        # 错误处理
        print(f"An error occurred: {str(e)}")
        return None

class SilenceRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("自动剪辑气口工具 作者@田同学Tino")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 设置应用图标
        set_app_icon(self.root)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件选择部分
        self.file_frame = ttk.LabelFrame(self.main_frame, text="文件选择", padding="5")
        self.file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=0, padx=5)
        
        self.browse_button = ttk.Button(self.file_frame, text="浏览", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=5)
        
        # 参数设置部分
        self.params_frame = ttk.LabelFrame(self.main_frame, text="参数设置", padding="5")
        self.params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 静音阈值设置
        ttk.Label(self.params_frame, text="静音阈值 (dB):").grid(row=0, column=0, padx=5)
        self.silence_thresh = tk.IntVar(value=-40)
        self.thresh_scale = ttk.Scale(
            self.params_frame,
            from_=-60,
            to=-20,
            variable=self.silence_thresh,
            orient=tk.HORIZONTAL,
            command=lambda x: self.update_scale_value(self.silence_thresh, self.thresh_entry)
        )
        self.thresh_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.thresh_entry = ttk.Entry(self.params_frame, width=5)
        self.thresh_entry.insert(0, "-40")
        self.thresh_entry.grid(row=0, column=2, padx=5)
        self.thresh_entry.bind('<Return>', lambda e: self.update_entry_value(
            self.thresh_entry, self.silence_thresh, -60, -20))
        
        # 最小静音长度设置
        ttk.Label(self.params_frame, text="最小静音长度 (ms):").grid(row=1, column=0, padx=5)
        self.min_silence = tk.IntVar(value=50)
        self.min_scale = ttk.Scale(
            self.params_frame,
            from_=0,
            to=500,
            variable=self.min_silence,
            orient=tk.HORIZONTAL,
            command=lambda x: self.update_scale_value(self.min_silence, self.min_entry)
        )
        self.min_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.min_entry = ttk.Entry(self.params_frame, width=5)
        self.min_entry.insert(0, "50")
        self.min_entry.grid(row=1, column=2, padx=5)
        self.min_entry.bind('<Return>', lambda e: self.update_entry_value(
            self.min_entry, self.min_silence, 0, 500))
        
        # 保留静音长度设置
        ttk.Label(self.params_frame, text="保留静音长度 (ms):").grid(row=2, column=0, padx=5)
        self.keep_silence = tk.IntVar(value=100)
        self.keep_scale = ttk.Scale(
            self.params_frame,
            from_=0,
            to=500,
            variable=self.keep_silence,
            orient=tk.HORIZONTAL,
            command=lambda x: self.update_scale_value(self.keep_silence, self.keep_entry)
        )
        self.keep_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        self.keep_entry = ttk.Entry(self.params_frame, width=5)
        self.keep_entry.insert(0, "100")
        self.keep_entry.grid(row=2, column=2, padx=5)
        self.keep_entry.bind('<Return>', lambda e: self.update_entry_value(
            self.keep_entry, self.keep_silence, 0, 500))
        
        # 进度显示
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, length=400,
                                      mode='determinate', variable=self.progress_var)
        self.progress.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=2)
        
        # 处理按钮
        self.process_button = ttk.Button(self.main_frame, text="开始处理",
                                       command=self.start_processing)
        self.process_button.grid(row=4, column=0, columnspan=2, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.ogg *.flac *.m4a *.wma"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.file_path.set(file_path)

    def start_processing(self):
        if not self.file_path.get():
            messagebox.showwarning("警告", "请先选择音频文件！")
            return
        
        # 禁用按钮，防止重复处理
        self.process_button.state(['disabled'])
        self.browse_button.state(['disabled'])
        
        # 在新线程中处理音频
        thread = threading.Thread(target=self.process_audio)
        thread.daemon = True
        thread.start()

    def process_audio(self):
        try:
            self.status_var.set("正在处理...")
            self.progress_var.set(0)
            
            output_file = remove_silence(
                self.file_path.get(),
                silence_thresh=self.silence_thresh.get(),
                min_silence_len=self.min_silence.get(),
                keep_silence=self.keep_silence.get()
            )
            
            if output_file:
                self.progress_var.set(100)
                self.status_var.set("处理完成！")
                messagebox.showinfo("成功", f"静音已移除。输出文件保存为：\n{output_file}")
                # 打开输出文件所在的文件夹
                folder_path = os.path.dirname(output_file)
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # macOS 和 Linux
                    try:
                        subprocess.run(['open', folder_path])  # macOS
                    except FileNotFoundError:
                        subprocess.run(['xdg-open', folder_path])  # Linux
            else:
                self.status_var.set("处理失败！")
                messagebox.showerror("错误", "音频处理失败。")
        
        except Exception as e:
            self.status_var.set("发生错误！")
            messagebox.showerror("错误", f"处理过程中发生错误：\n{str(e)}")
        
        finally:
            # 重新启用按钮
            self.process_button.state(['!disabled'])
            self.browse_button.state(['!disabled'])

    def update_scale_value(self, var, entry):
        """更新输入框的值"""
        entry.delete(0, tk.END)
        entry.insert(0, str(var.get()))

    def update_entry_value(self, entry, var, min_val, max_val):
        """更新滑块的值"""
        try:
            value = int(entry.get())
            if min_val <= value <= max_val:
                var.set(value)
            else:
                entry.delete(0, tk.END)
                entry.insert(0, str(var.get()))
                messagebox.showwarning("警告", f"请输入 {min_val} 到 {max_val} 之间的整数！")
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, str(var.get()))
            messagebox.showwarning("警告", "请输入整数！")

def main():
    root = tk.Tk()
    app = SilenceRemoverGUI(root)
    root.mainloop()

# 程序入口点
if __name__ == "__main__":
    main()