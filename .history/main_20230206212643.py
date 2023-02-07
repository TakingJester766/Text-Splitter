import sys
paragraphs = []
file_path = "book.txt"
sys.setrecursionlimit(10000)
paragraphs = []

def create_text_string(file_path):
    with open(file_path, "r") as file:
        contents = file.read()
        complete_text = contents
        return complete_text

def split_file_into_array(file_path, arr):
    with open(file_path, "r") as file:
        contents = file.read()
        lines = contents.split("\n")
        arr.extend([line for line in lines if line.endswith(".")])

def extract_paragraphs(text, arr, paragraphs):
    if not arr:
        paragraphs.append("....")
        return

    text_to_add = text.split(arr[0], 1)[0]
    text_to_add += arr[0]
    paragraphs.append(text_to_add)

    start_index = text.index(text_to_add) + len(text_to_add)
    new_text = text[start_index:]
    new_arr = arr[1:]

    extract_paragraphs(new_text, new_arr, paragraphs)

arr = []
text = create_text_string(file_path)
split_file_into_array(file_path, arr)

extract_paragraphs(text, arr, paragraphs)

print(paragraphs[-1])