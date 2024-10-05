import winreg
import ctypes

# 注册表根键路径
HID_PATH = r"SYSTEM\CurrentControlSet\Enum\HID"

def modify_flip_flop_wheel(base_key, path, value_to_set):
    """
    修改注册表中指定路径下的 FlipFlopWheel 键值。
    仅当该键存在时才进行修改，不创建新的键值。
    """
    try:
        # 打开 Device Parameters 键
        with winreg.OpenKey(base_key, path + r"\Device Parameters", 0, winreg.KEY_READ | winreg.KEY_WRITE) as device_params_key:
            try:
                # 检查 FlipFlopWheel 是否存在
                flip_flop_wheel_value, reg_type = winreg.QueryValueEx(device_params_key, "FlipFlopWheel")
                
                # 如果存在且类型为 REG_DWORD，则进行修改
                if reg_type == winreg.REG_DWORD:
                    winreg.SetValueEx(device_params_key, "FlipFlopWheel", 0, winreg.REG_DWORD, value_to_set)
                    print(f"成功修改 {path} 中的 FlipFlopWheel 为 {value_to_set}")
                else:
                    print(f"{path} 中 FlipFlopWheel 的数据类型不匹配，跳过修改")
            except FileNotFoundError:
                # 如果未找到 FlipFlopWheel 键值，跳过该键
                print(f"{path} 中未找到 FlipFlopWheel 键值，跳过修改")
    except FileNotFoundError:
        # 如果未找到 Device Parameters 键，跳过该路径
        print(f"未找到路径: {path} 下的 Device Parameters")

def traverse_and_modify_hid_keys(value_to_set):
    """
    遍历 HID 根键及其子键，寻找并修改每个 Device Parameters 下的 FlipFlopWheel 键值。
    """
    try:
        # 打开 HID 根键
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, HID_PATH, 0, winreg.KEY_READ) as hid_key:
            i = 0
            while True:
                try:
                    # 枚举 HID 子键
                    sub_key_name = winreg.EnumKey(hid_key, i)
                    sub_key_path = HID_PATH + "\\" + sub_key_name

                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key_path, 0, winreg.KEY_READ) as sub_key:
                        j = 0
                        while True:
                            try:
                                # 枚举 HID 子键的子键
                                inner_sub_key_name = winreg.EnumKey(sub_key, j)
                                device_parameters_path = sub_key_path + "\\" + inner_sub_key_name

                                # 检查并修改 Device Parameters 中的 FlipFlopWheel 键值
                                modify_flip_flop_wheel(winreg.HKEY_LOCAL_MACHINE, device_parameters_path, value_to_set)
                                j += 1
                            except OSError:
                                # 子子键枚举结束
                                break
                    i += 1
                except OSError:
                    # 子键枚举结束
                    break
    except FileNotFoundError:
        print(f"未找到 HID 路径: {HID_PATH}")

def main():
    # 检查是否以管理员身份运行
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("请以管理员身份运行该脚本！")
        return

    try:
        value_to_set = int(input("请输入要将 FlipFlopWheel 设置为的值（0 或 1）："))
        if value_to_set in (0, 1):
            traverse_and_modify_hid_keys(value_to_set)
        else:
            print("无效的输入，请输入 0 或 1。")
    except ValueError:
        print("请输入有效的整数值！")

if __name__ == "__main__":
    main()
