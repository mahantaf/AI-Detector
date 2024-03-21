import os
import pandas as pd
from glob import glob
from tree_sitter import Language, Parser

from tree_sitter_ast_cpp import F as F_cpp, remove_comments as R_cpp, analyze_cpp_code
from tree_sitter_ast_java import F as F_java, remove_comments as R_java, analyze_java_code
from tree_sitter_ast_python import F as F_python, remove_comments as R_python


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
        "comment_remover": R_cpp
    },
    "java": {
        "parser": java_parser,
        "generator": F_java,
        "comment_remover": R_java
    },
    "python": {
        "parser": python_parser,
        "generator": F_python,
        "comment_remover": R_python
    }
}

def analyze_code(code, lang):
    provider = providers[lang]
    parser = provider['parser']

    try:
        tree = parser.parse(bytes(code, "utf8"))
        return analyze_java_code(tree, code)
    except Exception as e:
        print(e)
        return None, None

# Function to process CSV files and generate ASTs
def process_csv_files(input_dir, output_dir):
    # Create the output directory structure if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Go through each file in the input directory and subdirectories
    for csv_file in glob(input_dir + '/**/*.csv', recursive=True):
        
        print(f"Processing {csv_file}")
        data = pd.read_csv(csv_file)
        data['idx'] = data.index  # Or however you are determining 'idx'

        # Generate the AST for each code snippet and add a new 'ast' column
        language = "java"
        
        for index, row in data.iterrows():
            keywords, conditional_operators = analyze_code(row['code'], language)
            data.loc[index, 'keywords'] = keywords
            data.loc[index, 'if_else_while_operators'] = conditional_operators

        # Select only the required columns to save in the new CSV

        output_data = data[['idx', 'code', 'actual label', 'SumCyclomatic', 'AvgCountLineCode', 'CountLineCodeDecl', 'CountDeclFunction', 'MaxNesting', 'CountLineBlank', 'keywords', 'if_else_while_operators']]

        # Define the output path by replacing 'data' with 'data_ast' in the csv_file path
        output_path = csv_file.replace(input_dir, output_dir)
        
        # Make sure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save to CSV
        output_data.to_csv(output_path, index=False)


input_dir = 'java'
output_dir = 'java_with_features'
process_csv_files(input_dir, output_dir)