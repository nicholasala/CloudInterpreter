import sys
import os
import CloudInterpreter
import OctreeFormatTools as oft

# pensa tre volte, programma una

def main(argv):
    if len(argv) >= 2:

        if not os.path.exists(argv[1]):
            print("Not valid path " + argv[1])
            return

        if os.path.isdir(argv[1]):
            octreeDir = argv[1]
        else:
            if len(argv) == 3 and argv[2] != "none":
                structure = argv[2]
            else:
                structure = "xyz"

            if "c" in structure:
                classes = {
                        1: "albero",
                        2: "casa",
                        3: "stalla",
                        4: "auto",
                        5: "computer",
                        6: "mouse",
                        7: "strada",
                        8: "ristorante",
                        9: "pavimento",
                        10: "cascata",
                        11: "ripostiglio",
                        12: "sedia",
                    }

                gen = oft.Generator(argv[1], structure, classes)
            else:
                gen = oft.Generator(argv[1], structure)

            octreeDir = gen.parse()

        CloudInterpreter.start(octreeDir, 80)

    else:
        print("Usage: python3 INPUT STRUCTURE")
        print("INPUT=path to octree hierarchy or file to convert")
        print("STRUCTURE=structure of file to convert")

if __name__ == "__main__":
   main(sys.argv)