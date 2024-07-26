#!/usr/bin/env python3
import sys
import os


def tchunk_to_terms(txt_path, input_filepath, output_dir="output_foreground", output_name="output_name.txt"):
    txt_path = txt_path.strip()


    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_name)

    # 读取base文件内容
    with open(txt_path, 'r', encoding='utf-8') as basefile:
        base_content = basefile.read()

    with open(output_path, 'w', encoding='utf-8') as outfile:
        term_id = 1  # 初始化TERM ID

        # 从input_filepath中读取每个original_word
        for line in open(input_filepath, 'r', encoding='utf-8'):
            parts = line.split('\t')
            if not parts:
                continue

            original_word = parts[0].strip()
            if not original_word:
                continue

            # 查找original_word在base中出现的所有位置，并记录出现次数
            start_pos = 0
            positions = []

            while True:
                found_pos = base_content.find(original_word, start_pos)
                if found_pos == -1:
                    break

                start = found_pos
                end = found_pos + len(original_word) - 1
                positions.append((start, end))

                start_pos = end + 1

            frequency = len(positions)  # 计算出现次数

            for start, end in positions:
                # 将信息写入terms格式
                outfile.write(
                    f'TERM ID="NYU_TERM_{term_id}" STRING="{original_word}" LEMMA="{original_word.upper()}" FREQUENCY="{frequency}" START={start} END={end}\n')
                term_id += 1  # 递增TERM ID

    print(f"Converted {input_filepath} to {output_path}")


def process_paths(name):
    file_list_path = name + ".file_list_2"

    # 检查文件是否存在
    if not os.path.exists(file_list_path):
        print(f"File {file_list_path} not found!")
        return

    # 读取每个路径
    with open(file_list_path, 'r', encoding='utf-8') as file_list:
        i=0
        for original_path in file_list:
            txt_path = original_path
            original_path = original_path.strip()

            # 将原始路径的第一个部分替换为 "output_background"
            parts = original_path.split('/')
            if len(parts) > 1:
                parts[1] = "output_foreground"
                new_path = "/".join(parts)

                # 在.txt后面加上.tchunk
                input_filepath = new_path + ".tchunk"
                if os.path.exists(input_filepath):
                    tchunk_to_terms(txt_path,input_filepath,name,name+ str(i) + ".terms")
                    i+=1
                else:
                    print(f"File {input_filepath} not found!")

# process_paths("离散数学")
def main(args):
    print("Start to convert tchunk to terms...")
    process_paths(args[1])
if __name__ == '__main__': sys.exit(main(sys.argv))


