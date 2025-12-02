import sys
import os
import traceback
import logging
import java_parser

if __name__ == "__main__":
    try:
        if "-debug" in sys.argv:
            logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
            logging.debug("DEBUG MODE")
        else:
            logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

        if "-help" in sys.argv or all(os.path.splitext(arg)[1] == ".py" for arg in sys.argv):
            logging.info("--target, --source, -debug, -help")
            exit()

        if "--target" in sys.argv:
            target = sys.argv[sys.argv.index("--target")+1]

        if "--source" in sys.argv:
            source = sys.argv[sys.argv.index("--source")+1]
        else:
            source = "Main.java"

        logging.info(f"Translating Java code ({source}) to code scheme ({os.path.join(target, "---")}.drawio)")


        with open(source) as source_file:
            source_code = source_file.read()
        java_to_draw_io = java_parser.JavaToDrawIOParser()
        java_class_list = java_to_draw_io.parse(source_code)
        for java_class in java_class_list:
            java_class.save_xml(path=os.path.join(target, f"{java_class.name}.drawio"))
    except Exception as error:
        logging.debug(f"{traceback.format_exc()}")
        logging.error(f"{error}")