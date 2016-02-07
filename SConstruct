import bootloadercmd as b

env = Environment(PIC = '24FJ128GB206',
                  CC = 'xc16-gcc',
                  PROGSUFFIX = '.elf',
                  CFLAGS = '-g -omf=elf -x c -mcpu=$PIC',
                  LINKFLAGS = '-omf=elf -mcpu=$PIC -Wl,--script="app_p24FJ128GB206.gld"',
                  CPPPATH = '../lib')
env.PrependENVPath('PATH', '/opt/microchip/xc16/v1.25/bin')
bin2hex = Builder(action = 'xc16-bin2hex $SOURCE -omf=elf',
                  suffix = 'hex',
                  src_suffix = 'elf')
env.Append(BUILDERS = {'Hex' : bin2hex})
list = Builder(action = 'xc16-objdump -S -D $SOURCE > $TARGET',
               suffix = 'lst',
               src_suffix = 'elf')
env.Append(BUILDERS = {'List' : list})

env.Program('mp1', ['mp1.c',
                    '../lib/descriptors.c',
                    '../lib/common.c',
                    '../lib/timer.c',
                    '../lib/pin.c',
                    '../lib/oc.c',
                    '../lib/md.c',
                    '../lib/ui.c',
                    '../lib/spi.c',
                    '../lib/usb.c'])

def load_function(target, source, env):
    bl = b.bootloadercmd()
    bl.import_hex(source[0].rstr())
    bl.write_device()
    bl.bootloader.start_user()
    bl.bootloader.close()
    return None

load = Builder(action=load_function,
               suffix = 'none',
               src_suffix = 'hex')

env.Append(BUILDERS = {'Load' : load})

env.Hex('mp1')
env.List('mp1')

env.Load('mp1')
