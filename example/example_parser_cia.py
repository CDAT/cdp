import cdp

class MyCDPParameter(cdp.cdp_parameter.CDPParameter):
     def check_values(self):
          pass


parser = cdp.cdp_parser.CDPParser(MyCDPParameter(),["/export/gleckler1/git/CIA/Defaults/DefArgsCIA.json",])
parser.use("cid")
parser.print_help()
