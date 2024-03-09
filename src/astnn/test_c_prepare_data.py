from pycparser import c_parser, parse_file
# from prepare_data import get_sequences, get_blocks
from prepare_data import get_blocks, get_sequences

from pycparser import c_parser

parser = c_parser.CParser()

def test_c_code(c_code_path):

    c_code = """
int main()
{
    int m,x100,x1;
    cin>>m;
    for(x100=1;m>=100;x100++)
    {
        m=m-100;
    }
    x1=m;
    cout<<x100<<endl;
    return 0;
}

"""

    
    ast = parser.parse(c_code)
    sequences = []
    get_sequences(ast, sequences)
    print("C Sequences:", sequences)

    # blocks = []
    # get_blocks(ast, blocks)
    # print("C Blocks:", [block.get_token() for block in blocks])

# Assuming test_code.c is in the current directory
test_c_code('test_code.c')
