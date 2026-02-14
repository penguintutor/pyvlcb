from pyvlcb import VLCBOpcode

filename = 'docs/spec.md'

# Translate key into friendly names (eg. apropriate caps)
key_lookup = {
    'opc': 'Name',
    'title': 'Title',
    'format': 'Args / data',
    'minpri': 'Priority',
    'comment': 'Description'
    }
    

def main():
    with open(filename, "w") as f:
        
        ## Title and introduction
        f.write("# VLCB protocol specification\n\n")
        f.write("Details of the VLCB specification as implemented within the PyVLCB library\n\n")
        f.write("This is intended as an overview only, where the specification differs from the official VLCB standards, then the VLCB documentation should take precedent.\n\n")
        
        ## OpCodes
        f.write("## VLCB Opcodes\n\n")
        f.write("These are the opcodes listed in the VLCBOpcode.opcodes dictionary.\n\n")
        for code, details in VLCBOpcode.opcodes.items():
            # Create Table Header
            opcode_int = int(code, 16)
            f.write(f"| OpCode | '{code}' ({opcode_int}) |\n")
            f.write("| :--- | :--- |\n")
            
            # Create rows for each key-value pair in the inner dict
            for key, value in details.items():
                # If in lookup swap the text to more user friendly
                key_string = key_lookup.get(key, key)
                # Clean up empty values for better display
                display_value = value if value != '' else "*None*"
                f.write(f"| {key_string} | {display_value} |\n")
            
            # Add spacing between tables
            f.write("\n---\n\n")
            
        # DCC Error codes
        f.write("## DCC Error codes\n\n")
        f.write("These are the DCC error codes listed in the VLCBOpcode.dcc_error_codes dictionary.\n\n")
        f.write(f"| Error code | Description |\n")
        f.write("| :--- | :--- |\n")
        for code, details in VLCBOpcode.dcc_error_codes.items():
            # Create Table Header
            code_int = int(code, 16)
            f.write(f"| '{code}' ({code_int}) | {details} |\n")
        f.write("\n---\n\n")
            
        # CMDERR / GRSP Error codes
        f.write("## CMDERR / GRSP Error codes\n\n")
        f.write("These are the CMDERR / GRSP error codes listed in the VLCBOpcode.grsp_error_codes dictionary.\n\n")
        f.write(f"| Error code | Description |\n")
        f.write("| :--- | :--- |\n")
        for code, details in VLCBOpcode.grsp_error_codes.items():
            # Create Table Header
            code_int = int(code, 16)
            f.write(f"| '{code}' ({code_int}) | {details} |\n")
        f.write("\n---\n\n")
            


if __name__ == "__main__":
    main()
    print(f"Successfully saved to {filename}")