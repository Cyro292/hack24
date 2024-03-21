import json

def merge_json(themen_data_file, contact_data_file):
    
    # Load the first JSON file
    with open(themen_data_file, 'r', encoding='utf-8') as file:
        themen_data = json.load(file)

    # Load the second JSON file
    with open(contact_data_file, 'r', encoding='utf-8') as file:
        contact_data = json.load(file)
    
    for category, subtopics in list(themen_data.items()):
        
        # The main category has contact information
        if category in contact_data:
            
            # iterate through all the subtopics
            for subtopic_key, subtopic_value in list(subtopics.items()):
                print(subtopic_key, subtopic_value)
                
                # The subtopic is a dictionary and is a category name
                if isinstance(subtopic_value, dict) and subtopic_key in contact_data[category]:
                    # Merge the contact information into the subtopic dictionary
                    themen_data[category][subtopic_key]['contact'] = contact_data[category][subtopic_key]
                
                # THe subtopic is not a category name and not a URL
                elif subtopic_key != 'URL':
                    # Handle nested subtopics
                    for nested_key, nested_value in list(subtopic_value.items()):
                        if isinstance(nested_value, dict) and nested_key in contact_data.get(category, {}):
                            themen_data[category][subtopic_key][nested_key]['contact'] = contact_data[category][nested_key]
            
            # If the main topic itself has contact information but no subtopics
            themen_data[category]['category-contact'] = contact_data[category]
                    
    return themen_data

# Example usage
combined_json = merge_json('themen_url_data.json', 'contact_info.json')

# Save the combined JSON to a file
with open('ubersicht.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(combined_json, indent=4, ensure_ascii=False))