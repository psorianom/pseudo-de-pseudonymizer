import xml.etree.ElementTree
import glob

texts = []
all_files = list(glob.glob('../data/extracto/*.xml'))
n_files = len(all_files)
with open("all_capp_new.txt", "w") as filo:
    for i,f in enumerate(all_files):
        print("Treating file {0} => {1}/{2}\n".format(f, i+1 , n_files))
        e = xml.etree.ElementTree.parse(f).getroot()

        try:
            text = [t for t in e.find("TEXTE").find("BLOC_TEXTUEL").find("CONTENU").itertext()]
            space_text = "\n".join(text)
            filo.write("".join(space_text) + "\n")
            
        except Exception as e:
            print("Could not parse file {}\n because {}".format(f, e))
