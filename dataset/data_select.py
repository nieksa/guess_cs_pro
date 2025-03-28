import json

# Path to your JSON file
input_file = r'C:\Users\lixuy\Desktop\csguess\dataset\pro_info.json'
output_file = r'C:\Users\lixuy\Desktop\csguess\processed_pro_info2.json'

# Load the existing data
with open(input_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Process each item in the data
for entry in data:
    # Remove the 'result' field from 'team', 'age', 'majorAppearances', and 'role'
    if 'team' in entry and 'result' in entry['team']:
        del entry['team']['result']
    
    if 'age' in entry and 'result' in entry['age']:
        del entry['age']['result']
    
    if 'majorAppearances' in entry and 'result' in entry['majorAppearances']:
        del entry['majorAppearances']['result']
    
    if 'role' in entry and 'result' in entry['role']:
        del entry['role']['result']
    
    # Remove the 'isSuccess' field
    if 'isSuccess' in entry:
        del entry['isSuccess']

# Write the updated data to a new file
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"数据已处理并保存到 {output_file}")
