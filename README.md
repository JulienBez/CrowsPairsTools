# Disclaimer
This work is the prolongation of the work I realised for my fist year master memoire. It is based on the CrowS-Pairs dataset. Here are some links : 

- https://github.com/nyu-mll/crows-pairs (original CrowS-Pairs)
- https://gitlab.inria.fr/french-crows-pairs/acl-2022-paper-data-and-code (french CrowS-Pairs) 

# CrowsPairsTools
This tool was made to help you create a well formed adaptation of the CrowS-Pairs dataset in your own language. It reviews every pair written in your language and points out the ones that are not minimal. As a reminder : a minimal pair is composed of two sentences with as few changing words as possible from one to the other. For more informations about the dataset, please refer to [the original work](https://github.com/nyu-mll/crows-pairs).

# Installation
To install CrowsPairsTools, you must have **Python 3.x** and **pip** installed. Clone this repository on your computer. Open your terminal and navigate to CrowsPairsTools's folder (where **main.py** is located). Once here, run the following command : 

```
pip install pandas
```

This is currently the only package required in order to make CrowsPairsTools work. To check if everything works as intended, you can simply run the following commands : 

```
python main.py --check
```

```
python main.py --apply
```

It will run the script on the example dataset, based on english (US) pairs.

# How to use
This tool was made to be as simple as possible when comes the moment to use it. You only need to have a CrowS-Pairs-like corpus and to specify your language's **IETF BCP 47** tag (you can find it [here]( https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a). For instance : 

- **CrowsPairs_exemple.csv** - a CrowS-Pairs-like dataset with english (US) and french pairs.
- **fr_FR** - this is the french language's **IETF BCP 47** tag.

You have to put your **CrowsPairs_exemple.csv** in the **data** folder. Then, from the **CrowsPairsTools** folder, run this command :

```
python main.py --check --data CrowsPairs_exemple.csv -l fr_FR
```

This command will check all the columns of your corpus with **fr_FR** in their name. You MUST at least have a **'sent_more_fr_FR'** and a **'sent_less_fr_FR'** column in order for the script to work. Do not forget to put **'id'** as the fist column header too. This command will generate a **fr_FR** folder in the **output** folder. 

This **fr_FR** folder contains two csv files : one containing every non minimal pairs the script found (**CrowsPairs_exemple_nonMinimal.csv**) and the other containing for each pair the problematic terms/words that differ from one sentence to the other (**CrowsPairs_exemple_changes.csv**).

At this point, you might want to manually correct each problematic pair in **CrowsPairs_exemple_nonMinimal.csv**. Once this is done, you can run the following command :

```
python main.py --apply --data CrowsPairs_exemple.csv -l fr_FR
```

It will create a new file (**CrowsPairs_fr_FR_corrected.csv**) in the **output/corrected/** folder, containing your corpus with every corrections.

## Available parameters
Here are all the parameters you can use with this script :

- **--check** : main task. Retrieve non minimal pairs from your dataset.
- **--apply** : main task. Save your corrections and create a well formed CrowS-Pairs-like dataset.
- **--data** : path to your CrowS-Pairs-like dataset. **Mandatory**.
- **-d** or **--delimiter** : separator character in your csv file. '\t' (tab) by default.
- **-l** or **--language** : language to base your analysis on. **Mandatory**.

## Equivalent words
A lot of pairs will be indicated as non minimal by the script whereas they are in fact minimal. This is because, depending on the language you are using, some words are affected by gender. In order to bypass those false non minimal pairs, you can go to **utils/equivalents/** and find a txt file with your language's tag (**fr_FR.txt**). In this file, you can create rules to indicate words that are more or less 'equivalents'. For instance, **'il'** and **'elle'** only differ because of gender in french. By writting a line with **'elle,il'** in **fr_FR.txt**, you indicate that every **'elle'** encountered is equivalent to **'il'**. Those equivalent rules are only applied while analyzing your dataset and DOES NOT MODIFY your dataset in any way. 

The goal with those sets of rule was to reduce the number of non minimal pairs found by the script, in order to make the correction processus shorter and easier. I could have used a lemmatizer instead of this, but it seemed to be a bit too much, considering that the pairs are already almost all minimal.
