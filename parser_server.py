import os.path
import sys
import io
import parser_lib
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Parser-v2"))
from parser.scripts.transfer_morpho import process_batch

def launch(args,q_in,q_out):
    parser=parser_lib.NetworkParserWrapper(args.model,args.parser_dir)
    while True:
        txt=q_in.get()
        conllu=parser.parse_text(txt)
        if args.process_morpho == True:
            conllu=process_batch(conllu, detransfer=True)
        q_out.put(conllu)
        
argparser = argparse.ArgumentParser(description='Parse/Tag conllu text')
argparser.add_argument('--model', default="/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Tagger", help='Model. Default: %(default)s')
argparser.add_argument('--parser-dir', default="Parser-v2", help='Parser. Default: ./%(default)s')
argparser.add_argument('--process_morpho', default=False, action='store_true', help='Run transfer_morpho script to return xpos and morpho to the correct fields')

