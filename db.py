import sqlite3
import datetime

def initialize_tables(cur):
    conn = cur.cursor()
    try:
        conn.execute('''
            DROP TABLE WORKERS;
        ''')
    except:
        pass
    try:
        conn.execute('''
            DROP TABLE SUBDIVISIONS;
        ''')
    except:
        pass
    try:
        conn.execute('''
            DROP TABLE ORDERS;
        ''')
    except:
        pass


    conn.execute('''
        CREATE TABLE WORKERS(
                ID INTEGER PRIMARY KEY   AUTOINCREMENT   NOT NULL,
                FULLNAME       TEXT     NOT NULL,
                POSITION       TEXT     NOT NULL,
                SUBDIVISION    TEXT     NOT NULL,
                SALARY         INT      NOT NULL
                );
    ''')
    conn.execute('''
        CREATE TABLE SUBDIVISIONS(
                ID INTEGER PRIMARY  KEY   AUTOINCREMENT   NOT NULL,
                TITLE           TEXT     NOT NULL,
                POSITIONS       TEXT     NOT NULL,
                UNITSIZE        INT      NOT NULL
                );
    ''')
    conn.execute('''
        CREATE TABLE ORDERS(
                ID INTEGER PRIMARY KEY   AUTOINCREMENT   NOT NULL,
                TITLE          TEXT     NOT NULL,
                TYPE           TEXT     NOT NULL,
                TEXT           TEXT     NOT NULL,
                DATE           DATE     NOT NULL
                );
    ''')
    

    conn.execute('''
        INSERT INTO WORKERS (ID,FULLNAME,POSITION,SUBDIVISION,SALARY) VALUES (1,'Smirnov Alexander','Engineer','Technical Department',18680);
    ''')
    conn.execute('''
        INSERT INTO WORKERS (ID,FULLNAME,POSITION,SUBDIVISION,SALARY) VALUES (2,'Gotie Alan','Team-Lead','Development Department',23120);
    ''')
    conn.execute('''
        INSERT INTO WORKERS (ID,FULLNAME,POSITION,SUBDIVISION,SALARY) VALUES (3,'Meril Andrea','Marketer','Sales Department',13660);
    ''')
    conn.execute('''
        INSERT INTO WORKERS (ID,FULLNAME,POSITION,SUBDIVISION,SALARY) VALUES (4,'Anderson Paul','Web-developer','Development Department',15500);
    ''')
    conn.execute('''
        INSERT INTO WORKERS (ID,FULLNAME,POSITION,SUBDIVISION,SALARY) VALUES (5,'Leclerk Anna','Consultant','Sales Department',10700);
    ''')
    conn.execute('''
        INSERT INTO WORKERS (ID,FULLNAME,POSITION,SUBDIVISION,SALARY) VALUES (6,'Sobraj Charles','Accountant','Sales Department',16900);
    ''')


    conn.execute('''
        INSERT INTO SUBDIVISIONS (ID,TITLE,POSITIONS,UNITSIZE) VALUES (1,'Technical Department','Tech. Assistant, Technician, Engineer',20);
    ''')
    conn.execute('''
        INSERT INTO SUBDIVISIONS (ID,TITLE,POSITIONS,UNITSIZE) VALUES (2,'Development Department','Web-developer, Team-Lead, DevOps',35);
    ''')
    conn.execute('''
        INSERT INTO SUBDIVISIONS (ID,TITLE,POSITIONS,UNITSIZE) VALUES (3,'Sales Department','Marketer, Consultant, Accountant',55);
    ''')


    conn.execute('''
        INSERT INTO ORDERS (ID,TITLE,TYPE,TEXT,DATE) VALUES (1,'Transfer order', 'Transfer', 'Alan Gotie is transfered to Development Department as Team-Lead for good and qualitative work', '2021/04/09');
    ''')
    conn.execute('''
        INSERT INTO ORDERS (ID,TITLE,TYPE,TEXT,DATE) VALUES (2,'Dismissal order', 'Dismissal', 'Sahar Musal is fired for his bad attitude and non-proffesionalism', '2020/06/21');
    ''')
    conn.execute('''
        INSERT INTO ORDERS (ID,TITLE,TYPE,TEXT,DATE) VALUES (3,'Hiring order', 'Hiring','Charles Sobraj is hired for us to perform work', '2021/05/19');
    ''')
    cur.commit()
     

