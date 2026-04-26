import os,ast,re



def read_file(filename):
    with open(rf"{filename}",'r',encoding='utf-8') as file:
        content=file.read()
        file.close()
    return content


def readlines_file(filename):
    with open(rf"{filename}",'r',encoding='utf-8') as file:
        content=file.readlines()
        file.close()
    return content


def writelines_file(filename,line):
    with open(rf"{filename}",'a+',encoding='utf-8') as file:
        file.write(line)
    file.close()
    
def exists_delete(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def tr_prictur_path(line):
    global last_num
    # print(last_num)
    line=repr(line)
    # print(line)
    complie_text=re.compile(r'typora-user-images\\\\(\d+\.png)')
    pictur_file_name=re.search(complie_text,line)
    if pictur_file_name!=None:
        pictur_file_name=pictur_file_name[1]
        # print(pictur_file_name[1])
        base_picturs=os.listdir(pictur_base_path)
        if pictur_file_name in base_picturs:
            picture_path=pictur_base_path+pictur_file_name
            last_num+=1
            new_pictur_name=str(last_num)+".png"
            new_picture_path=destetion_pictur_path+new_pictur_name
            # print(new_pictur_name)


            os.rename(picture_path,new_picture_path)

            line1=re.sub(r'(\[\d+\])',"[]",line)
            line2=re.sub(r'\(.+\)',f'(../picturs/{new_pictur_name})',line1)
            # print(line2)
            writelines_file(tmp_file_path,ast.literal_eval(line2))
    


    else:
        line=ast.literal_eval(line)
        writelines_file(tmp_file_path,line)
    
def clear_directory(dir_path):
    """
    清空指定目录下的所有文件和子目录，保留目录本身。
    如果目录为空，则不做任何操作。
    """
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"路径不存在或不是目录: {dir_path}")

    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)          # 删除文件或符号链接
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)      # 递归删除子目录
        except Exception as e:
            print(f"删除失败 {item_path}: {e}")

# print(len(already_num))
if __name__=="__main__":
    
    destetion_pictur_path=r"C:\Users\16531\Desktop\selenium-learning\picturs\\"
    pictur_base_path=r"C:\\Users\\16531\\AppData\\Roaming\\Typora\\typora-user-images\\"
    text_name_path=input("请给我需要处理文件的绝对路径：")
    # text_name_path=text_name_path[1:-2]
    text_name_path=text_name_path.split('"')[1]
    # print(text_name_path)
    tmp_file_path=r"C:\Users\16531\Desktop\selenium-learning\topics\new.md"
    picturs=os.listdir(r"C:\Users\16531\Desktop\selenium-learning\picturs")
    if picturs!=[]:
        last_picturs_id=int(os.listdir(r"C:\Users\16531\Desktop\selenium-learning\picturs")[-1].split('.')[0])
    else:
        last_picturs_id=0




    content=read_file(text_name_path)
    already_num=re.findall(r'picturs/(\d+)\.png',content)
    exists_delete(tmp_file_path)


    if len(already_num)!=0:
        if int(already_num[-1])<last_picturs_id:
            last_num=int(last_picturs_id)
            lines=readlines_file(text_name_path)
            for line in lines:
                tr_prictur_path(line)
            # print(last_num)
        else:
            last_num=int(already_num[-1])
            lines=readlines_file(text_name_path)
            for line in lines:
                tr_prictur_path(line)

    elif len(already_num)==0:
        if os.listdir(destetion_pictur_path)!=[]:
            last_num=int(str(os.listdir(destetion_pictur_path)[-1]).split('.')[0])
        else:
            last_num=0
        lines=readlines_file(text_name_path)
        for line in lines:
            tr_prictur_path(line)
            

    else:
        print('no')
    os.remove(text_name_path)
    os.rename(tmp_file_path,text_name_path)
    clear_directory(r"C:\\Users\\16531\\AppData\\Roaming\\Typora\\typora-user-images")
    clear_directory(r"C:\\Users\\16531\\Pictures\\PixPinAutoSave")
        #直接给项目路径，然后完整便利出*.md文件，结合当前日期，是则进行修改排查。


