#coding:utf-8

def parse_args():
    import optparse
    usage = """
   split file: %prog [options] src_file des_folder
   combine file: %prog [options] src_folder des_file
        """
    parser = optparse.OptionParser(usage)
    help = "The memery size of this program will take while running. This option can be like 4g, 4gb, 100m, 100mb. Case match insensitively. Default to 2g."
    parser.add_option('-m', '--memery', dest='memery_sz', default='2g', help=help)
    help = "The size of each output file. This option can be like 4g, 4gb, 100m, 100mb. Case match insensitively. Default to 2g."
    parser.add_option('-o', '--output', dest='output_sz', default='2g', help=help)
    _, addresses = parser.parse_args()
    print _
    print _.memery_sz
    print addresses
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
