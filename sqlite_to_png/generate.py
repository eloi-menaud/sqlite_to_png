import re
import os
import pydot



class Row:
    name=""
    type_=""
    NOTNULL=False
    UNIQUE=False
    PRIMARYKEY=False
    DEFAULT=""
    
    def __str__(self):
        r = self.name
        r += "\n  " + self.type_
        r += "\n  UNIQUE" if self.UNIQUE else ""
        r += "\n  NOT NULL" if self.NOTNULL else ""
        r += "\n  DEFAULT " + self.DEFAULT if self.DEFAULT else ""
        r+="\n"
        return r

class Graph:
    foreignKey = []
    tables = [] 
    title = ""
    def toDot(self):
        r = "digraph " + self.title + "{\n"
        print("------------------------------------------")
        for table in self.tables :
            r+=table
        r += "splines=spline\nnodesep=3\nedge [dir=none]"
        for fk in self.foreignKey:
            r += fk + "\n"
        r += "}"
        return r

class Table:
    rows= [] #list of rows
    name= ""
    pks=[]
    def __init__(self):
        self.rows = []
        self.name = ""

    def toDot(self):
        r = f'{self.name} [\n'
        r+= 'shape=plain\n'
        r+= 'label=<\n'
        r+= '<table border="0" cellborder="1" cellspacing="0" cellpadding="4">\n'
        r+= f'<tr> <td> <b>{self.name}</b> </td> </tr>'
        r+= '<tr><td>\n'
        r+= '<table border="0" cellborder="" cellspacing="0" >\n'
        
        for i in range(len(self.rows)):
            r += "<tr> <td> </td> </tr>\n" if (i > 0) else ""
            r += self.rows[i] + "\n"
        
        r += "</table>\n"
        r+= "</td> </tr>\n"
        r+="</table>"
        r+=">\n"
        r+="]\n"

        return r



def generate():
    db = ""
    with open("db.sql","r") as file :
        db = file.read()


        def toDot(self):
            r = ''
            r += f'\t<tr><td align="left" port="{self.name.replace("* ","")}"><b>{self.name}</b></td> </tr>\n'
            r += f'\t<tr><td align="left">{self.type_}</td> </tr>\n'
            r += f'\t<tr><td align="left">UNIQUE</td></tr>\n' if self.UNIQUE else ""
            r += f'\t<tr><td align="left">NOT NULL</td></tr>\n' if self.NOTNULL else ""
            r += f'\t<tr><td align="left">DEFAULT : {self.DEFAULT}</td></tr>\n' if self.DEFAULT else ""
            return r



    # clean comments
    db = re.sub("--[\s^\n]*.+", '', db) # remove commentaires --
    db = re.sub("#[\s^\n]*.+", '', db) # remove commentaires #
    db = re.sub("\/\*(.|\n)*\*\/", '', db) # remove commentaires #
    db = re.sub("IF NOT EXISTS ", '', db)

    # get table
    tables = re.findall('CREATE TABLE [^;]+',db)


    graph = Graph()
    graph.title = "titre"


    for t in tables :
        table = Table()

        # name stuff
        datas = ""
        try:
            table.name,datas = re.findall("^CREATE TABLE (\w+)\s*\s*\(([^;]*)\)",t)[0]
        except ValueError:
            print(f"Can't parse {t} to find table name and rows definition : \n")
        
        # primary Key stuff
        for pk_datas in re.findall('PRIMARY KEY\s+\([^)]+\),', datas):
            datas = datas.replace(pk_datas,"")
            pks = re.findall("\(([^)])",pk_datas)[0].replace(" ","").split(',')
            for pk in pks:
                table.pks.append(pk)
        # foreignKey stuff
        for fk_datas in re.findall('FOREIGN KEY\s*\(([\w, ]*)\)\s*REFERENCES\s+(\w+)\s*\(([\w, ]+)\)[^,]*', datas) :
            datas = re.sub('FOREIGN KEY\s*\([\w, ]*\)\s*REFERENCES\s+\w+\s*\([\w, ]+\)[^,]*','',datas)
            try:
                fks_str,destTable,refKey_str = fk_datas
            except Exception as e:
                print(f"Can't parse {t}, c'ant find foreign key \n" + "   need match : FOREIGN KEY\s*\(([\w,]*)\)\s*REFERENCES\s+(\w+)\s*\(([\w]+)\)\n" + "   where ([\w,]*) (\w+) ([\w]+) are groups of foreign keys, referenced talbe, referenced keys\n")
            
            fks = re.sub('\s*','',fks_str).replace("* ","").split(',')
            destKeys = re.sub('\s*','',refKey_str).split(',')

            if(len(fks) != len(destKeys)):
                print(f"Can't parse foreign key ({fks}) : {len(fks)} foreign key but {len(destKeys)} referenced keys")
            for i in range(len(destKeys)) :
                graph.foreignKey.append((f"{table.name}:{fks[i]} -> {destTable}:{destKeys[i]}"))   

        # key stuff    
        rows = datas.replace('\n','').split(",")
        rows = [re.sub('^[\s]*','',row) for row in rows]
        for row in rows:
            r = Row()
            row_datas = re.findall('\w+',row)
            if(not row_datas):
                break
            r.name = row_datas[0]
            r.type_ = row_datas[1]
            r.NOTNULL = ("NOT NULL" in row)
            if (("PRIMARY KEY" in row) or (r.name in table.pks)) :
                r.name = "* " + r.name 
                r.PRIMARYKEY = "* " + r.name

            r.UNIQUE = ("UNIQUE" in row) 
            
            if( "DEFAULT" in row ):
                if(r.type_ == "TEXT"): #if TEXT : take spaces "foo foo" and need to catch also "start'quote'last"
                    if(len(default := re.findall('DEFAULT\s*"(.*)"\s*',row)) == 1):
                        r.DEFAULT = default[0]
                        
                    elif(len(default := re.findall("DEFAULT\s*'(.*)'\s*",row))== 1):
                        r.DEFAULT = default[0]
                    else :
                        print(f"Parsing error : Can't find the DEFAULT vaule of type TEXT in row -> {row}")
                else:
                    if(len(default := re.findall('DEFAULT\s*([0-9.]*)',row)) == 1):
                        r.DEFAULT = default[0]
                    else:
                        print(f"Parsing error : Can't find the DEFAULT vaule of type {r.type_} in row -> {row}")
            table.rows.append(r.toDot()) 
            
        graph.tables.append(table.toDot())
        


    graphs = pydot.graph_from_dot_data(graph.toDot())
    graphs[0].write_png('graph.png')



