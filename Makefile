# Install nuXmv from https://nuxmv.fbk.eu/download.html and add it to path
# Then run this make file

# Uncomment the model component to run

SMV = AC-barebone
# SMV = AC-nfdomain
# SMV = AC-slicing
# SMV = AC-roaming
# SMV = AC-indirect
# SMV = AC-other

# Mention the property to test. Only properties that the model violates will produce counterexamples.
# test the following sample counterexample generating property with AC-barebone
# PROP = raise_ce

ifndef PROP
	PROP = no_ce
endif

# define trace depth; for CoreScan 30 is sufficient to find all attacks
depth = 30

ifndef depth
	depth := 40
endif

script := "read_model -i $(SMV).smv" # read model
script += "go_bmc" # flatten hierarcy and build model and variable ordering
script += "check_ltlspec_bmc -k $(depth) -P \"$(PROP)\"" #check ltl property named PROP
script += "quit"

all:
	$(info Modelchecking $(SMV).smv)
	mkdir -p $(SMV)
	@printf "%s\\n" $(script) > script.txt
	nuXmv -v 0 -source script.txt > $(SMV)/$(PROP).txt
	$(info nuXmv output is at $(PROP).txt)
	# make sure call are imported python packages ce_parser is available
	python3 ce_parser.py $(SMV)/$(PROP).txt > $(SMV)/$(PROP)_config.txt 
	# nf_config helps analyze the counterexample configuration quickly to facilitate root cause analysis
	$(info nf_config of the counterexample available at $(PROP)_config.txt)

clean:
	# @rm -rf script.txt $(PROP).txt $(PROP)_config.txt