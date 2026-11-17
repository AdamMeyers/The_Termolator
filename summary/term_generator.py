#!/usr/bin/env python3
import sys
import os


def occurrence_groups(txt_path, input_filepath):
    """Yield one group per chunk row, sharing positions for repeated words."""
    with open(txt_path, encoding="utf-8") as source:
        text = source.read()

    matches = {}
    with open(input_filepath, encoding="utf-8") as chunks:
        for line in chunks:
            word = line.split("\t", 1)[0].strip()
            if not word:
                continue
            if word not in matches:
                positions = []
                start = text.find(word)
                while start != -1:
                    end = start + len(word)
                    positions.append((start, end - 1))
                    start = text.find(word, end)
                matches[word] = positions
            if matches[word]:
                yield word, matches[word]


def term_attributes(word, frequency):
    return f'STRING="{word}" LEMMA="{word.upper()}" FREQUENCY="{frequency}"'


def tchunk_to_terms(txt_path, input_filepath, output_dir="output_foreground", output_name="output_name.txt"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_name)
    with open(output_path, "w", encoding="utf-8") as outfile:
        term_id = 1
        for word, positions in occurrence_groups(txt_path.strip(), input_filepath):
            attributes = term_attributes(word, len(positions))
            for start, end in positions:
                outfile.write(f'TERM ID="NYU_TERM_{term_id}" {attributes} START={start} END={end}\n')
                term_id += 1
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


