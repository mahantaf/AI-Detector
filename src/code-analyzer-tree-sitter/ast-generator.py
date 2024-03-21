import os
import pandas as pd
from glob import glob
from tree_sitter import Language, Parser

from tree_sitter_ast_cpp import F as F_cpp, remove_comments as R_cpp, analyze_cpp_code, replace_function_names as RF_cpp, rename_variables as RV_cpp
from tree_sitter_ast_java import F as F_java, remove_comments as R_java, analyze_java_code, replace_method_names as RF_java, rename_variables as RV_java
from tree_sitter_ast_python import F as F_python, remove_comments as R_python, replace_function_names as RF_python, rename_variables as RV_python


CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')
cpp_parser = Parser()
cpp_parser.set_language(CPP_LANGUAGE)

JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
java_parser = Parser()
java_parser.set_language(JAVA_LANGUAGE)

PY_LANGUAGE = Language('build/my-languages.so', 'python')
python_parser = Parser()
python_parser.set_language(PY_LANGUAGE)

providers = {
    "cpp": {
        "parser": cpp_parser,
        "generator": F_cpp,
        "comment_remover": R_cpp,
        "function_replacer": RF_cpp,
        "variable_replacer": RV_cpp
    },
    "java": {
        "parser": java_parser,
        "generator": F_java,
        "comment_remover": R_java,
        "function_replacer": RF_java,
        "variable_replacer": RV_java
    },
    "python": {
        "parser": python_parser,
        "generator": F_python,
        "comment_remover": R_python,
        "function_replacer": RF_python,
        "variable_replacer": RV_python
    }
}


def change_variable_names(code, lang):
    provider = providers[lang]
    parser = provider['parser']
    variable_replacer = provider['variable_replacer']

    try:
        tree = parser.parse(bytes(code, "utf8"))
        code_with_replaced_variables = variable_replacer(tree, code)
        return code_with_replaced_variables
    except Exception as e:
        print("[ERROR] [CHANGE_VARIABLE_NAMES]: ", e)
        return None

def change_function_names(code, lang):
    provider = providers[lang]
    parser = provider['parser']
    function_replacer = provider['function_replacer']

    try:
        tree = parser.parse(bytes(code, "utf8"))
        code_with_replaced_functions = function_replacer(tree, code)
        return code_with_replaced_functions
    except Exception as e:
        print("[ERROR] [CHANGE_FUNCTION_NAMES]: ", e)
        return None

def remove_blank_lines(code):
    # Split the code into lines
    lines = code.split('\n')
    # Remove lines that are empty or contain only whitespace
    non_blank_lines = [line for line in lines if line.strip()]
    # Join the non-blank lines back into a single string
    cleaned_code = '\n'.join(non_blank_lines)
    return cleaned_code

def remove_comments(code, lang):
    provider = providers[lang]
    parser = provider['parser']
    comment_remover = provider['comment_remover']
    try:
        tree = parser.parse(bytes(code, "utf8"))
        code_with_no_comment = comment_remover(tree, code)
        return code_with_no_comment
    except Exception as e:
        print("[ERROR] [REMOVE_COMMENTS]: ", e)
        return None

def generate_ast_sequence(code, lang):
    provider = providers[lang]
    parser = provider['parser']
    generator = provider['generator']

    code = str(code)
    try:
        tree = parser.parse(bytes(code, "utf8"))
        AST = generator(tree.root_node, bytes(code, 'utf8'))
        return ' '.join(AST)
    except Exception as e:
        print("[ERROR] [GENERATE AST]: ", e)
        return None

def process_csv_files(input_dir, output_dir):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for csv_file in glob(input_dir + '/**/*.csv', recursive=True):
        print(f"Processing {csv_file}")
        data = pd.read_csv(csv_file)
        data['idx'] = data.index

        language = language_inference_from_path(csv_file)

        original_size = len(data)
        
        data['new_code'] = data['code'].apply(lambda code: change_variable_names(code, language))
        data['ast'] = data['new_code'].apply(lambda code: generate_ast_sequence(code, language))
        
        data.dropna(subset=['ast'], inplace=True)

        number_removed = original_size - len(data)
        print(f"{csv_file} not parsed: {number_removed}/{original_size}")

        
        output_data = data[['idx', 'code', 'new_code', 'ast', 'actual label']]
        # output_data = data[['idx', 'code', 'ast', 'actual label']]

        output_path = csv_file.replace(input_dir, output_dir)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        output_data.to_csv(output_path, index=False)

def language_inference_from_path(file_path):
    parts = file_path.split(os.sep)[-1].split('_')
    language = parts[2] 
    return language.lower()


input_dir = 'data_temp1'
output_dir = 'data_ablation_study_code_embedding/uniform_variables_name'
process_csv_files(input_dir, output_dir)

# code = """
# class MiniRomanConverter {
# public:
#     string int_to_mini_roman(int number) {
#         string result = "";
#         vector<int> values = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
#         vector<string> symbols = {""m"", ""cm"", ""d"", ""cd"", ""c"", ""xc"", ""l"", ""xl"", ""x"", ""ix"", ""v"", ""iv"", ""i""};

#         for (int i = 0; i < values.size(); i++) {
#             while (number >= values[i]) {
#                 number -= values[i];
#                 result += symbols[i];
#             }
#         }

#         // Convert the result to lowercase
#         for (char &c : result) {
#             c = tolower(c);
#         }

#         return result;
#     }
# };
# """

# changed_code = remove_comments(code, "cpp")
# print(changed_code)
