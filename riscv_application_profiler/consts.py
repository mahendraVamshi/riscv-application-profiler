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

extensions = {
    'rv32i': ['add', 'addi', 'and', 'andi', 'auipc', 'beq', 'bge', 'bgeu', 'blt', 'bltu', 'bne', 'jal', 'jalr', 'lb', 'lbu', 'lh', 'lhu', 'lui', 'lw', 'or', 'ori', 'sb', 'sh', 'sll', 'slli', 'slt', 'slti', 'sltiu', 'sltu', 'sra', 'srai', 'srl', 'srli', 'sub', 'sw', 'xor', 'xori'],
    'rv64i': ['add', 'addi', 'addiw', 'addw', 'and', 'andi', 'auipc', 'beq', 'bge', 'bgeu', 'blt', 'bltu', 'bne', 'jal', 'jalr', 'lb', 'lbu', 'ld', 'lh', 'lhu', 'lui', 'lw', 'or', 'ori', 'sb', 'sd', 'sh', 'sll', 'slli', 'slliw', 'sllw', 'slt', 'slti', 'sltiu', 'sltu', 'sra', 'srai', 'sraiw', 'sraw', 'srl', 'srli', 'srliw', 'srlw', 'sub', 'subw', 'sw', 'xor', 'xori'],
    'rv32m': ['div', 'divu', 'mul', 'mulh', 'mulhsu', 'mulhu', 'rem', 'remu'],
    'rv64m': ['div', 'divu', 'mul', 'mulh', 'mulhsu', 'mulhu', 'rem', 'remu', 'divuw', 'divw', 'mulw', 'mulh', 'mulhu', 'mulhsu', 'remuw', 'remw'],
    'rv32f': ['fadd.s', 'fclass.s', 'fcvt.s.w', 'fcvt.s.wu', 'fcvt.w.s', 'fcvt.wu.s', 'fdiv.s', 'feq.s', 'fle.s', 'flt.s', 'flw', 'fmadd.s', 'fmax.s', 'fmin.s', 'fmsub.s', 'fmul.s', 'fnmadd.s', 'fnmsub.s', 'fsqrt.s', 'fsgnj.s', 'fsgnjn.s', 'fsgnjx.s', 'fsqrt.s', 'fsub.s'],
    'rv64f': ['fadd.d', 'fclass.d', 'fcvt.d.s', 'fcvt.d.w', 'fcvt.d.wu', 'fcvt.s.d', 'fcvt.w.d', 'fcvt.wu.d', 'fdiv.d', 'feq.d', 'fle.d', 'flt.d', 'fld', 'fmadd.d', 'fmax.d', 'fmin.d', 'fmsub.d', 'fmul.d', 'fnmadd.d', 'fnmsub.d', 'fsqrt.d', 'fsgnj.d', 'fsgnjn.d', 'fsgnjx.d', 'fsqrt.d', 'fsub.d'],
}