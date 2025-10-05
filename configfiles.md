# Config files

If any of the files are missing then displays empty data or similar

## data/

settings.json 
* General settings

yards.json
* List of yards (if none display all locos)

locos.json
* List of all locos
* Includes enable option for ones currently showed

layouts.json
* List of what layouts available

rules.json
* List of sets of automation rules
* Can be associated with layout (in future)
* or individual ruleset added like locos.json

## data/locos/
&lt;loconame&gt;.json
&lt;loconame&gt;.png  
* typically called this, but name is from the .json file

## data/layouts/
&lt;layoutname&gt;-track.png 
* image showing layout
&lt;layoutname&gt;-objects.json
* objects to display

## data/yards/
&lt;yardname&gt;.json

## data/rules/
&lt;rulename&gt;.json