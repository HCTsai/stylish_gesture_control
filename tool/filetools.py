'''
Created on 2021年5月3日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
def list_to_file(data_list,cols=[], delimiter = ",", out_file = "outfile.txt"):
    with open(out_file,"w",encoding="utf-8") as f:        
        for row in data_list : 
            line = ""
            if len(cols) == 0 :
                line = delimiter.join(row)
            else :
                c_list = []
                for c in cols :
                    c_list.append(row[c])
                line = delimiter.join(c_list)
                if c_list[-1] == "" :
                    print (row)
                    print (line)            
            f.write(line+"\n")
            
def file_to_list(file_path, delimiter = ",", ignore="#"):
    res = []
    with open(file_path,"r",encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines :
            if not line.startswith(ignore) :
                data_list = line.strip().split(sep=delimiter)
                res.append(data_list)
    return res
