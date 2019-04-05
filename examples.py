import socketscpi
import numpy as np


def awg_example(ipAddress, port=5025):
    """Tests generic waveform transfer to M8190. Length and granularity checks not performed."""
    awg = socketscpi.SocketInstrument(host=ipAddress, port=port, timeout=10)
    print(awg.instId)
    awg.write('*rst')
    awg.query('*opc?')

    fs = 10e9
    freq = 100e6
    res = 'wsp'

    awg.write('func:mode arb')
    awg.write(f'trace1:dwidth {res}')
    awg.write(f'frequency:raster {fs}')

    awg.write('output1:route dac')
    awg.write('output1:norm on')

    rl = int(fs / freq * 64)
    t = np.linspace(0, rl / fs, rl, endpoint=False)
    wfm = np.array(2047 * np.sin(2 * np.pi * freq * t), dtype=np.int16) << 4

    awg.write(f'trace:def 1, {rl}')
    awg.binblockwrite('trace:data 1, 0, ', wfm)

    awg.write('trace:select 1')
    awg.write('init:cont on')
    awg.write('init:imm')
    awg.query('*opc?')

    awg.err_check()
    awg.disconnect()


def vna_example(ipAddress, port=5025):
    """Test generic VNA connection, sweep control, and data transfer."""
    vna = socketscpi.SocketInstrument(host=ipAddress, port=port, timeout=10)
    print(vna.instId)

    vna.write('system:fpreset')
    vna.query('*opc?')

    measName = 'meas1'
    vna.write('display:window1:state on')
    vna.write(f'calc1:parameter:define "{measName}", "S11"')
    vna.write(f'display:window1:trace1:feed "{measName}"')
    vna.write(f'calc1:parameter:select "{measName}"')

    vna.write('initiate:continuous off')
    vna.write('initiate:immediate')
    vna.query('*opc?')
    vna.write('display:window1:y:auto')

    vna.write('format:border swap')
    vna.write('format real,64')

    vna.write('calculate1:data? fdata')
    meas = vna.binblockread(dtype=np.float64)
    vna.query('*opc?')

    vna.write('calculate1:x?')
    freq = vna.binblockread(dtype=np.float64)
    vna.query('*opc?')

    vna.err_check()
    vna.disconnect()

    return freq, meas


def main():
    # awg_example('10.112.181.139', port=5025)
    vna_example('10.112.181.177', port=5025)

if __name__ == '__main__':
    main()