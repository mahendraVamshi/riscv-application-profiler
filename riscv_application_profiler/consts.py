commitlog_regex="^core\s+\d+:\s+\d*\s+(0x[0-9a-fA-F]+)\s+\((0x[0-9a-fA-F]+)\)\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?"
disass_regex = "^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([a-z][a-z\.0-9]*)"

ops_dict = {
    "RV32": {
        "I": {
            "loads": [
                "lb",
                "lbu",
                "lh",
                "lhu",
                "lw",
            ],
            "stores": ["sb", "sh", "sw"],
            "imm computes": [
                "addi",
                "andi",
                "ori",
                "xori",
                "slti",
                "sltiu",
                "auipc",
                "lui",
            ],
            "imm shifts": ["slli", "srli", "srai"],
            "reg computes": ["add", "sub", "slt", "sltu", "xor", "or", "and"],
            "reg shifts": ["sll", "srl", "sra"],
            "jumps": ["jal", "jalr"],
            "branches": ["bge", "bgeu", "blt", "bltu", "beq", "bne"],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            #'nop' : ['nop'],
        },
        "M": {
            "loads": [],
            "stores": [],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [
                "div",
                "divu",
                "mul",
                "mulh",
                "mulhsu",
                "mulhu",
                "rem",
                "remu",
            ],
            "reg shifts": [],
            "jumps": [],
            "branches": [],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            #'nop' : [],
        },
        "F": {
            "loads": ["flw","flwsp","fld","fldsp"],
            "stores": ["fsw","fswsp","fsd","fsdsp"],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [
                "fmadd.s",
                "fmsub.s",
                "fadd.s",
                "fsub.s",
                "fmul.s",
                "fdiv.s",
                "fmin.s",
                "fmax.s",
                "fsqrt.s",
                "fmadd.s",
                "fmsub.s",
                "fnmsub.s"
                "fnmadd.s"
            ],
            "reg shifts": [],
            "jumps": [],
            "compares": ["flt.s","feq.s","fle.s"],
            "conversions":[
                "fcvt.w.s",
                "fcvt.wu.s",
                "fcvt.s.w",
                "fcvt.s.wu",
                "fsgnj.s",
                "fsgnjn.s",
                "fsgnjx.s",
            ],
            "moves":["fmv.s","fmv.x.w","fmv.w.x"],
            "classifies":["fclass.s"],
            "branches": [],
            "csrs":["frcsr.s","fscsr.s","frrm","fsrm","fsrmi",],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
        },
        "D": {
            "loads": ["fld","fldsp"],
            "stores": ["fsd","fsdsp"],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [
                "fmadd.d",
                "fmsub.d",
                "fadd.d",
                "fsub.d",
                "fmul.d",
                "fdiv.d",
                "fmin.d",
                "fmax.d",
                "fsqrt.d",
                "fmadd.d",
                "fmsub.d",
                "fnmsub.d"
                "fnmadd.d"
            ],
            "reg shifts": [],
            "jumps": [],
            "compares": ["flt.d","feq.d","fle.d"],
            "conversions":[
                "fcvt.w.d",
                "fcvt.wu.d",
                "fcvt.d.w",
                "fcvt.d.wu",
                "fsgnj.d",
                "fsgnjn.d",
                "fsgnjx.d",
            ],
            "moves":[],
            "classifies":["fclass.d"],
            "branches": [],
            "csrs":["frcsr","fscsr","frrm","fsrm","fsrmi",],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            
        }, 
        "C": {
            "loads": [
                "c.lwsp",
                "c.lw",
            ],
            "stores": [
                "c.swsp",
                "c.sw",
            ],
            "imm computes": [
                "c.li",
                "c.lui",
                "c.addi",
                "c.addi16sp",
                "c.addi4spn",
                "c.andi",
            ],
            "imm shifts": [
                "c.slli",
                "c.srli",
                "c.srai",
            ],
            "reg computes": [
                "c.add",
                "c.addw",
                "c.sub",
                "c.subw",
                "c.and",
                "c.or",
                "c.xor",
                "c.mv",
            ],
            "reg shifts": ["c.sll", "c.srl", "c.sra"],
            "jumps": ["c.j", "c.jal", "c.jr", "c.jalr"],
            "branches": [
                "c.beqz",
                "c.bnez",
                "c.bltz",
                "c.bgez",
                "c.bltz",
                "c.bgez",
                "c.bltzal",
                "c.bgezal",
            ],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            #'nop' : ['c.nop'],
        },  # c.nop, c.ebreak, c.mv,
        "B": {
            "set/clear": ["sbset","sbclr","sbseti","sbclri",],
            "count": ["clz","ctz","pcnt",],
            "extract/insert": ["sbext","sbextu","sbset","sbinv","sbseti","sbinvi",],
            "permute": ["pack","packh","packu","packw","unpack","unpackh","unpacku","unpackw"],
            "gather/scatter": ["gather","gatheru","gatherx","scatter","scatteru","scatterx"],
            "funnel/merge": ["funnel","unfunnel","merge","mergei"],
            "crc": ["crc32.b","crc32.h","crc32.w","crc32c.b","crc32c.h","crc32c.w"],
            "loads": [],
            "stores": [],
            "imm computes": ["bclri","bexti","binv","bseti",],
            "imm shifts": [],
            "reg computes": ["add.uw",
                             "andn",
                             "bclr",
                             "bext",
                             "binv",
                             "bset",
                             "clmul",
                             "clmulh",
                             "clmulr",
                             "clz",
                             "clzw",
                             "cpop"],#"or","xor","not","andc","orn","xnor",
            "reg shifts": ["sll","srl","sra","slo","sro","rol","ror",],
            "jumps": [],
            "compares": [],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "branches": [],
            "csrs":[],
        },
        "P": {
            "loads": [
                "vld",
            ],
            "stores": [
                "vst",
            ],
            "imm computes": [
                "vaddi",
                "vsubi",
                "vslli",
                "vsrli",
                "vsrai",
                "vandi",
                "vori",
                "vxori",
                "vslti",
                "vsltiu",
            ],
            "imm shifts": [
                "vsll",
                "vsrl",
                "vsra",
            ],
            "reg computes": [
                "vadd",
                "vsub",
                "vand",
                "vor",
                "vxor",
                "vslt",
                "vsltu",
                "vmin",
                "vmax",
                "vseq",
                "vsne",
                "vzext",
                "vsext",
            ],
            "reg shifts": [
                "vssrl",
                "vssra",
                "vsll",
                "vsrl",
                "vsra",
            ],
            "jumps": [],
            "branches": [],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
        },
        "Zicsr": {
            "loads": [],
            "stores": [],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [],
            "reg shifts": [],
            "jumps": [],
            "compares": [],
            "conversions": [],
            "moves": [],
            "classifies": [],
            "branches": [],
            "csrs": ["csrrw","csrrs","csrrc","csrrwi","csrrsi","csrrci"],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": []
            },

    },
    "RV64": {
        "I": {
            "loads": ["ld", "lh", "lhu", "lb", "lbu", "lw", "lwu"],
            "stores": ["sb", "sh", "sw", "sd"],
            "imm computes": [
                "addi",
                "addiw",
                "andi",
                "ori",
                "xori",
                "slti",
                "sltiu",
                "auipc",
                "lui",
            ],
            "imm shifts": ["slli", "srli", "srai", "slliw", "srliw", "sraiw"],
            "reg computes": [
                "add",
                "sub",
                "slt",
                "sltu",
                "xor",
                "or",
                "and",
                "addw",
                "subw",
            ],
            "reg shifts": ["sll", "srl", "sra", "sllw", "srlw", "sraw"],
            "jumps": ["jal", "jalr"],
            "branches": ["bge", "bgeu", "blt", "bltu", "beq", "bne"],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            #'nop' : ['nop'],
        },
        "M": {
            "loads": [],
            "stores": [],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [
                "div",
                "divu",
                "mul",
                "mulh",
                "mulhsu",
                "mulhu",
                "rem",
                "remu",
            ],
            "reg shifts": [],
            "jumps": [],
            "branches": [],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            #'nop' : [],
        },
        "F": {
            "loads": ["flw","flwsp","fld","fldsp"],
            "stores": ["fsw","fswsp","fsd","fsdsp"],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [
                "fmadd.s",
                "fmsub.s",
                "fadd.s",
                "fsub.s",
                "fmul.s",
                "fdiv.s",
                "fmin.s",
                "fmax.s",
                "fsqrt.s",
                "fmadd.s",
                "fmsub.s",
                "fnmsub.s"
                "fnmadd.s"
            ],
            "reg shifts": [],
            "jumps": [],
            "compares": ["flt.s","feq.s","fle.s"],
            "conversions":[
                "fcvt.w.s",
                "fcvt.wu.s",
                "fcvt.s.w",
                "fcvt.s.wu",
                "fcvt.l.s",
                "fcvt.lu.s",
                "fcvt.s.l",
                "fcvt.s.lu",
                "fsgnj.s",
                "fsgnjn.s",
                "fsgnjx.s",
            ],
            "moves":["fmv.s","fmv.x.w","fmv.w.x"],
            "classifies":["fclass.s"],
            "branches": [],
            "csrs":["frcsr","fscsr","frrm","fsrm","fsrmi",],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
        },
        "D": {
            "loads": ["fld","fldsp"],
            "stores": ["fsd","fsdsp"],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [
                "fmadd.d",
                "fmsub.d",
                "fadd.d",
                "fsub.d",
                "fmul.d",
                "fdiv.d",
                "fmin.d",
                "fmax.d",
                "fsqrt.d",
                "fmadd.d",
                "fmsub.d",
                "fnmsub.d"
                "fnmadd.d"
            ],
            "reg shifts": [],
            "jumps": [],
            "compares": ["flt.d","feq.d","fle.d"],
            "conversions":[
                "fcvt.w.d",
                "fcvt.wu.d",
                "fcvt.d.w",
                "fcvt.d.wu",
                "fcvt.l.d",
                "fcvt.lu.d",
                "fcvt.d.l",
                "fcvt.d.lu",
                "fsgnj.d",
                "fsgnjn.d",
                "fsgnjx.d",
            ],
            "moves":["fmv.x.d","fmv.d.x"],
            "classifies":["fclass.d"],
            "branches": [],
            "csrs":["frcsr","fscsr","frrm","fsrm","fsrmi",],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            
        },
        "C": {
            "loads": [
                "c.lwsp",
                "c.ldsp",
                "c.lw",
                "c.ld",
            ],  # c.lq, c.lqsp, c.flwsp, c.fldsp, c.fld, c.flw
            "stores": [
                "c.swsp",
                "c.sdsp",
                "c.sw",
                "c.sd",
            ],  # c.sq,  c.sqsp, c.fswsp, c.fsdsp, c.fsd, c.fsw
            "imm computes": [
                "c.addi4spn",
                "c.addi",
                "c.addiw",
                "c.li",
                "c.lui",
                "c.addi16sp",
                "c.addi4spn",
                "c.addi",
                "c.addiw",
                "c.li",
                "c.lui",
                "c.addi16sp",
            ],
            "imm shifts": ["c.slli", "c.srli", "c.srai"],
            "reg computes": [
                "c.add",
                "c.sub",
                "c.xor",
                "c.or",
                "c.and",
                "c.subw",
                "c.addw",
                "c.mv",
            ],
            "reg shifts": ["c.sll", "c.srl", "c.sra"],
            "jumps": ["c.j", "c.jal", "c.jr", "c.jalr"],
            "branches": [
                "c.beqz",
                "c.bnez",
                "c.bltz",
                "c.bgez",
                "c.bltz",
                "c.bgez",
                "c.bltzal",
                "c.bgezal",
            ],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            #'nop' : ['c.nop'],
        },

        "B": {
            "set/clear": ["sbset","sbclr","sbseti","sbclri",],
            "count": ["clz","ctz","pcnt",],
            "extract/insert": ["sbext","sbextu","sbset","sbinv","sbseti","sbinvi",],
            "permute": ["pack","packh","packu","packw","unpack","unpackh","unpacku","unpackw"],
            "gather/scatter": ["gather","gatheru","gatherx","scatter","scatteru","scatterx"],
            "funnel/merge": ["funnel","unfunnel","merge","mergei"],
            "crc": ["crc32.b","crc32.h","crc32.w","crc32c.b","crc32c.h","crc32c.w","crc32c.d","crc32.d"],
            "loads": [],
            "stores": [],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": ["and","or","xor","not","andc","orn","xnor",],
            "reg shifts": ["sll","srl","sra","slo","sro","rol","ror",],
            "jumps": [],
            "compares": [],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "branches": [],
            "csrs":[],
        },
        "P": {
            "loads": [
                "vld",
            ],
            "stores": [
                "vst",
            ],
            "imm computes": [
                "vaddi",
                "vsubi",
                "vslli",
                "vsrli",
                "vsrai",
                "vandi",
                "vori",
                "vxori",
                "vslti",
                "vsltiu",
            ],
            "imm shifts": [
                "vsll",
                "vsrl",
                "vsra",
            ],
            "reg computes": [
                "vadd",
                "vsub",
                "vand",
                "vor",
                "vxor",
                "vslt",
                "vsltu",
                "vmin",
                "vmax",
                "vseq",
                "vsne",
                "vzext",
                "vsext",
            ],
            "reg shifts": [
                "vssrl",
                "vssra",
                "vsll",
                "vsrl",
                "vsra",
            ],
            "jumps": [],
            "branches": [],
            "set/clear": [],
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": [],
            "compares":[],
            "conversions":[],
            "moves":[],
            "classifies":[],
            "csrs":[],
        },
        "Zicsr": {
            "loads": [],
            "stores": [],
            "imm computes": [],
            "imm shifts": [],
            "reg computes": [],
            "reg shifts": [],
            "jumps": [],
            "compares": [],
            "conversions": [],
            "moves": [],
            "classifies": [],
            "branches": [],
            "csrs": ["csrrw","csrrs","csrrc","csrrwi","csrrsi","csrrci"], #"csrr","csrw","csrs","csrc","csrwi","csrsi","csrci"
            "set/clear": [],  
            "count": [],
            "extract/insert": [],
            "permute": [],
            "gather/scatter": [],
            "funnel/merge": [],
            "crc": []
            },
    },
}
reg_file = {f'x{i}':'0' for i in range(32)}