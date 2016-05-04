# coding:utf-8

from sys import exit
from os.path import isfile, isdir, exists

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

def create_file(src_f, dst_nm, n, chunk_sz, remainder_sz):
    '''return if nothing to read for src_f'''
    with open(dst_nm, 'wb') as dst_f:
        for _ in range(n):
            chunk = src_f.read(chunk_sz)
            dst_f.write(chunk)
            if len(chunk)<chunk_sz:
                return True
        remainder = src_f.read(remainder_sz)
        dst_f.write(remainder)
        return True if len(remainder)<remainder_sz else False

def splitfile(src, dst, mem_sz=MEM_SZ, output_sz=OUTPUT_SZ, safe=True):
    if not exists(src):
        raise Exception("Error: " + DONT_EXIST_ERROR)
    elif not isfile(src):
        raise Exception("Error: source is not a file.")

    try:
        mem_sz = parse_chunk_sz(mem_sz)
    except:
        raise Exception('Error: '+ MEM_FORMAT_ERROR)
    mem_sz -= 1024*1024*150
    if mem_sz<=0:
        raise Exception('Error: ' + MEM_SIZE_ERROR)

    try:
        output_sz = parse_chunk_sz(output_sz)
    except:
        raise Exception("Error: Output files' size must starts with integers, then either M(B) or G(B).")
    if output_sz<=0:
        raise Exception('Error: output size must be larger than 1MB.')

    if mem_sz >= output_sz:
        mem_sz = output_sz
        read_time_per_file = 1
        remainder_sz = 0
    else:
        read_time_per_file = output_sz//mem_sz
        remainder_sz = output_sz%mem_sz
    check_dst(dst, safe)

    from os import makedirs
    from os.path import join
    file_name = 1
    makedirs(dst)
    with open(src, 'rb') as src_f:
        while True:
            if create_file(
                        src_f,
                        join(dst, str(file_name)),
                        read_time_per_file,
                        mem_sz,
                        remainder_sz,
                    ):
                break
            file_name += 1



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
        if opts.output_sz:
            parser.error("You may not specify the OUTPUT_SIZE option to combine files")
        file_type = 'directory'
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

