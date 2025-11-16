Automation Sequence


Event driven

For each rule when triggered it calls event_bus with details of the event, which 
broadcasts the event.


Pre - get loco details (perhaps 1 use in MW - if more then need to add later)
Locos are known as Loco1, Loco2, Loco3 (max 5 in current design)
When starting then ask user to select corresponding locos
Note sequence will assume certain locos start in certain places as unable to detect which loco triggers which sensor
(unless advanced train detection in use)
Each rule also includes location information which can be used to position (perhaps an image)



Each sequence runs sequentially, but multiple sequences cn be started at the same time 
perhaps from a single click of a button. This will be defined within the automation file which will define the 
triggers and the sequences.



Example - Move Loco to shed


Start

Set Loco function (activate sound)
Set Loco speed

- Wait until input changes (eg. CBUS Event input)

Switch point

- Wait on next sensor

- Wait on input change

Set Loco speed (perhaps have this as a subsequence??)
- Wait 0.5 seconds
Set Loco speed
- Wait 0.5 seconds
Stop loco

- Wait 1 second 

Reverse loco direction
Set Loco Speed

- Wait on next sensor

Set loco speed 

- Wait 1 second

Stop Loco



Also need if / else

Also handle loops

Also feedback to the operator (eg. if a sequence fails after x attempts)

To handle multiple events then include them in a sequence - eg. subsequence / sequence calling a sequence
if a sequence uses locos then they inherit the same locos. If an unrelated sequence needs locos then will 
request those separately.

It is normally only locos that can be assigned dynamically, assumed that points will not physically reposition, 
whereas Locos can be swapped out as required


Include variables (these are like an event where you can query). Rather than wait on sensor can query it's state and 
keep running. This would be similar to have multiple processes.

Can also make use of variables within a Rule - these are stored in the appropriate value fields as ${varname}

sequence includes Labels. These are skipped over, but can be used for loops (goto loop). Loops should really only move backwards (avoid 
jump forward to avoid risk of spagetti code), although not enforced. Still possible to make the rules difficult to follow so should be used with care
Ideally prefix loop with : but not required

Where a rule performs a condition check (eg Jump) then it needs "test": "equals" "==" or "lessthan" "<" or "greaterthan" ">", or 
"notequals" "!=" or "<=" or ">=" (no long version of those) 

Can only jump within the current sequence. Can break to exit the current sequence back to the upper level (or if top then 
stop sequence).

"wait" can wait on condition or time waittype = delay (default) or waittype = condition, time defaults to 1 second if not configured otherwise
this applies with the condition as it forms a delay until the condition is checked.
# This is different to the timer (if that is added) as this is done through time.sleep and should only be run if on a thread / threadpool

# There is an optional maxloop value which can be used to exit the wait if the condition is never met. In which case run maxloop number of delays
then end the wait. maxloop should be an absolute value rather than a variable.







