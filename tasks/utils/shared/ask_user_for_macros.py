import subprocess
import sys
import time
import tkinter as tk

WIN_WIDTH_PERCENTAGE = 0.5
WIN_HEIGHT_PERCENTAGE = 0.5


def _execute_command(command):
    """
    Execute the given command.

    Args:
        - command (str): The command to execute.

    Returns:
        - output (str): The output of the command.
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


def _derive_window_geometries():
    output = _execute_command("xdotool getdisplaygeometry")
    x_screen, y_screen = tuple(int(var) for var in output.split(" "))

    window_width = int(WIN_WIDTH_PERCENTAGE * x_screen)
    window_height = int(WIN_HEIGHT_PERCENTAGE * y_screen)
    y_offset = -int(0.12 * (y_screen + window_height))

    # Center the window
    x = (x_screen - window_width) // 2
    y = (y_screen - window_height) // 2

    geometries = {
        "x": x,
        "y": y + y_offset,
        "width": window_width,
        "height": window_height,
    }

    return geometries


def ask_user_for_macros():
    user_input = None

    def submit_text():
        nonlocal user_input
        user_input = text_box.get("1.0", tk.END).strip()
        root.quit()
        root.destroy()
        sys.stdout.flush()
        time.sleep(0.5)

    def focus_submit(event):
        submit_btn.focus()
        return "break"

    root = tk.Tk()
    geometries = _derive_window_geometries()
    root.geometry(
        f"{geometries['width']}x{geometries['height']}+{geometries['x']}+{geometries['y']}"
    )
    root.title("Field for Macros")
    root.configure(
        bg="#A9A9A9"
    )  # Set background color to dark gray (RGB: 169, 169, 169)

    text_box = tk.Text(
        root,
        height=geometries["height"] // 22,
        width=geometries["width"] // 12,
        bg="#DCDCDC",  # Gainsboro gray for a softer brightness
    )
    text_box.pack(padx=10, pady=12)
    text_box.bind("<Tab>", focus_submit)

    submit_btn = tk.Button(
        root,
        text="Submit",
        command=submit_text,
        bg="#D3D3D3",
        activebackground="#696969",  # Darker color when highlighted
    )
    submit_btn.pack(pady=(0, 10))
    submit_btn.bind("<Return>", lambda event: submit_text())
    submit_btn.bind("<Shift-Tab>", lambda event: text_box.focus())

    root.after(100, lambda: _execute_command("xdotool key super+g"))
    root.mainloop()

    return user_input


if __name__ == "__main__":
    # Example usage
    macros = ask_user_for_macros()
    print("User input:", macros)
