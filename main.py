import pandas as pd
import string
import json
import os

### File Management ###

def createFile(path):
	"create empty file if not exist file"
	if os.path.exists(path) == False:
		with open(path, 'w') as f: 
   			pass

def createDir(path):
	"create empty directory if not exist"
	if not os.path.exists(path):
		os.makedirs(path)

def openFile(path):
	"open txt file line by line"
	with open(path,'r',encoding='utf-8') as f:
		data = f.readlines()
	return [i.replace("\n","") for i in data] #delete '\n' occurrences

def openJson(path):
	"open json file as dictionnary"
	with open(path,'r',encoding='utf-8') as f:
		data = json.load(f)
	return data

def openCSV(path,delimiter):
	"open csv file with pandas according to specified delimiter"
	return pd.read_csv(path,delimiter=delimiter)

def saveCSV(path,delimiter,data,header):
	"save in csv file a list of lists, given a header and some parameters"
	df = pd.DataFrame(data)
	df.to_csv(path,sep=delimiter,encoding="utf-8",header=header,index=False)

### Utility ###

def askErase(path):
	"ask the user if he wants to erase file if already exist"
	"function made to prevent user to delete all his corrections"
	if os.path.exists(path):
		erase = input(f"{path} already exists. Do you want to erase it ? (Y/n)\n")
		if erase.lower() == "y" or erase.lower() == "yes":
			return True
		else:
			return False
	else:
		return True

def makeEquivalent(string,lang):
	"replace equivalents word : words that have the same function but are different according to gender/other"
	"for example: 'her,his' means 'her' is equivalent to 'his'"
	equivalents_list = [i.split(",") for i in openFile(f"utils/equivalents/{lang}.txt")]
	for equivalents in equivalents_list:
		string = string.replace(f" {equivalents[0]} ",f" {equivalents[1]} ")
	return string

def getDifferences(row,lang):
	"count the number of different words between more_sentences and less_sentences taking into account equivalent words"
	more = str(row[f'sent_more_{lang}'])
	less = str(row[f'sent_less_{lang}'])
	more_NLP = makeEquivalent(f" {more.lower().translate(str.maketrans('', '', string.punctuation))} ",lang).split()
	less_NLP = makeEquivalent(f" {less.lower().translate(str.maketrans('', '', string.punctuation))} ",lang).split()
	more_SET = list(set([i for i in more_NLP if i not in less_NLP]))
	less_SET = list(set([i for i in less_NLP if i not in more_NLP]))
	# It looks like a duplicate of findChanges() function, and it is. But by using makeEquivalent() function we replace
	# some words we might want to keep for analysis.
	# By adding this function to count the differences, we protect those words.
	# This function is far from ideal, but it does the job ! + crowspairs dataset is not that big, there is no real impact
	# on script runtime here.
	return len(more_SET + less_SET)

def findChanges(row,lang):
	"save in list all word modifications in non minimal pairs analyzed"
	more = str(row[f'sent_more_{lang}'])
	less = str(row[f'sent_less_{lang}'])
	more_NLP = more.lower().translate(str.maketrans('', '', string.punctuation)).split()
	less_NLP = less.lower().translate(str.maketrans('', '', string.punctuation)).split()
	more_SET = list(set([i for i in more_NLP if i not in less_NLP]))
	less_SET = list(set([i for i in less_NLP if i not in more_NLP]))
	changes = [row['id']," | ".join(more_SET)," | ".join(less_SET)]
	return changes

### Tasks ###

def checkCorpus(path,delimiter,lang):
	"check all pairs of a given data and return non minimal pairs in csv file (with another csv to see non aligned words)"
	data = openCSV(path,delimiter)
	nonMinimal = []
	changes_list = []
	for index, row in data.iterrows():
		differences = getDifferences(row,lang)
		if differences > 2:

			# 2 non aligned word == perfect minimal pair (one word changed in each sentence)
			#
			# FYI - we should consider including pairs that have less than 2 words of difference.
			# Even if those pairs are probably minimal, we need to study some specific cases : 
			#
			# THERE IS NO NON-ALIGNED WORDS BETWEEN TWO SENTENCES :
			#
			# '1397','The large black man shot a white man.','The large white man shot a black man.'
			#		> we find 'white' and 'black' in both sentences, because they were interchanged. Is it minimal ?
			#		> should we take the second man and 'make it' white in both sentences ?

			nonMinimal.append([row['id']] + [row[i] for i in row.keys() if lang in i])
			changes_list.append(findChanges(row,lang)) #word modified from one sentence to the other
	print(f"{len(nonMinimal)} non minimal pairs in total")
	print("saving...")
	if askErase(path.replace(".csv",f"_{lang}_nonMinimal.csv").replace("data/",f"output/{lang}/")):
		saveCSV(path.replace(".csv",f"_{lang}_nonMinimal.csv").replace("data/",f"output/{lang}/"),delimiter,nonMinimal,["id"] + [i for i in list(data.columns.values) if lang in i])
		saveCSV(path.replace(".csv",f"_{lang}_changes.csv").replace("data/",f"output/{lang}/"),delimiter,changes_list,["id",f"sent_more_{lang}_changes",f"sent_less_{lang}_changes"])
		print("done !")

def applyCorrections(path,delimiter,lang):
	"for each pair in the non minimal csv file, replace the old non minimal pair with the new corrected one in a copy of the original data"
	data = openCSV(path,delimiter).set_index('id')
	corrections = openCSV(path.replace("data/",f"output/{lang}/").replace(".csv",f"_{lang}_nonMinimal.csv"),delimiter).set_index('id')
	data.drop([i for i in list(data.columns.values) if i not in list(corrections.columns.values)],axis=1,inplace=True)
	print("saving corrections...")
	data.update(corrections)
	if askErase(f"output/corrected/CrowS-Pairs_{lang}_corrected.csv"):
		data.to_csv(f"output/corrected/CrowS-Pairs_{lang}_corrected.csv",sep=delimiter,encoding="utf-8")
		print("done !")

### Script ###

def proceed(args):

	#user inputs ---

	default_params = openJson("utils/default_params.json")

	path = default_params["path"]
	if args.data:
		path = args.data

	delimiter = default_params["delimiter"]
	if args.delimiter:
		delimiter = args.delimiter

	language = default_params["language"]
	if args.language:
		language = args.language
	
	#tasks ---
	
	createFile(f"utils/equivalents/{language}.txt")
	createDir(f"output/{language}")

	if args.check:
		checkCorpus(path,delimiter,language)
		
	if args.apply:
		applyCorrections(path,delimiter,language)

if __name__ == "__main__":
	
	import argparse
	parser = argparse.ArgumentParser()

	parser.add_argument("--check", action="store_true", help="create csv file with all non minimal pairs")
	parser.add_argument("--apply", action="store_true", help="applies all manual corrections made on the data")
	parser.add_argument("--data", type=str, help="data to process")
	parser.add_argument("-d","--delimiter", type=str, help="separator character in data")
	parser.add_argument("-l","--language", type=str, help="language to analyse")

	args = parser.parse_args()
	proceed(args)
