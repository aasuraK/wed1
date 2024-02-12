import os

file_pwd = os.getcwd()

file_path = '/Users/amoghnigam/Downloads/pathsetter/dashboard/input/processed_supermarket_sales 15:15:39.899084.csv'


output_file_name = "check_v1_" + file_path.split("/")[-1]

output_folder = os.path.join("output", output_file_name)

output_file_path = os.path.join(file_pwd, output_folder)



# print(file_path)