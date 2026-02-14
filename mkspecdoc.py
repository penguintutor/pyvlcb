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
        f.write("# VLCB protocol specification\n\n")
        
        f.write("Details of the VLCB specification as implemented within PyVLCB library\n\n")
        
        f.write("## Opcode table\n\n")
        
        for code, details in VLCBOpcode.opcodes.items():
            # Create Table Header
            opcode_int = int(code, 16)
            f.write(f"| OpCode | Hex: {code} Decimal {opcode_int} |\n")
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

if __name__ == "__main__":
    main()
    print(f"Successfully saved to {filename}")