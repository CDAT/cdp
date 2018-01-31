import cdp, sys

class MyCDPParameter(cdp.cdp_parameter.CDPParameter):
     def check_values(self):
          pass


parser = cdp.cdp_parser.CDPParser(MyCDPParameter(),[sys.prefix+"/share/cdp/default_args.json",])
parser.use("num_workers")
parser.print_help()
