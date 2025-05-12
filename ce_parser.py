# a simple parser for CoreScan counterexample analysis

# %%
import re
import sys
import pprint
import json

nf_instances = ['consumer1', 'consumer2', 'producer1', 'producer2']
nf_instances_temp = ['consumer', 'producer']

# parameters to extract
nf_params = ['model_id', 'nfInstanceId', 'nfType', 'fqdn', 'plmns[1]', 'plmns[2]', 'sNssais[1]', 'sNssais[2]', 'allowedNFTypes[1]', 'allowedNFTypes[2]', 'allowedNFDomains[1]', 'allowedNFDomains[2]',  'allowedsNssais[1]', 'allowedsNssais[2]',  'allowedPlmns[1]', 'allowedPlmns[2]']
nf_service_params = ['serviceInstanceId', 'serviceName', 'fqdn', 'sNssais[1]', 'sNssais[2]', 'allowedNFTypes[1]', 'allowedNFTypes[2]', 'allowedNFDomains[1]', 'allowedNFDomains[2]',  'allowedsNssais[1]', 'allowedsNssais[2]',  'allowedPlmns[1]', 'allowedPlmns[2]']
model_params = ["roaming", "comType", "atrType", "crossProfileCheckRequired", "requesterInfoReq","isCCAEnabled"]
output = {}
config = {}

for nf in nf_instances_temp:
    output[nf] = {}
    # output[nf]['nfService'] = {}

for nf in nf_instances:
    output[nf] = {}
    output[nf]['nfService'] = {} 

# print(output)
filename = sys.argv[1]
# filename = "r1.txt"

input_file = f"{filename}"
with open(input_file, 'r') as file:
    content = file.read()
# content

# %%
def extract_info(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Define regex patterns to extract information
    consumer1_pattern = re.compile(r'consumer1\.nfInstanceId = (\d+)\n\s+consumer1\.nfType = (\w+)')
    consumer2_pattern = re.compile(r'consumer2\.nfInstanceId = (\d+)\n\s+consumer2\.nfType = (\w+)')
    producer1_pattern = re.compile(r'producer1\.nfInstanceId = (\d+)\n\s+producer1\.nfType = (\w+)')
    producer2_pattern = re.compile(r'producer2\.nfInstanceId = (\d+)\n\s+producer2\.nfType = (\w+)')

    # Extract information using regex patterns
    consumer1_match = consumer1_pattern.search(content)
    consumer2_match = consumer2_pattern.search(content)
    producer1_match = producer1_pattern.search(content)
    producer2_match = producer2_pattern.search(content)

    # Write extracted information to extracted_config.txt
    with open('extracted_config.txt', 'w') as output_file:
        output_file.write("Consumer 1:\n")
        if consumer1_match:
            output_file.write(f"First Occurrence: nfInstanceId = {consumer1_match.group(1)}, nfType = {consumer1_match.group(2)}\n")
        else:
            output_file.write("First Occurrence not found\n")

        output_file.write("\nConsumer 2:\n")
        if consumer2_match:
            output_file.write(f"First Occurrence: nfInstanceId = {consumer2_match.group(1)}, nfType = {consumer2_match.group(2)}\n")
        else:
            output_file.write("First Occurrence not found\n")

        output_file.write("\nProducer 1:\n")
        if producer1_match:
            output_file.write(f"First Occurrence: nfInstanceId = {producer1_match.group(1)}, nfType = {producer1_match.group(2)}\n")
        else:
            output_file.write("First Occurrence not found\n")

        output_file.write("\nProducer 2:\n")
        if producer2_match:
            output_file.write(f"First Occurrence: nfInstanceId = {producer2_match.group(1)}, nfType = {producer2_match.group(2)}\n")
        else:
            output_file.write("First Occurrence not found\n")

# %%
def extract(nf:str, param:str, is_service_level:bool, occurance:int, protocol_instance:str):
    # Define regex patterns to extract information
    service = ''
    if is_service_level:
        service = 'nfService1\.'
    protocol = ''
    if protocol_instance != '':
        protocol = f'{protocol_instance}\.'
    
    #fix escape for param
    param_for_pattern = param.replace('[', r'\[')

    pattern = re.compile( f'    {protocol}{nf}\.{service}{param_for_pattern} = ' + r'(\S+)')

    # Extract information using regex patterns
    matches = pattern.findall(content)
    # print(matches)

    if matches and len(matches) >= occurance: 
        if param.endswith(('[1]','[2]')):
            param = param[:-3]
            if is_service_level == False:
                if param not in output[nf]:
                    if matches[occurance-1] in ('0', 'none'):
                        output[nf][param] = []
                    else:
                        output[nf][param] = [matches[occurance-1]]
                else:
                    if matches[occurance-1] not in ('0', 'none'):
                        output[nf][param].append(matches[occurance-1])
            else:
                if param not in output[nf]['nfService']:
                    if matches[occurance-1] in ('0', 'none'):
                        output[nf]['nfService'][param] = []
                    else:
                        output[nf]['nfService'][param] = [matches[occurance-1]]
                else:
                    if matches[occurance-1] not in ('0', 'none'):
                        output[nf]['nfService'][param].append(matches[occurance-1])
        else:
            if is_service_level == False:
                output[nf][param] = matches[occurance-1]
            else:
                output[nf]['nfService'][param] = matches[occurance-1]


    # Write extracted information to extracted_config.txt
    # with open('extracted_config.txt', 'w') as output_file:
    #     output_file.write("Consumer 1:\n")
    #     if consumer1_match:
    #         output_file.write(f"First Occurrence: nfInstanceId = {consumer1_match.group(1)}, nfType = {consumer1_match.group(2)}\n")
    #     else:
    #         output_file.write("First Occurrence not found\n")
    
def extract_all(nf_instances:list, occurance:int, protocol_instance:str):
    for nf in nf_instances:
        for nf_param in nf_params:
            extract(nf, nf_param, False, occurance, protocol_instance)
        
        for nf_service_param in nf_service_params:
            extract(nf, nf_service_param, True, occurance, protocol_instance)

def extract_config():
    # Define regex patterns to extract information
    state_pattern = re.compile(r'-> State: (.+?) <-')
    param_pattern = re.compile(r's1\.modelParam\.(\w+) = (\S+)')
    # reqForSpecificProducer_pattern = re.compile(r'reqForSpecificProducer = (\S+)')

    # Split the configuration text into states
    states = state_pattern.split(content)[1:]
    # Extract information using regex patterns
    if len(states) < 2: 
        print("No counterexample found");
        exit(0)
    state = states[1]
    match_params = param_pattern.finditer(state)
    # match_reqFSP = reqForSpecificProducer_pattern.search(state)
    # if match_reqFSP:
    #     config['reqForSpecificProducer'] = match_reqFSP.group(1)

    config["model_param"] = {}
    for match_param in match_params: 
        if match_param.group(1) in model_params:
            config["model_param"][match_param.group(1)] = match_param.group(2)

if __name__ == "__main__":
    extract_all(nf_instances, 1, '')

    # extract_all(nf_instances_temp, 2, 's1')
    extract('consumer','model_id',False,2,'s1')
    extract('consumer','nfInstanceId',False,2,'s1')
    extract('producer','model_id',False,2,'s1')
    extract('producer','nfInstanceId',False,2,'s1')

    extract_config()
    pprint.pprint(config, sort_dicts=False)
    # print(output)
    print("-----------------------------------------------------")
    pprint.pprint(output, sort_dicts=False)
    # print(json.dumps(output, indent=4))



