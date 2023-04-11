commitlog_regex="^core\s+\d+:\s+\d*\s+(0x[0-9a-fA-F]+)\s+\((0x[0-9a-fA-F]+)\)\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?"
disass_regex = "^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([a-z][a-z\.0-9]*)"

ops_dict = {
    'loads' : ['lb', 'lh', 'lw', 'lbu', 'lhu', 'ld', 'lwu'],
    'stores' : ['sb', 'sh', 'sw', 'sd'],
    'imm computes' : ['addi', 'addiw', 'andi', 'ori', 'xori', 'slli', 'srli', 'srai', 'slliw', 'srliw', 'sraiw', 'slti', 'sltiu', 'auipc', 'lui'],
    'imm shifts' : ['slli', 'srli', 'srai', 'slliw', 'srliw', 'sraiw'],
    'reg computes' : ['add', 'sub', 'sll', 'slt', 'sltu', 'xor', 'srl', 'sra', 'or', 'and', 'addw', 'subw', 'sllw', 'srlw', 'sraw'],
    'reg shifts' : ['sll', 'srl', 'sra', 'sllw', 'srlw', 'sraw'],
    'jumps' : ['jal', 'jalr'],
    'branches' : ['bge', 'bgeu', 'blt', 'bltu', 'beq', 'bne']
}