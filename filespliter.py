# coding:utf-8

def parse_args():
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

    help = "The max memery size of this program will take while running. This option can be like 4g, 3gb, 100m, 200mb. Case match insensitively. Default to 2g."
    parser.add_option('-m', '--memery', dest='memery_sz', default='2g', help=help)

    help = "The max size of each output file. This option can be like 4g, 3gb, 100m, 200mb. Case match insensitively. Default to 2g."
    parser.add_option('-s', '--size', dest='output_sz', default='2g', help=help)

    help = "Attempt to rewrite files if the output file alreardy exist rather than display a warning message and exit."
    parser.add_option('-f', '--force', dest="safe", action="store_false", default=True, help=help)
    print dir(parser)
    opts, file_or_dir = parser.parse_args()
    print opts
    print file_or_dir
    if len(file_or_dir)!=2 :
        parser.error('There should be only one file and directory name, %d given.'%(len(file_or_dir)))

    from os.path import isfile, isdir
    src, dst = file_or_dir
    if isdir(src):
        if isfile(dst) and opts.safe:
            parser.error('File {0} already exist. Please rename the output file name or give the -f option to force to rewrite the file.'.format(dst))
        parser.mode = 'combine'
    elif isfile(src):
        if isdir(dst) and opts.safe:
            parser.error('Directory {0} already exist. Please rename the output directory name or give the -f option to force to use the existing directory, in this case files in the directory may be rewrote.'.format(dst))
        parser.mode = 'split'

    #if not addresses:
    #    print parser.format_help()
    #    parser.exit()
    #def parse_address(addr):
    #     if ':' not in addr:
    #         host = '127.0.0.1'
    #         port = addr
    #     else:
    #         host, port = addr.split(':', 1)

    #     if not port.isdigit():
    #         parser.error('Ports must be integers.')

    #     return host, int(port)
    #return map(parse_address, addresses)

if __name__ == '__main__':
    args = parse_args()