class DB():
    def get_orders(self, conn):
        result = []
        for line in conn.execute('''
            SELECT ID,TITLE,TYPE,TEXT,DATE FROM ORDERS;
        '''):
            result.append(line)
        return result

    def get_order(self, conn, ids):
        result = []
        for line in conn.execute(f'''
            SELECT ID,TITLE,TYPE,TEXT,DATE FROM ORDERS WHERE ID={ids};
        '''):
            result.append(line)
        return result

    def get_all_workers(self, conn):
        result = []
        for line in conn.execute('''
            SELECT FULLNAME,POSITION,SUBDIVISION,SALARY FROM WORKERS;
        '''):
            result.append(line)
        return result

    def get_all_subdivisions(self, conn):
        result = []
        for line in conn.execute('''
            SELECT TITLE,POSITIONS,UNITSIZE FROM SUBDIVISIONS;
        '''):
            result.append(line)
        return result

    def get_subdivision_by_name(self, conn, subdivision):
        result = []
        for line in conn.execute(f'''
            SELECT TITLE,POSITIONS,UNITSIZE FROM SUBDIVISIONS WHERE TITLE='{subdivision}';
        '''):
            result.append(line)
        return result
    
    def get_subdivision_positions(self, conn, title):
        result = []
        for line in conn.execute(f'''
            SELECT POSITIONS FROM SUBDIVISIONS WHERE TITLE='{title}';
        '''):
            result.append(line)
        return result

    def get_worker_by_name(self, conn, fullname):
        return conn.execute(f'''
            SELECT FULLNAME,POSITION,SUBDIVISION,SALARY FROM WORKERS WHERE FULLNAME='{fullname}';
        ''')

    def get_workers_by_department(self, conn, subdivision):
        result = []
        for line in conn.execute(f'''
            SELECT FULLNAME,POSITION,SUBDIVISION,SALARY FROM WORKERS WHERE SUBDIVISION='{subdivision}';
        '''):
            result.append(line)
        return result


    def remove_subdivision_and_people(self, conn, subdivision):
        date = datetime.datetime.now().strftime('%Y\%m\%d')
        for person in self.get_workers_by_department(conn, subdivision):
            self.add_order(conn, 'Dismissal order', 'Dismissal', person[0] + ' was dismissed', date)
        conn.execute(f'''
                DELETE FROM WORKERS WHERE SUBDIVISION='{subdivision}';
            ''')
        conn.execute(f'''
            DELETE FROM SUBDIVISIONS WHERE TITLE='{subdivision}';
        ''')

    def remove_worker(self, conn, fullname):
        conn.execute(f'''
            DELETE FROM WORKERS WHERE FULLNAME='{fullname}';
        ''')


    def update_worker(self, conn, fullname, newname, newposition, subdivision, salary):
        
        conn.execute(f'''
            UPDATE WORKERS SET FULLNAME='{newname}', POSITION='{newposition}', SUBDIVISION='{subdivision}', SALARY={salary} WHERE FULLNAME = '{fullname}';
        ''')

    def update_subdivisions(self, conn, subdivision, newsubdivisiontitle, newpositions, newunitsize):
        date = datetime.datetime.now().strftime('%Y\%m\%d')
        conn.execute('''
            UPDATE SUBDIVISIONS SET TITLE=?, POSITIONS=?, UNITSIZE=? WHERE TITLE=?;
        ''', (newsubdivisiontitle, newpositions, newunitsize, subdivision))
        for person in self.get_workers_by_department(conn, subdivision):
            self.add_order(conn, 'Transfer order', 'Transfer', person[0] + ' was transferred to ' + newsubdivisiontitle, date)
            self.update_worker(conn, person[0], person[0], person[1], newsubdivisiontitle, person[3])


    def add_worker(self, conn, fullname, position, subdivision, salary):
        conn.execute(f'''
            INSERT INTO WORKERS (FULLNAME,POSITION,SUBDIVISION,SALARY) VALUES ('{fullname}','{position}','{subdivision}',{salary});
        ''')
    
    def add_subdivision(self, conn, title, positions, unitsize):
        conn.execute(f'''
            INSERT INTO SUBDIVISIONS (TITLE,POSITIONS,UNITSIZE) VALUES ('{title}','{positions}',{unitsize});
        ''')

    def add_order(self, conn, title, type, text, date):
        conn.execute(f'''
            INSERT INTO ORDERS (TITLE,TYPE,TEXT,DATE) VALUES ('{title}','{type}','{text}','{date}');
        ''')
    
    def update_positions_of_workers_in_subdivision(self, conn, subdivision, newpositions):
        date = datetime.datetime.now().strftime('%Y\%m\%d')
        positions = self.get_subdivision_positions(conn, subdivision)[0][0]
        print(positions)
        print(newpositions)
        if positions!=newpositions:
            for old, new in zip(positions.split(', '), newpositions.split(', ')):
                print(old)
                print(new)
                conn.execute(f'''
                    UPDATE WORKERS SET POSITION='{new}' WHERE POSITION = '{old}';
                ''')
                self.add_order(conn, 'Positions changed', 'Swapping ',  old + ' was changed to ' + new + ' in department ' + subdivision, date)
                
if __name__=='__main__':
    initialize_tables(sqlite3.connect('database.db'))
    

    