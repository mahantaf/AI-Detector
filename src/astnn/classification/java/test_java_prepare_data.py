import javalang
from prepare_data_java import get_sequence, get_blocks

# Make sure prepare_data_java.py imports ASTNodeJava from tree_java.py

def test_java_code(java_code):
    # Parse the Java source code into an AST
    tree = javalang.parse.parse(java_code)
    
    # Extract sequences
    sequences = []
    get_sequence(tree, sequences)
    # get_sequences(tree, sequences)
    print("Java Sequences:", sequences)
    
    # Extract blocks
    blocks = []
    get_blocks(tree, blocks)
    # get_blocks(tree, blocks)
    
    print("Java Blocks:")
    new_blocks = []
    for block in blocks:
        # Assuming block is an instance of ASTNodeJava or a 'End' string
        if hasattr(block, 'get_token'):
            new_blocks.append(block.get_token(block.node))
            # new_blocks.append(block.get_token(block.node))
        else:
            new_blocks.append(block)
    print(new_blocks)

# Java source code to test
java_code = """
public class Test {
    public static void main(String[] args) {
        int m = 100, x5 = 0, x1 = 0;
        
        while(m >= 100) { m -= 100; x100 += 1; }
        while(m >= 50) { m -= 50; x50 += 1; }
        x1 = m;
        
        System.out.println(x5);
        System.out.println(x1);
    }
}
"""

test_java_code(java_code)
