import psycopg2

import instruments.database as idB

def create_tables():

    schema = """
    CREATE TABLE sm_bookmarks
    (
        bookmark_id SERIAL PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        owner INTEGER,
        timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX url on sm_bookmarks(url);
    CREATE INDEX owner on sm_bookmarks(owner);

    CREATE TABLE sm_projects
    (
        project_id SERIAL PRIMARY KEY,
        project_name TEXT NOT NULL,
        project_owner INTEGER
    );
    CREATE INDEX project_name on sm_projects(project_name);
    CREATE INDEX project_owner on sm_projects(project_owner);

    CREATE TABLE sm_project_bookmarks
    (
        project_id INTEGER NOT NULL,
        bookmark_id INTEGER NOT NULL,
        PRIMARY KEY (project_id, bookmark_id)
    );"""

    idB.execute_query(schema)
    
    
def tables_created():
    
    query = """
    SELECT relname FROM pg_class 
    WHERE relname = 'sm_bookmarks'
    OR relname = 'sm_projects'
    OR relname = 'sm_project_bookmarks';
    """
    
    result = idB.execute_query(query)
    
    if result:
        return True
        
    return False
        

def save_bookmark(url, title, project=None):
    query = """INSERT INTO sm_bookmarks (url, title, owner) VALUES (%s, %s, %s) RETURNING bookmark_id;"""
    
    bookmark_id = idB.execute_query(query, (url, title, 1))
    
    if project:
        query = """INSERT INTO sm_project_bookmarks VALUES(%s,%s) RETURNING project_id;"""
        idB.execute_query(query, (project, bookmark_id))
        
    return bookmark_id
    
    
def update_bookmark(bookmark_id, title, url):
    query = """UPDATE sm_bookmarks SET url=%s, title=%s WHERE bookmark_id=%s;"""
    idB.execute_query(query, (url, title, bookmark_id))
    
    return bookmark_id
    
    
def move_bookmark(bookmark_id, project_id):
    query = """DELETE FROM sm_project_bookmarks WHERE bookmark_id=%s;"""
    idB.execute_query(query, (bookmark_id,))
    
    if project_id != 0:
        query = """INSERT INTO sm_project_bookmarks VALUES(%s, %s);"""
        idB.execute_query(query, (project_id, bookmark_id))
    
    
def delete_bookmark(bookmark_id):
    query = """DELETE FROM sm_bookmarks WHERE bookmark_id=%s;"""
    idB.execute_query(query, (bookmark_id,))
    
    query = """DELETE FROM sm_project_bookmarks WHERE bookmark_id=%s;"""
    idB.execute_query(query, (bookmark_id,))
    
    
def get_recent_bookmarks(page=0):
    BOOKMARKS_PER_PAGE = 25
    
    offset = BOOKMARKS_PER_PAGE * page
    bookmark_count = idB.execute_query("""SELECT count(bookmark_id) FROM sm_bookmarks;""")
    
    more_bookmarks=False
    if bookmark_count > (offset+BOOKMARKS_PER_PAGE):
        more_bookmarks = True

    
    query = """SELECT url, title, b.bookmark_id, project_name, p.project_id 
               FROM sm_bookmarks b 
               LEFT JOIN sm_project_bookmarks pb ON pb.bookmark_id=b.bookmark_id
               LEFT JOIN sm_projects p ON p.project_id=pb.project_id
               ORDER BY timestamp DESC
               LIMIT %s OFFSET %s;"""
    
    results = idB.execute_query(query, (BOOKMARKS_PER_PAGE, offset))
    
    return results, more_bookmarks
    
    
def get_project_bookmarks(project):
    query = """SELECT url, title, b.bookmark_id
               FROM sm_bookmarks b 
               JOIN sm_project_bookmarks pb ON pb.bookmark_id=b.bookmark_id 
               WHERE pb.project_id=%s
               ORDER BY timestamp DESC;"""
               
    results = idB.execute_query(query, (project,))
    
    query = """SELECT project_name FROM sm_projects WHERE project_id=%s;"""
    project_name = idB.execute_query(query, (project,))
        
    return results, project_name
    
    
def get_projects():
    query = """SELECT p.project_id, project_name, 
               (SELECT count(bookmark_id) 
                FROM sm_project_bookmarks b 
                WHERE b.project_id=p.project_id) as bookmark_count 
               FROM sm_projects p 
               ORDER BY project_name;"""
               
    results = idB.execute_query(query)
    
    return results
    
    
def get_project_id(project_name):
    query = """SELECT project_id FROM sm_projects WHERE project_name=%s;"""
    project_id = idB.execute_query(query, (project_name,))
    return project_id
    
    
def create_project(project):
    query = """INSERT INTO sm_projects (project_name) VALUES (%s) RETURNING project_id;"""
    project_id = idB.execute_query(query, (project,))
    
    return project_id
    
    
def search_for_bookmarks(terms):
    query = """SELECT url, title, b.bookmark_id, project_name, p.project_id 
               FROM sm_bookmarks b 
               LEFT JOIN sm_project_bookmarks pb ON pb.bookmark_id=b.bookmark_id
               LEFT JOIN sm_projects p ON p.project_id=pb.project_id
               WHERE to_tsvector('english', title) @@ plainto_tsquery('english', %s)
               ORDER BY timestamp DESC;"""
               
    bookmarks = idB.execute_query(query, (terms,))
    return bookmarks