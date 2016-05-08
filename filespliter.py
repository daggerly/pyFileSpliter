# coding:utf-8

from sys import stdout, exit
from os.path import isfile, isdir, exists, join, getsize
from math import ceil

MEM_SZ = '2g'
OUTPUT_SZ = '2g'

DONT_EXIST_ERROR = "source file or directory doesn't exists."
MEM_FORMAT_ERROR = "Memery size must starts with integers, then either M(B) or G(B)."
MEM_SIZE_ERROR = "Memery size must be larger than 150MB."

def parse_chunk_sz(chunk_sz):
    chunk_sz = chunk_sz.strip().lower()
    import re
    chunk_sz, base = re.match('(\d+?)([mg]{1})b?', chunk_sz).groups()
    chunk_sz = int(chunk_sz)
    chunk_sz *= (1024*1024 if base=='m' else 1024*1024*1024)
    return  chunk_sz

def check_dst(dst, safe):
    if exists(dst):
        if safe:
            raise Exception("Can't create file or directory {0}: already exist.".format(dst))
        elif isdir(dst):
            from shutil import rmtree
            rmtree(dst)
        else:
            from os import remove
            remove(dst)

def write_file_in_memery_ctl(src_f, dst_f, bytes_to_read, chunk_sz):
    while bytes_to_read>0:
        if bytes_to_read>chunk_sz:
            chunk = src_f.read(chunk_sz)
        else:
            chunk = src_f.read(bytes_to_read)
        dst_f.write(chunk)
        yield
        if len(chunk)<chunk_sz:  return  # when some source filesize is small, return instead still read 
        bytes_to_read -= chunk_sz

def print_percent(total, now):
    if now >= total:
        now = total
    elif now < 0:
        now = 0
    now = (now*100) // total
    n = '*'*(now*80//100)
    line = '%d%% %s'%(now,n)
    stdout.write(line.ljust(80) + '\r')
    stdout.flush()
    from time import sleep
    sleep(1)

def splitfile(src, dst, mem_sz=MEM_SZ, output_sz=OUTPUT_SZ, safe=True):
    if not exists(src):
        raise Exception(DONT_EXIST_ERROR)
    elif not isfile(src):
        raise Exception("Source is not a file.")
    src_sz = getsize(src)

    try:
        mem_sz = parse_chunk_sz(mem_sz)
    except:
        raise Exception(MEM_FORMAT_ERROR)
    mem_sz -= 1024*1024*150
    if mem_sz<=0:
        raise Exception(MEM_SIZE_ERROR)

    try:
        output_sz = parse_chunk_sz(output_sz)
    except:
        raise Exception("Output files' size must starts with integers, then either M(B) or G(B).")
    if output_sz<=0:
        raise Exception('Output size must be larger than 1MB.')

    if mem_sz >= output_sz:
        mem_sz = output_sz
    
    piece_amount = int(ceil(src_sz*1.0 / output_sz))  # file names will generate
    read_times_per_piece = int(ceil(output_sz*1.0 / mem_sz))
    read_times_total = piece_amount * read_times_per_piece

    check_dst(dst, safe)

    from os import makedirs
    makedirs(dst)
    now_trunk = 1
    file_type = src.rsplit('.', 1)[-1]
    print_percent(read_times_total, 0)
    with open(src, 'rb') as src_f:
        for piece_num in range(piece_amount):
            dst_nm = join(dst, str(piece_num)) 
            dst_nm = '.'.join([dst_nm, file_type])
            with open(dst_nm, 'wb') as dst_f:
                write_status = write_file_in_memery_ctl(
                            src_f,
                            dst_f,
                            output_sz,
                            mem_sz,
                )
                for i in write_status:
                    print_percent(read_times_total, now_trunk)
                    now_trunk += 1
    print('\nFinished!')


def combinefile(src, dst, mem_sz=MEM_SZ, safe=True):
    if not exists(src):
        raise Exception(DONT_EXIST_ERROR)
    elif not isdir(src):
        raise Exception("Source is not a directory.")

    from os import listdir
    fnames = listdir(src)
    file_type = fnames[0].rsplit('.', 1)[-1]
    try:
        digit_fnames = sorted([int(i.rsplit('.', 1)[0]) for i in fnames])
        for i in range(len(digit_fnames)): 
            if i not in digit_fnames:
                raise Exception("")
    except:
        raise Exception("File's name in source directory must be sequenced integers start from 1.")

    try:
        mem_sz = parse_chunk_sz(mem_sz)
    except:
        raise Exception(MEM_FORMAT_ERROR)
    mem_sz -= 1024*1024*150  # except python progress memery usage
    if mem_sz<=0:
        raise Exception(MEM_SIZE_ERROR)

    dst = '%s.%s'%(dst, file_type)
    check_dst(dst, safe)
    
    piece_amount = len(digit_fnames) 
    first_file = join(src, '0.%s'%(file_type,))
    read_times_per_piece = int(ceil(getsize(first_file)*1.0 / mem_sz))
    read_times_total = piece_amount * read_times_per_piece

    now_trunk = 0
    print_percent(read_times_total, now_trunk)
    with open(dst, 'wb') as dst_f:
        for piece in digit_fnames:
            src_nm = join(src, '%d.%s'%(piece, file_type))
            with open(src_nm, 'rb') as src_f:
                write_status = write_file_in_memery_ctl(
                            src_f,
                            dst_f,
                            getsize(src_nm),
                            mem_sz,
                )
                for i in write_status:
                    print_percent(read_times_total, now_trunk)
                    now_trunk += 1
    print('\nFinished!')

if __name__ == '__main__':
    import optparse
    usage = """
  split file: %prog [options] file directory
  combine files: %prog [options] directory file
        """
    description = """
  pyFileSpliter splits a large file into small files named 1 2 3 ... which in a directory default named as same as the file,
  or combines files in the directory into a large file named default assame as the directory.
    """
    parser = optparse.OptionParser(usage, description=description)

    help = "The max memery use while this program running. This option can be like 4G, 3GB, 400M, 200MB, and must larger than 100MB. Case match insensitively. Default to 2g."
    parser.add_option('-m', '--memery', dest='memery_size', default=MEM_SZ, help=help)

    help = "The max size of each output file. This option can be like 4G, 3GB, 400M, 200MB. Case match insensitively. Default to 2g."
    parser.add_option('-o', '--output', dest='output_size', help=help)

    help = "Attempt to remove old file and create new file if the output file alreardy exist rather than display a warning message and exit."
    parser.add_option('-f', '--force', dest="safe", action="store_false", default=True, help=help)
    opts, file_and_dir = parser.parse_args()
    if len(file_and_dir)!=2 :
        parser.error('There should be one file and one directory name, {0} given.'.format(len(file_and_dir)))
    src, dst = file_and_dir
    if not exists(src):
        parser.error(DONT_EXIST_ERROR)
    elif isdir(src):
        if opts.output_size:
            parser.error("You may not specify the OUTPUT_SIZE option to combine files")
        try:
            combinefile(
                          src,
                          dst,
                          mem_sz=opts.memery_size,
                          safe=opts.safe
            )
        except Exception as e:
            parser.error(e.message)
    elif isfile(src):
        try:
            splitfile(
                src,
                dst,
                mem_sz=opts.memery_size,
                output_sz=opts.output_size or OUTPUT_SZ,
                safe=opts.safe
            )
        except Exception as e:
            parser.error(e.message)
    else:
        parser.error('Unknow source file type')

