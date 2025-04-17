import os
import subprocess
import sys
import time
import tkinter as tk
import warnings

from PIL import Image, ImageTk

WIN_WIDTH_PERCENTAGE = 0.5
WIN_HEIGHT_PERCENTAGE = 0.5

HELP_IMG_PATH = os.path.join(os.path.dirname(__file__), "help.png")


def _execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


def _derive_main_window_geometries():
    output = _execute_command("xdotool getdisplaygeometry")
    x_screen, y_screen = tuple(int(var) for var in output.split(" "))

    window_width = int(WIN_WIDTH_PERCENTAGE * x_screen)
    window_height = int(WIN_HEIGHT_PERCENTAGE * y_screen)
    y_offset = -int(0.12 * (y_screen + window_height))

    x = (x_screen - window_width) // 2
    y = (y_screen - window_height) // 2

    return {
        "x": x,
        "y": y + y_offset,
        "width": window_width,
        "height": window_height,
    }


def _derive_help_window_geometries(img_width, img_height, padding=(20, 20)):
    output = _execute_command("xdotool getdisplaygeometry")
    x_screen, y_screen = tuple(int(var) for var in output.split(" "))

    screen_padding = (int(0.05 * x_screen), int(0.05 * y_screen))

    x = (x_screen - img_width) // 2
    y = (y_screen - img_height) // 2
    is_width_exceeded = is_height_exceeded = False

    if x < screen_padding[0] * 2:
        img_width = x_screen - screen_padding[0] * 2
        x = screen_padding[0]
        is_width_exceeded = True
    if y < screen_padding[1] * 2:
        img_height = y_screen - screen_padding[1] * 2
        y = screen_padding[1]
        is_height_exceeded = True

    return {
        "x": x,
        "y": y,
        "width": img_width - padding[0] * 2,
        "height": img_height - padding[1] * 2,
        "is_width_exceeded": is_width_exceeded,
        "is_height_exceeded": is_height_exceeded,
    }


def _show_help_window(main_root):
    def close_help():
        help_win.destroy()
        main_root.deiconify()

    img_padding = (20, 20)
    button_space = 40

    img = Image.open(HELP_IMG_PATH)
    geometries = _derive_help_window_geometries(
        img.width, img.height, padding=img_padding
    )
    if geometries["is_width_exceeded"] or geometries["is_height_exceeded"]:
        img = img.resize(
            (geometries["width"], geometries["height"] - button_space), Image.LANCZOS
        )
    help_img = ImageTk.PhotoImage(img)

    main_root.withdraw()
    help_win = tk.Toplevel()
    win_width = int(geometries["width"] + img_padding[0] * 2)
    win_height = int(geometries["height"] + img_padding[1] * 2)
    help_win.geometry(f"{win_width}x{win_height}+{geometries['x']}+{geometries['y']}")
    help_win.title("Help Information")
    help_win.configure(bg="#F5F5F5")

    help_win.help_img = help_img
    image_label = tk.Label(help_win, image=help_img, bg="#F5F5F5")
    image_label.pack(padx=img_padding[0], pady=img_padding[1])

    return_btn = tk.Button(help_win, text="Return", command=close_help, bg="#D3D3D3")
    return_btn.pack(pady=5)
    return_btn.bind("<Return>", lambda event: close_help())


def ask_user_for_macros(submit_file):
    user_input = ""

    def root_destroy():
        root.quit()
        root.destroy()
        sys.stdout.flush()
        time.sleep(0.5)

    def submit_text():
        nonlocal user_input
        user_input = text_box.get("1.0", tk.END).strip()
        with open(submit_file, "w", encoding="utf-8") as file:
            file.write(user_input)

        root_destroy()

    def focus_submit(event=None):
        submit_btn.focus()
        return "break"

    def focus_text(event=None):
        text_box.focus()
        return "break"

    def select_all(event):
        text_box.tag_add("sel", "1.0", "end")
        return "break"

    def cut(event):
        text_box.event_generate("<<Cut>>")
        return "break"

    def focus_cancel(event=None):
        cancel_btn.focus()
        return "break"

    def focus_help(event=None):
        help_btn.focus()
        return "break"

    def cancel_process(event=None):
        nonlocal user_input
        user_input = ""
        root_destroy()
        return "break"

    def load_last_macros(event=None):
        if os.path.exists(submit_file):
            with open(submit_file, "r", encoding="utf-8") as file:
                last_macros = file.read()
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, last_macros)
        else:
            warnings.warn("No previous macros found.")
        return "break"

    def focus_last_macros(event=None):
        last_macros_btn.focus()
        return "break"

    root = tk.Tk()
    geometries = _derive_main_window_geometries()
    root.geometry(
        f"{geometries['width']}x{geometries['height']}+{geometries['x']}+{geometries['y']}"
    )
    root.title("Field for Macros")
    root.configure(bg="#A9A9A9")

    text_box = tk.Text(
        root,
        height=geometries["height"] // 22,
        width=geometries["width"] // 12,
        bg="#DCDCDC",
    )
    text_box.pack(padx=10, pady=12)
    text_box.bind("<Tab>", focus_submit)
    text_box.bind("<Shift-Tab>", focus_help)
    text_box.bind("<Control-a>", select_all)
    text_box.bind("<Control-x>", cut)

    button_frame = tk.Frame(root, bg="#A9A9A9")
    button_frame.pack(pady=(0, 10))

    submit_btn = tk.Button(
        button_frame,
        text="Submit",
        command=submit_text,
        bg="#D3D3D3",
        activebackground="#696969",
    )
    submit_btn.bind("<Tab>", focus_last_macros)
    submit_btn.bind("<Shift-Tab>", focus_text)
    submit_btn.bind("<Return>", lambda event: submit_text())
    submit_btn.grid(row=0, column=0, padx=10)

    last_macros_btn = tk.Button(
        button_frame,
        text="Load Last",
        command=load_last_macros,
        bg="#D3D3D3",
    )
    last_macros_btn.bind("<Tab>", focus_cancel)
    last_macros_btn.bind("<Shift-Tab>", focus_submit)
    last_macros_btn.bind("<Return>", lambda event: load_last_macros())
    last_macros_btn.grid(row=0, column=1, padx=10)

    cancel_btn = tk.Button(
        button_frame,
        text="Cancel",
        command=cancel_process,
        bg="#D3D3D3",
        activebackground="#B22222",
    )
    cancel_btn.bind("<Tab>", focus_help)
    cancel_btn.bind("<Shift-Tab>", focus_last_macros)
    cancel_btn.bind("<Return>", lambda event: cancel_process())
    cancel_btn.grid(row=0, column=2, padx=10)

    help_btn = tk.Button(
        button_frame,
        text="Help",
        command=lambda: _show_help_window(root),
        bg="#D3D3D3",
    )
    help_btn.bind("<Tab>", focus_text)
    help_btn.bind("<Shift-Tab>", focus_cancel)
    help_btn.bind("<Return>", lambda event: _show_help_window(root))
    help_btn.grid(row=0, column=3, padx=10)

    root.mainloop()

    return user_input


if __name__ == "__main__":
    submit_file = "_macros.txt"
    macros = ask_user_for_macros(submit_file=submit_file)
    print("User input:", macros)
