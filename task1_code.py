import os
import sys
import tempfile
import heapq

def normalize_ipv6(addr):
    """
    Преобразует IPv6 адрес в каноническую форму:
    8 групп по 4 шестнадцатеричные цифры в нижнем регистре
    """
    addr = addr.lower()
    if '::' in addr:
        parts = addr.split(':')
        if addr.startswith('::'):
            parts = [''] + parts[1:]
        elif addr.endswith('::'):
            parts = parts[:-1] + ['']
        empty_index = parts.index('')
        left_parts = [p for p in parts[:empty_index] if p]
        right_parts = [p for p in parts[empty_index + 1:] if p]
        missing_groups = 8 - len(left_parts) - len(right_parts)
        expanded = left_parts + ['0'] * missing_groups + right_parts
    else:
        expanded = addr.split(':')
    normalized = []
    for group in expanded:
        if len(group) < 4:
            group = group.zfill(4)
        normalized.append(group)
    return ':'.join(normalized)

def split_and_sort_chunks(input_file, chunk_size = 10000000):
    """
    Разбивает входной файл на отсортированные куски и возвращает список временных файлов
    """
    temp_files = []
    current_chunk = []
    with open(input_file, 'r') as f:
        for line in f:
            addr = line.strip()
            if addr:
                normalized = normalize_ipv6(addr)
                current_chunk.append(normalized)
                if len(current_chunk) >= chunk_size:
                    current_chunk.sort()
                    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
                    temp_file.write('\n'.join(current_chunk))
                    temp_file.close()
                    temp_files.append(temp_file.name)
                    current_chunk = []
        if current_chunk:
            current_chunk.sort()
            temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
            temp_file.write('\n'.join(current_chunk))
            temp_file.close()
            temp_files.append(temp_file.name)
    return temp_files

def merge_and_count_unique(temp_files, output_file):
    """
    Выполняет многопутевое слияние отсортированных файлов и подсчет уникальных записей
    """
    if not temp_files:
        return 0
    file_handles = []
    try:
        for temp_file in temp_files:
            f = open(temp_file, 'r')
            file_handles.append(f)
        heap = []
        for i, f in enumerate(file_handles):
            line = f.readline().strip()
            if line:
                heapq.heappush(heap, (line, i))
        unique_count = 0
        last_addr = None
        with open(output_file, 'w') as out:
            while heap:
                addr, file_index = heapq.heappop(heap)
                if addr != last_addr:
                    unique_count += 1
                    last_addr = addr
                next_line = file_handles[file_index].readline().strip()
                if next_line:
                    heapq.heappush(heap, (next_line, file_index))
            out.write(str(unique_count))
        return unique_count
    finally:
        for f in file_handles:
            f.close()

def cleanup_temp_files(temp_files):
    """Удаляет временные файлы"""
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    input_string = list(map(str, input().split()))
    input_file = input_string[0]
    output_file = input_string[1]
    if not os.path.exists(input_file):
        sys.exit(1)
    try:
        chunk_size = 10000000
        temp_files = split_and_sort_chunks(input_file, chunk_size)
        unique_count = merge_and_count_unique(temp_files, output_file)
    except Exception as e:
        sys.exit(1)
    finally:
        if 'temp_files' in locals():
            cleanup_temp_files(temp_files)

if __name__ == "__main__":
    main()
