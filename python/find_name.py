import pandas as pd
import json

# Load the CSV file into a DataFrame
csv_file_path_modif = r'rocketguns_json\lang\lang.vromfs.bin_u\lang\units_modifications.csv'
df = pd.read_csv(csv_file_path_modif, on_bad_lines='skip', delimiter=';')

csv_file_path = r'rocketguns_json\lang\lang.vromfs.bin_u\lang\units.csv'
du = pd.read_csv(csv_file_path, on_bad_lines='skip', delimiter=';')

file_path_weaponry = r'rocketguns_json\lang\lang.vromfs.bin_u\lang\units_weaponry.csv'
dw = pd.read_csv(file_path_weaponry, on_bad_lines='skip', delimiter=';')

# Update the DataFrame with the JSON values where the name matches
def find_sensor_name(file_name):
    key = 'sensors/'+file_name
    if key in df.iloc[:, 0].values:
        row_index = df.index[df.iloc[:, 0] == key].tolist()[0]
        string_in_first_language = df.iloc[row_index, 1]
        return(string_in_first_language. encode('ascii', 'ignore').decode('ascii'))
    else: 
        return None

def find_unit_name(file_name):
    key = file_name + '_shop'
    if key in du.iloc[:, 0].values:
        row_index = du.index[du.iloc[:, 0] == key].tolist()[0]
        string_in_first_language = du.iloc[row_index, 1]
        return(string_in_first_language. encode('ascii', 'ignore').decode('ascii') if not isinstance(string_in_first_language, float) else file_name)
    else: 
        return file_name

def find_weapon_name(file_name):
    key = 'weapons/' + file_name + '/short'
    if key in dw.iloc[:, 0].values:
        row_index = dw.index[dw.iloc[:, 0] == key].tolist()[0]
        string_in_first_language = dw.iloc[row_index, 1]
        return(string_in_first_language. encode('ascii', 'ignore').decode('ascii'))
    else: 
        return file_name

# Save the updated DataFrame back to a new CSV file

if __name__ == "__main__":
    print(find_weapon_name('cn_pl12'))
