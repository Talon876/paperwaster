#!/usr/bin/env pytest
from paperwaster import parse_message

def test_message_parsing():
    cmd = parse_message('')
    assert cmd['cmd'] == 'nop'
    assert cmd['msg'] == ''

    cmd = parse_message('print')
    assert cmd['cmd'] == 'nop'
    assert cmd['msg'] == 'print'

    cmd = parse_message('print ')
    assert cmd['cmd'] == 'nop'
    assert cmd['msg'] == 'print '

    cmd = parse_message('print the printing printer')
    assert cmd['cmd'] == 'print'
    assert cmd['msg'] == 'the printing printer'

    cmd = parse_message('img 0-2000-4000-20000200-40002000-4004000-20000400-4000203e-400c000-20618400-2040-84000000-20718800-3f1f-fc08000-0-0-0')
    assert cmd['cmd'] == 'image'
    assert cmd['code'] == '0-2000-4000-20000200-40002000-4004000-20000400-4000203e-400c000-20618400-2040-84000000-20718800-3f1f-fc08000-0-0-0'

    cmd = parse_message('reset')
    assert cmd['cmd'] == 'reset'
    cmd = parse_message('reset the printer please')
    assert cmd['cmd'] == 'reset'
