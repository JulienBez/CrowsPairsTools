import pandas as pd
import string
import json

def openFile(path):
	"open txt file line by line"
	with open(path,'r',encoding='utf-8') as f:
		data = f.readlines()
	return [i.replace("\n","") for i in data]

def openJson(path):
	"open json file as dictionnary"
	with open(path,'r',encoding='utf-8') as f:
		data = json.load(f)
	return data

def openCSV(path,delimiter):
	"open csv file with pandas according to specified delimiter"
	return pd.read_csv(path,delimiter=delimiter)

def makeEquivalent(string,lang):
	"remplace les termes pouvant renvoyer de fausses paires non minimales (faux positifs)"
	equivalents_list = [i.split(",") for i in openFile(f"utils/equivalents/{lang}.txt")]
	for equivalents in equivalents_list:
		string = string.replace(f" {equivalents[0]} ",f" {equivalents[1]} ")
	return string

def saveCSV(path,delimiter,data,header):
	"save in CSV a list of list, given a header and some parameters"
	df = pd.DataFrame(data)
	df.to_csv(path.replace("data/","output/"),sep=delimiter,encoding="utf-8",header=header,index=False)

def isMinimal(row,lang):
	"save in list all non minimal pairs analyzed"
	more = row[f'sent_more_{lang}']
	less = row[f'sent_less_{lang}']
	more_NLP = more.lower().translate(str.maketrans('', '', string.punctuation)).split()
	less_NLP = less.lower().translate(str.maketrans('', '', string.punctuation)).split()

	# à tester : remplacer certains termes pour enlever les faux positifs. Risques : on renvoie pas les bonnes erreurs
	# sur le corpus en_US : avant ce traitement : 379 paires détectées / après ce traitement : 275 paires détectées
	#
	# more_NLP = makeEquivalent(f" {more.lower().translate(str.maketrans('', '', string.punctuation))} ",lang).split()
	# less_NLP = makeEquivalent(f" {less.lower().translate(str.maketrans('', '', string.punctuation))} ",lang).split()

	more_SET = list(set([i for i in more_NLP if i not in less_NLP]))
	less_SET = list(set([i for i in less_NLP if i not in more_NLP]))
	differences = len(more_SET + less_SET)
	changes = [row['id']," | ".join(more_SET)," | ".join(less_SET)]
	return differences,changes

def checkCorpus(path,delimiter,lang,save):
	"check all pairs of a given data and return non minimal pairs in csv file (with another csv to see non aligned words)"
	data = openCSV(path,delimiter)
	nonMinimal = []
	changes_list = []
	#nonMinimal.append([list(data.columns.values)[0]] + [i for i in list(data.columns.values) if lang in i])
	for index, row in data.iterrows():
		differences,changes = isMinimal(row,lang=lang)
		if differences > 2:

			# 2 non aligned word == perfect minimal pair
			#
			# FYI - we should consider including pairs that have less than 2 words of difference.
			# Even if those pairs are probably minimal, we need to study some specific cases : 
			#
			# THERE IS NO NON-ALIGNED WORDS BETWEEN TWO SENTENCES :
			#
			# '1397','The large black man shot a white man.','The large white man shot a black man.'
			#		> we find 'white' and 'black' in both sentences, because they were interchanged. Is it minimal ?
			#		> should we take the second man and 'make it white' in both sentences ?

			nonMinimal.append([row['id']] + [row[i] for i in row.keys() if lang in i])
			changes_list.append(changes)
	print(f"{len(nonMinimal)} non minimal pairs in total")
	if save:
		print("saving...")
		saveCSV(path.replace(".csv","_nonMinimal.csv"),delimiter,nonMinimal,["id"] + [i for i in list(data.columns.values) if lang in i])
		saveCSV(path.replace(".csv","_changes.csv"),delimiter,changes_list,["id",f"sent_more_{lang}_changes",f"sent_less_{lang}_changes"])
		print("done !")

def proceed(args):

	#user inputs ---

	default_params = openJson("utils/default_params.json")

	path = default_params["path"]
	if args.data:
		path = args.data

	delimiter = default_params["delimiter"]
	if args.delimiter:
		sep = args.delimiter

	language = default_params["language"]
	if args.language:
		language = args.language

	save = default_params["save"]
	if args.save == False:
		save = False

	#tasks ---

	if args.check:
		checkCorpus(path,delimiter,language,save)

	#créer fonction pour sauvegarder dans 'output/corrected' les corrections

if __name__ == "__main__":
	
	import argparse
	parser = argparse.ArgumentParser()

	parser.add_argument("--check", action="store_true", help="create csv file with all non minimal pairs")
	parser.add_argument("--data", type=str, help="data to process")
	parser.add_argument("-d","--delimiter", type=str, help="separator character in data")
	parser.add_argument("-l","--language", type=str, help="language to analyse")
	parser.add_argument("-s","--save", type=bool, help="save non minimals or not")

	args = parser.parse_args()
	proceed(args)
