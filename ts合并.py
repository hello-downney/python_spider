import os
import subprocess
from pathlib import Path


def merge_ts_files(input_root_dir, output_dir):
    """
    合并 input_root_dir 下每个子目录中的所有 .ts 文件，
    输出为同名的 .mp4 视频文件到 output_dir。

    :param input_root_dir: 包含多个子目录的大目录路径（每个子目录是一组 ts 文件）
    :param output_dir: 合并后视频的输出目录
    """
    input_root = Path(input_root_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    # 遍历每个子目录
    for subdir in input_root.iterdir():
        if not subdir.is_dir():
            continue  # 跳过非目录项

        # 获取该子目录下所有的 .ts 文件（按文件名排序）
        ts_files = sorted(subdir.glob("*.ts"))
        if not ts_files:
            print(f"跳过空目录: {subdir}")
            continue

        # 构建输出文件路径（用子目录名作为输出文件名）
        output_file = output_root / f"{subdir.name}.mp4"

        # 创建临时的文件列表（用于 ffmpeg concat）
        list_file_path = output_root / f"{subdir.name}_filelist.txt"
        with open(list_file_path, 'w', encoding='utf-8') as f:
            for ts in ts_files:
                # 注意：Windows 路径需转义反斜杠或使用正斜杠；ffmpeg 接受正斜杠
                f.write(f"file '{ts.resolve().as_posix()}'\n")

        # 调用 ffmpeg 合并
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file_path),
            '-c', 'copy',  # 直接复制流，不重新编码
            '-y',  # 覆盖输出文件
            str(output_file)
        ]

        print(f"正在合并 {subdir.name} → {output_file}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ 成功: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 失败: {subdir.name}, 错误: {e}")

        # 删除临时文件列表
        list_file_path.unlink()


if __name__ == "__main__":
    # 示例用法
    input_dir = r"D:\伪恋第一季"  # 替换为你的输入大目录
    output_dir = r"D:\伪恋第一季"  # 替换为你想保存合并视频的目录

    merge_ts_files(input_dir, output_dir)
