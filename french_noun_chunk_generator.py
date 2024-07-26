import argparse
import os


def load_directory(directory_name):
    return os.listdir(directory_name)

def process_data(input_file, output_dir):
    with open(input_file, "r") as file:
        lines = file.readlines()

    processed_lines = []
    previous_tag = 'O'

    for line in lines:
        if line[0] != '<' or '<NP>' in line or '</NP>' in line:
            parts = line.strip().split('\t')
            if len(parts) == 3 and line[0] != '<':
                parts[1], parts[2] = parts[2], parts[1]
                if previous_tag == 'NP':
                    tag = 'B-NP'
                elif previous_tag == 'B-NP' or previous_tag == 'I-NP':
                    tag = 'I-NP'
                else:
                    tag = 'O'
                parts.append(tag)
                previous_tag = tag
            else:
                if '<NP>' in line:
                    previous_tag = 'NP'
                if '</NP>' in line:
                    previous_tag = 'O'
            
            processed_lines.append('    '.join(parts))
    filename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, filename + ".txt.tchunk")
    
    
    with open(output_file, "w") as file:
        for line in processed_lines:
            if '<NP>' not in line and '</NP>' not in line:
                file.write(line + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outputting .tchunk and .pos files. A list of the tchunk names will be provided as well.")
    parser.add_argument('-f', '--foreground', nargs = 1, help = "Please enter the input foreground directory", required = True)
    parser.add_argument('-b', '--background', nargs = 1, help = "Please enter the input background directory", required = True)
    parser.add_argument('-d', '--dict_filter', nargs=1, default= False, help="Please enter True or False for turning dictionary on or off", required=False)
    parser.add_argument('-p','--program_directory',nargs=1,default=".",help="This should be the directory containing program files",required=True)
    args = parser.parse_args()

    foreground_files = load_directory(args.foreground[0])
    background_files = load_directory(args.background[0])
    # dict_on = str_to_bool(args.dict_filter[0])
    # program_dir = args.program_directory[0]

    out_foreground_path = os.path.join(os.getcwd(), "output_foreground")
    out_background_path = os.path.join(os.getcwd(), "output_background")

    print("The program is runing and analyzing model.")

    if not os.path.exists(out_foreground_path):
        os.mkdir(out_foreground_path)
    if not os.path.exists(out_background_path):
        os.mkdir(out_background_path)

    print("Writing into foreground.")
    
    for file in foreground_files:
    	if file.endswith(".txt_tagged"):
            processed_data = process_data(args.foreground[0] + '/' + file, out_foreground_path)
            
    print("Writing into background.")
    
    for file in background_files:
    	if file.endswith(".txt_tagged"):
            processed_data = process_data(args.background[0] + '/' + file, out_background_path)
           














