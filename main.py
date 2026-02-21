import sys
import argparse

CHUNK_SIZE = 64 * 1024  # 64KB，可根据实际情况调整

def encode_chunked(input_file, output_file):
    """正向编码：分块处理，输出变换后的文件"""
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        prev_byte = None  # 上一块的最后一个原始字节，初始为 None 表示还没有数据

        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break

            out_chunk = bytearray(len(chunk))
            if prev_byte is None:
                # 第一块：第一个字节不变
                out_chunk[0] = chunk[0]
                for i in range(1, len(chunk)):
                    out_chunk[i] = chunk[i] ^ chunk[i-1]
            else:
                # 非第一块：第一个字节与上一块的最后一个原始字节异或
                out_chunk[0] = chunk[0] ^ prev_byte
                for i in range(1, len(chunk)):
                    out_chunk[i] = chunk[i] ^ chunk[i-1]

            fout.write(out_chunk)

            # 记录当前块的最后一个原始字节，供下一块使用
            prev_byte = chunk[-1]

def decode_chunked(input_file, output_file):
    """逆向解码：分块恢复原文件"""
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        prev_byte = None  # 上一块最后一个已恢复的原始字节

        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break

            out_chunk = bytearray(len(chunk))
            if prev_byte is None:
                # 第一块：第一个字节直接就是原始值
                out_chunk[0] = chunk[0]
                for i in range(1, len(chunk)):
                    out_chunk[i] = chunk[i] ^ out_chunk[i-1]
            else:
                # 非第一块：第一个字节与上一块的最后一个原始字节异或
                out_chunk[0] = chunk[0] ^ prev_byte
                for i in range(1, len(chunk)):
                    out_chunk[i] = chunk[i] ^ out_chunk[i-1]

            fout.write(out_chunk)

            # 记录当前块的最后一个恢复出的原始字节
            prev_byte = out_chunk[-1]

def main():
    parser = argparse.ArgumentParser(description='逐字节 XOR 变换（分块处理，适合大文件）')
    parser.add_argument('mode', choices=['encode', 'decode'], help='操作模式：encode 或 decode')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('output', help='输出文件路径')
    parser.add_argument('--chunk-size', type=int, default=64*1024, help='分块大小（字节），默认 64KB')
    args = parser.parse_args()

    # 更新全局块大小
    global CHUNK_SIZE
    CHUNK_SIZE = args.chunk_size

    try:
        if args.mode == 'encode':
            encode_chunked(args.input, args.output)
        else:
            decode_chunked(args.input, args.output)
        print(f"处理完成，结果已写入 {args.output}")
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()