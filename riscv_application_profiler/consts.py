commitlog_regex="^core\s+\d+:\s+\d*\s+(0x[0-9a-fA-F]+)\s+\((0x[0-9a-fA-F]+)\)\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?"
disass_regex = "^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([a-z][a-z\.0-9]*)"
isa_regex = "(i)(m)*(f)*(d)*(c)*"
#rv32im = [rv32,i,m]

# ops_dict = {
#     'loads' : {'rv32i' : ['lb', 'lbu', 'lh', 'lhu',], 'rv64i' : ['ld', 'lh', 'lhu', 'lb', 'lbu', 'lw','lwu']},
#     'stores' : {'rv32i' : ['sb', 'sh', 'sw'], 'rv64i' : ['sb', 'sh', 'sw', 'sd']},
#     'imm computes' : {'rv32i' : ['addi', 'andi', 'ori', 'xori', 'slti', 'sltiu', 'auipc', 'lui'],'rv64i' : ['addi', 'addiw', 'andi', 'ori', 'xori', 'slti', 'sltiu', 'auipc', 'lui']},
#     'imm shifts' : {'rv32i' : ['slli', 'srli', 'srai'], 'rv64i' : ['slli', 'srli', 'srai', 'slliw', 'srliw', 'sraiw']},
#     'reg computes' : {'rv32i' : ['add', 'sub', 'slt', 'sltu', 'xor', 'or', 'and'], 'rv64i' : ['add', 'sub','slt', 'sltu', 'xor', 'or', 'and', 'addw', 'subw']},
#     'reg shifts' : {'rv32i' : ['sll', 'srl', 'sra'], 'rv64i' : ['sll', 'srl', 'sra', 'sllw', 'srlw', 'sraw']},
#     'jumps' : {'rv32i' : ['jal', 'jalr'], 'rv64i' : ['jal', 'jal']},
#     'branches' : {'rv32i' : ['bge', 'bgeu', 'blt', 'bltu', 'beq', 'bne'], 'rv64i' : ['bge', 'bgeu', 'blt', 'bltu', 'beq', 'bne']}
# }

extensions = {
    'rv32i': ['add', 'addi', 'and', 'andi', 'auipc', 'beq', 'bge', 'bgeu', 'blt', 'bltu', 'bne', 'jal', 'jalr',  'lui', 'lw', 'or', 'ori', 'sb', 'sh', 'sll', 'slli', 'slt', 'slti', 'sltiu', 'sltu', 'sra', 'srai', 'srl', 'srli', 'sub', 'sw', 'xor', 'xori'],
    'rv64i': ['add', 'addi', 'addiw', 'addw', 'and', 'andi', 'auipc', 'beq', 'bge', 'bgeu', 'blt', 'bltu', 'bne', 'jal', 'jalr','lui', 'or', 'ori', 'sb', 'sd', 'sh', 'sll', 'slli', 'slliw', 'sllw', 'slt', 'slti', 'sltiu', 'sltu', 'sra', 'srai', 'sraiw', 'sraw', 'srl', 'srli', 'srliw', 'srlw', 'sub', 'subw', 'sw', 'xor', 'xori'],
    #'rv32im': ['div', 'divu', 'mul', 'mulh', 'mulhsu', 'mulhu', 'rem','remu'],
    'rv64im': ['div', 'divu', 'mul', 'mulh', 'mulhsu', 'mulhu', 'rem', 'remu', 'divuw', 'divw', 'mulw', 'mulh', 'mulhu', 'mulhsu', 'remuw', 'remw'],
    'rv32f': ['fadd.s', 'fclass.s', 'fcvt.s.w', 'fcvt.s.wu', 'fcvt.w.s', 'fcvt.wu.s', 'fdiv.s', 'feq.s', 'fle.s', 'flt.s', 'flw', 'fmadd.s', 'fmax.s', 'fmin.s', 'fmsub.s', 'fmul.s', 'fnmadd.s', 'fnmsub.s', 'fsqrt.s', 'fsgnj.s', 'fsgnjn.s', 'fsgnjx.s', 'fsqrt.s', 'fsub.s'],
    'rv64f': ['fadd.d', 'fclass.d', 'fcvt.d.s', 'fcvt.d.w', 'fcvt.d.wu', 'fcvt.s.d', 'fcvt.w.d', 'fcvt.wu.d', 'fdiv.d', 'feq.d', 'fle.d', 'flt.d', 'fld', 'fmadd.d', 'fmax.d', 'fmin.d', 'fmsub.d', 'fmul.d', 'fnmadd.d', 'fnmsub.d', 'fsqrt.d', 'fsgnj.d', 'fsgnjn.d', 'fsgnjx.d', 'fsqrt.d', 'fsub.d'],
}

# for key in ops_dict:
#     ops_dict[key]['rv32mi'] = ops_dict[key]['rv32i']
#     ops_dict[key]['rv64mi'] = ops_dict[key]['rv64i']

#     if key == 'reg computes':
#         ops_dict[key]['rv32mi'].extend(extensions['rv32mi'])
#         ops_dict[key]['rv64mi'].extend(extensions['rv64mi'])

#print(*ops_dict.items(),sep='\n')



ops_dict = {
    'rv32' : {
    'i' : {
    'loads' : ['lb', 'lbu', 'lh', 'lhu',],
    'stores' : ['sb', 'sh', 'sw'],
    'imm computes' : ['addi', 'andi', 'ori', 'xori', 'slti', 'sltiu', 'auipc', 'lui'],
    'imm shifts' : ['slli', 'srli', 'srai'], 'rv64i' : ['slli', 'srli', 'srai', 'slliw', 'srliw', 'sraiw'],
    'reg computes' : ['add', 'sub', 'slt', 'sltu', 'xor', 'or', 'and'], 'rv64i' : ['add', 'sub','slt', 'sltu', 'xor', 'or', 'and', 'addw', 'subw'],
    'reg shifts' : ['sll', 'srl', 'sra'], 'rv64i' : ['sll', 'srl', 'sra', 'sllw', 'srlw', 'sraw'],
    'jumps' : ['jal', 'jalr'], 'rv64i' : ['jal', 'jal'],
    'branches' : ['bge', 'bgeu', 'blt', 'bltu', 'beq', 'bne'], 'rv64i' : ['bge', 'bgeu', 'blt', 'bltu', 'beq', 'bne'],
    'mul' : []
    },
    'm' : {
    'loads' :[],'stores':[],'imm computes' :[],'imm shifts' :[],'reg computes' :[],'reg shifts' :[],'jumps' :[],'branches' :[],
    'mul' : ['div', 'divu', 'mul', 'mulh', 'mulhsu', 'mulhu', 'rem','remu']
    },

    'rv64' : {
    'i' : {
    'loads' : ['ld', 'lh', 'lhu', 'lb', 'lbu', 'lw','lwu']
    }
    }
}
}